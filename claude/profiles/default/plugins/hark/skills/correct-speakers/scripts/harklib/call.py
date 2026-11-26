"""One conversation: its files, its people, and Hark's rebuild of it."""

import hashlib
from pathlib import Path
from typing import Any, cast

from . import regroup, store


class NothingToRegroupError(LookupError):
    def __init__(self, name: str) -> None:
        super().__init__(
            f"{name} has no system words or no diarized segments to regroup"
        )


class Call:
    def __init__(self, name: str) -> None:
        self.name = name
        self.folder = store.CONVERSATIONS / name
        self.conversation = self.read("conversation")
        self.recognition = self.read("recognition")
        self.diarization = self.read("diarization")
        self.people: dict[str, str] = {
            person["id"]: person["name"] for person in store.people()
        }
        self.microphone = next(
            (
                voice["id"]
                for voice in self.conversation["voices"]
                if voice["track"] == "microphone"
            ),
            None,
        )
        self.grouping = regroup.Grouping(
            self.recognition, self.diarization, self.microphone
        )
        self.labels = {
            voice: entry["label"]
            for voice, entry in self.conversation["speech"].items()
        }
        self._chunks: dict[str, Any] | None = None

    def path(self, layer: str) -> Path:
        return store.path_of(self.folder, layer)

    def has(self, layer: str) -> bool:
        return self.path(layer).exists()

    def read(self, layer: str) -> dict[str, Any]:
        return store.read(self.path(layer), layer)

    @property
    def chunks(self) -> dict[str, Any]:
        if self._chunks is None:
            self._chunks = self.read("chunks")
        return self._chunks

    @property
    def audio(self) -> Path:
        return self.folder / "system.m4a"

    @property
    def recognizer(self) -> str:
        return str(self.recognition["engine"]["name"])

    def rebuilt(self, conversation: dict[str, Any] | None = None) -> regroup.Transcript:
        """The transcript Hark derives from a conversation record, default this one."""
        conversation = conversation or self.conversation
        transcript = regroup.regrouped(
            self.grouping, conversation["speech"], conversation["corrections"]
        )
        if transcript is None:
            raise NothingToRegroupError(self.name)
        return transcript

    def speaker(
        self, voice: str | None, attributions: dict[str, str] | None = None
    ) -> str:
        """A voice as Hark's inspector names it, with any label the diarizer gave it."""
        if voice is None or voice == self.microphone:
            return "Me"
        if attributions is None:
            attributions = cast("dict[str, str]", self.conversation["attributions"])
        person_id = attributions.get(voice)
        person = None if person_id is None else self.people.get(person_id)
        label = self.labels.get(voice, "new")
        return person or f"Unnamed {label} {voice[:4]}"

    def state(self) -> str:
        """A digest of the files a plan uses, so a plan an edit outdated is refused."""
        digest = hashlib.sha256()
        for layer in ("conversation", "recognition", "diarization"):
            digest.update(self.path(layer).read_bytes())
        if store.PEOPLE_FILE.exists():
            digest.update(store.PEOPLE_FILE.read_bytes())
        return digest.hexdigest()

    @property
    def cache(self) -> Path:
        directory = store.CACHE / str(self.conversation["id"])
        directory.mkdir(parents=True, exist_ok=True)
        return directory


def clock(seconds: float) -> str:
    return f"{int(seconds) // 60}:{seconds % 60:04.1f}"
