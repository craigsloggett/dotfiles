"""Replay the library through the port and compare with what Hark itself wrote."""

from pathlib import Path
from typing import Any

from . import regroup, store


class Replay:
    def __init__(self, folder: str) -> None:
        self.folder = folder
        self.transcript: bool | None = None
        self.voices: bool | None = None
        self.voiceprints: bool | None = None
        self.skipped: str | None = None
        self.first_difference: str | None = None


def replay(folder: Path) -> Replay:
    """Replay one conversation: True, False, or None where Hark wrote nothing."""
    result = Replay(folder.name)
    needed = ("conversation", "recognition", "diarization", "transcript")
    missing = [layer for layer in needed if not store.path_of(folder, layer).exists()]
    if missing:
        result.skipped = "no " + ", ".join(missing)
        return result
    conversation = store.read(store.path_of(folder, "conversation"), "conversation")
    recognition = store.read(store.path_of(folder, "recognition"), "recognition")
    diarization = store.read(store.path_of(folder, "diarization"), "diarization")
    written = store.read(store.path_of(folder, "transcript"), "transcript")["turns"]
    microphone = next(
        (
            voice["id"]
            for voice in conversation["voices"]
            if voice["track"] == "microphone"
        ),
        None,
    )
    grouping = regroup.Grouping(recognition, diarization, microphone)
    transcript = regroup.regrouped(
        grouping, conversation["speech"], conversation["corrections"]
    )
    if transcript is None:
        result.skipped = "no system words or segments"
        return result
    result.transcript = transcript.records() == written
    result.voices = transcript.voices == [
        voice["id"] for voice in conversation["voices"]
    ]
    if not result.transcript:
        result.first_difference = first_difference(transcript.records(), written)
    voiceprints = store.path_of(folder, "voiceprints")
    if store.path_of(folder, "chunks").exists() and voiceprints.exists():
        chunks = store.read(store.path_of(folder, "chunks"), "chunks")
        system = [
            voice
            for voice in transcript.voices
            if voice is not None and voice != microphone
        ]
        expected = regroup.voiceprints(chunks, transcript, system)
        result.voiceprints = voiceprints.read_text(encoding="utf-8") == store.text_of(
            "voiceprints", expected
        )
    return result


def first_difference(
    ported: list[dict[str, Any]], written: list[dict[str, Any]]
) -> str:
    for index, (mine, theirs) in enumerate(zip(ported, written, strict=False)):
        if mine != theirs:
            sides = (
                f"{name} {turn['span']} {turn['voiceID'][:8]} {turn['text'][:50]!r}"
                for name, turn in (("port", mine), ("Hark", theirs))
            )
            return f"turn {index}: " + " / ".join(sides)
    return f"turn counts differ: port {len(ported)} / Hark {len(written)}"
