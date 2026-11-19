"""Replay the library through the port and compare with what Hark itself wrote."""

import os

from . import regroup, store


class Replay:
    def __init__(self, folder):
        self.folder = folder
        self.transcript = None
        self.voices = None
        self.voiceprints = None
        self.skipped = None


def replay(folder):
    """One conversation's files against the port: True, False, or None where Hark wrote nothing."""
    result = Replay(os.path.basename(folder))
    needed = ("conversation", "recognition", "diarization", "transcript")
    missing = [layer for layer in needed if not os.path.exists(store.path_of(folder, layer))]
    if missing:
        result.skipped = "no " + ", ".join(missing)
        return result
    conversation = store.read(store.path_of(folder, "conversation"), "conversation")
    recognition = store.read(store.path_of(folder, "recognition"), "recognition")
    diarization = store.read(store.path_of(folder, "diarization"), "diarization")
    written = store.read(store.path_of(folder, "transcript"), "transcript")["turns"]
    microphone = next((voice["id"] for voice in conversation["voices"] if voice["track"] == "microphone"), None)
    grouping = regroup.Grouping(recognition, diarization, microphone)
    transcript = regroup.regrouped(grouping, conversation["speech"], conversation["corrections"])
    if transcript is None:
        result.skipped = "no system words or segments"
        return result
    result.transcript = transcript.records() == written
    result.voices = transcript.voices == [voice["id"] for voice in conversation["voices"]]
    result.first_difference = None
    if not result.transcript:
        result.first_difference = first_difference(transcript.records(), written)
    if os.path.exists(store.path_of(folder, "chunks")) and os.path.exists(store.path_of(folder, "voiceprints")):
        chunks = store.read(store.path_of(folder, "chunks"), "chunks")
        system = [voice for voice in transcript.voices if voice != microphone]
        expected = regroup.voiceprints(chunks, transcript, system)
        with open(store.path_of(folder, "voiceprints"), encoding="utf-8") as handle:
            result.voiceprints = handle.read() == store.text_of("voiceprints", expected)
    return result


def first_difference(ported, written):
    for index, (mine, theirs) in enumerate(zip(ported, written)):
        if mine != theirs:
            sides = (
                f"{name} {turn['span']} {turn['voiceID'][:8]} {turn['text'][:50]!r}"
                for name, turn in (("port", mine), ("Hark", theirs))
            )
            return f"turn {index}: " + " / ".join(sides)
    return f"turn counts differ: port {len(ported)} / Hark {len(written)}"
