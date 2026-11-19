"""One conversation: its files, its people, and Hark's rebuild of it."""

import hashlib
import os

from . import regroup, store


class Call:
    def __init__(self, name):
        self.name = name
        self.folder = os.path.join(store.CONVERSATIONS, name)
        self.conversation = self.read("conversation")
        self.recognition = self.read("recognition")
        self.diarization = self.read("diarization")
        self.people = {person["id"]: person["name"] for person in store.people()}
        self.microphone = next(
            (voice["id"] for voice in self.conversation["voices"] if voice["track"] == "microphone"), None
        )
        self.grouping = regroup.Grouping(self.recognition, self.diarization, self.microphone)
        self.labels = {voice: entry["label"] for voice, entry in self.conversation["speech"].items()}
        self._chunks = None

    def path(self, layer):
        return store.path_of(self.folder, layer)

    def has(self, layer):
        return os.path.exists(self.path(layer))

    def read(self, layer):
        return store.read(self.path(layer), layer)

    @property
    def chunks(self):
        if self._chunks is None:
            self._chunks = self.read("chunks")
        return self._chunks

    @property
    def audio(self):
        return os.path.join(self.folder, "system.m4a")

    @property
    def recognizer(self):
        return self.recognition["engine"]["name"]

    def rebuilt(self, conversation=None):
        """The transcript Hark derives from a conversation record, this one's unless another is given."""
        conversation = conversation or self.conversation
        transcript = regroup.regrouped(self.grouping, conversation["speech"], conversation["corrections"])
        if transcript is None:
            raise LookupError(f"{self.name} has no system words or no diarized segments to regroup")
        return transcript

    def speaker(self, voice, attributions=None):
        """A voice as Hark's inspector names it, with the diarizer's label when it has one."""
        if voice == self.microphone:
            return "Me"
        attributions = self.conversation["attributions"] if attributions is None else attributions
        person = self.people.get(attributions.get(voice))
        label = self.labels.get(voice, "new")
        return person or f"Unnamed {label} {voice[:4]}"

    def state(self):
        """A digest of every file a plan depends on, so a plan made before an in-app edit is refused."""
        digest = hashlib.sha256()
        for layer in ("conversation", "recognition", "diarization"):
            with open(self.path(layer), "rb") as handle:
                digest.update(handle.read())
        if os.path.exists(store.PEOPLE_FILE):
            with open(store.PEOPLE_FILE, "rb") as handle:
                digest.update(handle.read())
        return digest.hexdigest()

    @property
    def cache(self):
        directory = os.path.join(store.CACHE, self.conversation["id"])
        os.makedirs(directory, exist_ok=True)
        return directory


def clock(seconds):
    return f"{int(seconds) // 60}:{seconds % 60:04.1f}"
