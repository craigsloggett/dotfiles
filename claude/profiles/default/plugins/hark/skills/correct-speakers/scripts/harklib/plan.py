"""From intended speakers to the corrections that make Hark's rebuild produce them."""

import copy
import json
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

from . import regroup, store
from .call import clock

if TYPE_CHECKING:
    from .call import Call


class PlanError(Exception):
    pass


class UnknownPersonError(PlanError):
    def __init__(self, name: str) -> None:
        super().__init__(
            f"No person is named {name!r}. Confirm the spelling with the user, "
            "then list it under add_people."
        )


class UnknownVoiceError(PlanError):
    def __init__(self, speaker: str) -> None:
        super().__init__(
            f"{speaker!r} is not a label (S1, S2, …) or a voice id of this conversation"
        )


class UnknownSpeakerError(PlanError):
    def __init__(self, speaker: str) -> None:
        super().__init__(
            f"{speaker!r} is not a label, a voice id, new:<tag>, "
            "or a known person's name"
        )


class AmbiguousSpeakerError(PlanError):
    def __init__(self, speaker: str, count: int) -> None:
        super().__init__(
            f"{speaker} has {count} voices here; name the one you mean by its label"
        )


class UnknownKeepError(PlanError):
    def __init__(self, unknown: str) -> None:
        super().__init__(f"keep names {unknown}, which is not a line of the evidence")


class UnknownLinesError(PlanError):
    def __init__(self, missing: list[str]) -> None:
        super().__init__(f"moves names {missing}, not lines of the evidence")


class EmptyMoveError(PlanError):
    def __init__(self, move: dict[str, Any]) -> None:
        super().__init__(f"A move holds no words: {move}")


class InseparableWordsError(PlanError):
    def __init__(self, start: float) -> None:
        super().__init__(
            f"Two words start together at {clock(start)}; no span separates them"
        )


class UnsettledError(PlanError):
    def __init__(self) -> None:
        super().__init__(
            "The corrections did not settle; "
            "this is a bug in the plan, not in the conversation"
        )


class RebuildMismatchError(PlanError):
    def __init__(self) -> None:
        super().__init__("The rebuild does not match the intended speakers")


class StaleEvidenceError(PlanError):
    def __init__(self) -> None:
        super().__init__(
            "The conversation changed since the evidence was gathered; "
            "run evidence again"
        )


def minted() -> str:
    return str(uuid.uuid4()).upper()


class Plan:
    def __init__(
        self, call: Call, evidence: dict[str, Any], overrides: dict[str, Any]
    ) -> None:
        self.call = call
        self.evidence = evidence
        self.overrides = overrides
        self.before = call.rebuilt()
        self.people: dict[str, str] = dict(call.people)
        self.added_people: list[dict[str, str]] = []
        self.attributions: dict[str, str] = dict(call.conversation["attributions"])
        self.new_voices: dict[str, str] = {}
        self.guesses: list[tuple[dict[str, Any], str, str]] = []
        self.intended: dict[int, str] = {}
        self.added: list[dict[str, Any]] = []
        self._name()
        self._intend()
        self._correct()

    # Who is who

    def person_named(self, name: str) -> str | None:
        matches = [
            person
            for person, known in self.people.items()
            if known.casefold() == name.casefold()
        ]
        return matches[0] if matches else None

    def _name(self) -> None:
        for name in self.overrides.get("add_people", []):
            if self.person_named(name) is None:
                person = minted()
                self.people[person] = name
                self.added_people.append({"id": person, "name": name})
        suggested = self.evidence.get("suggested", {})
        names: dict[str, str | None] = {
            voice: self.people[person] for voice, person in suggested.items()
        }
        for speaker, name in self.overrides.get("name", {}).items():
            names[self._existing_voice(speaker)] = name
        for voice, name in names.items():
            if name is None:
                continue
            person = self.person_named(name)
            if person is None:
                raise UnknownPersonError(name)
            self.attributions[voice] = person

    def _existing_voice(self, speaker: str) -> str:
        labelled: list[str] = [
            voice for voice, label in self.call.labels.items() if label == speaker
        ]
        if labelled:
            return labelled[0]
        voices = set(self.before.voices) | set(self.call.labels)
        prefixed: list[str] = [
            voice
            for voice in voices
            if voice is not None
            and len(speaker) >= 4
            and voice.startswith(speaker.upper())
        ]
        if len(prefixed) == 1:
            return prefixed[0]
        raise UnknownVoiceError(speaker)

    def _voice_of(self, state: str) -> str:
        """The voice a speaker's words go to, minting one for a voiceless speaker."""
        kind, _, key = state.partition(":")
        if kind == "voice":
            return key
        if kind == "person":
            speaking = [
                voice
                for voice in self.before.voices
                if self.attributions.get(voice) == key
            ]
            if len(speaking) == 1 and speaking[0] is not None:
                return speaking[0]
        if state not in self.new_voices:
            self.new_voices[state] = minted()
            if kind == "person":
                self.attributions[self.new_voices[state]] = key
        return self.new_voices[state]

    def _state_of(self, speaker: str) -> str:
        if speaker.startswith("new:"):
            return speaker
        try:
            return "voice:" + self._existing_voice(speaker)
        except PlanError:
            pass
        person = self.person_named(speaker)
        if person is None:
            raise UnknownSpeakerError(speaker)
        speaking = [
            voice
            for voice in self.before.voices
            if self.attributions.get(voice) == person
        ]
        if len(speaking) > 1:
            raise AmbiguousSpeakerError(speaker, len(speaking))
        return f"voice:{speaking[0]}" if speaking else f"person:{person}"

    # What should be

    def _intend(self) -> None:
        owners = self.before.owners
        states = {index: f"voice:{voice}" for index, voice in owners.items()}
        lines = {line["id"]: line for line in self.evidence.get("lines", [])}
        kept = set(self.overrides.get("keep", []))
        for unknown in kept - set(lines):
            raise UnknownKeepError(unknown)
        for line in lines.values():
            proposal = line["proposal"]
            if proposal is None or line["id"] in kept:
                continue
            for index in line["words"]:
                states[index] = proposal["to"]
            if proposal["confidence"] != "high":
                self.guesses.append((line, proposal["confidence"], proposal["basis"]))
        words = {word.index: word for word in self.call.grouping.system_words}
        for move in self.overrides.get("moves", []):
            state = self._state_of(move["speaker"])
            for index in self._moved_indexes(move, lines, words, owners):
                states[index] = state
        self.intended = {
            index: self._voice_of(state) for index, state in states.items()
        }

    @staticmethod
    def _moved_indexes(
        move: dict[str, Any],
        lines: dict[str, dict[str, Any]],
        words: dict[int, regroup.Word],
        owners: dict[int, str],
    ) -> list[int]:
        if "lines" in move:
            missing = [name for name in move["lines"] if name not in lines]
            if missing:
                raise UnknownLinesError(missing)
            indexes: list[int] = [
                index for name in move["lines"] for index in lines[name]["words"]
            ]
        else:
            indexes = [
                index
                for index, word in words.items()
                if move["from"] <= word.start < move["to"]
            ]
        indexes = [index for index in indexes if index in owners]
        if not indexes:
            raise EmptyMoveError(move)
        return indexes

    # What makes it so

    def _correct(self) -> None:
        """Append reassignments until Hark's rebuild gives every word its voice.

        A reassigned word is pinned, and pinning changes which stranded words
        Hark carries over to the next speaker, so each pass can unsettle a
        neighbour; pin those too until nothing moves.
        """
        call = self.call
        self.conversation = copy.deepcopy(call.conversation)
        self.conversation["attributions"] = self.attributions
        # Every system word in start order. One a discard already removed has no
        # intended speaker, and a reassignment reaching over it would bring it
        # back, so it ends any run it sits in.
        order = [word for word, _ in call.grouping.placements]
        self.added = []
        for _ in range(50):
            owners = call.rebuilt(self.conversation).owners
            wrong = [
                position
                for position, word in enumerate(order)
                if word.index in self.intended
                and owners.get(word.index) != self.intended[word.index]
            ]
            if not wrong:
                break
            for run in self._runs(order, wrong):
                correction = self._reassignment(order, run)
                self.conversation["corrections"].append(correction)
                self.added.append(correction)
        else:
            raise UnsettledError
        self.after = call.rebuilt(self.conversation)
        if self.after.owners != {
            index: self.intended[index] for index in self.after.owners
        }:
            raise RebuildMismatchError
        self.conversation["voices"] = [
            {
                "id": voice,
                "track": "microphone" if voice == call.microphone else "system",
            }
            for voice in self.after.voices
        ]

    def _runs(self, order: list[regroup.Word], wrong: list[int]) -> list[list[int]]:
        runs: list[list[int]] = []
        for position in wrong:
            voice = self.intended[order[position].index]
            if (
                runs
                and runs[-1][-1] == position - 1
                and self.intended.get(order[position - 1].index) == voice
            ):
                runs[-1].append(position)
            else:
                runs.append([position])
        return runs

    def _reassignment(
        self, order: list[regroup.Word], run: list[int]
    ) -> dict[str, Any]:
        first, last = order[run[0]], order[run[-1]]
        end = last.end
        if run[-1] + 1 < len(order):
            end = min(end, order[run[-1] + 1].start)
        if (run[0] > 0 and order[run[0] - 1].start >= first.start) or end <= last.start:
            raise InseparableWordsError(first.start)
        return {
            "correction": {
                "reassign": {
                    "span": [first.start, end],
                    "voice": {
                        "id": self.intended[first.index],
                        "track": "system",
                    },
                }
            },
            "recognizer": self.call.recognizer,
        }

    # What it means

    @property
    def is_empty(self) -> bool:
        return (
            not self.added
            and self.attributions == self.call.conversation["attributions"]
        )

    def speaker(self, voice: str) -> str:
        if voice == self.call.microphone:
            return "Me"
        person = self.people.get(self.attributions.get(voice))
        if person is not None and person != "":
            return person
        tag = next(
            (
                state
                for state, minted_voice in self.new_voices.items()
                if minted_voice == voice
            ),
            None,
        )
        return f"Unnamed {tag or self.call.labels.get(voice, '')} {voice[:4]}".replace(
            "  ", " "
        )

    def moved_words(self) -> int:
        before = self.before.owners
        return sum(
            1 for index, voice in self.intended.items() if before.get(index) != voice
        )

    def changed_turns(self) -> list[str]:
        old = {
            (turn.start, turn.end, turn.voice, turn.text) for turn in self.before.turns
        }
        before = self.before.owners
        rows = []
        for turn in self.after.turns:
            if (
                turn.voice is None
                or turn.voice == self.call.microphone
                or (turn.start, turn.end, turn.voice, turn.text) in old
            ):
                continue
            was = {before.get(word.index) for word in turn.words} - {turn.voice}
            note = ""
            if was:
                note = (
                    " (was "
                    + ", ".join(
                        sorted(
                            self.call.speaker(voice)
                            for voice in was
                            if voice is not None
                        )
                    )
                    + ")"
                )
            speaker = self.speaker(turn.voice)
            rows.append(f"  {clock(turn.start):>7}  {speaker}{note}: {turn.text}")
        return rows

    def voiceprint_notes(self) -> list[str]:
        """Which speakers get a voiceprint, and which Hark trusts as exemplars."""
        system = [
            voice
            for voice in self.after.voices
            if voice is not None and voice != self.call.microphone
        ]
        prints = regroup.voiceprints(self.call.chunks, self.after, system)["byVoice"]
        rows = []
        for voice in system:
            spans = self.after.spans(voice)
            speech = sum(end - start for start, end in spans)
            stretch = regroup.longest_stretch(spans)
            if voice not in prints:
                standing = "no voiceprint (no chunk heard 3s of it)"
            elif (
                speech >= regroup.MINIMUM_EXEMPLAR_SPEECH
                and stretch >= regroup.MINIMUM_EXEMPLAR_STRETCH
            ):
                standing = "voiceprint, trusted to suggest this person elsewhere"
            else:
                standing = "voiceprint, too little speech to suggest anyone"
            rows.append(f"  {self.speaker(voice):<28} {speech:6.0f}s  {standing}")
        return rows

    def _speaker_changes(self) -> list[str]:
        call = self.call
        was_named = call.conversation["attributions"]
        named = {
            voice: person
            for voice, person in self.attributions.items()
            if was_named.get(voice) != person
        }
        out = [
            f"  Name {call.speaker(voice)} as {self.people[person]}"
            for voice, person in named.items()
            if voice not in self.new_voices.values()
        ]
        out.extend(
            f"  New voice for {self.speaker(voice)}"
            for voice in self.new_voices.values()
        )
        out.extend(f"  Add {person['name']} to people" for person in self.added_people)
        gone = [
            voice
            for voice in self.before.voices
            if voice is not None and voice not in self.after.voices
        ]
        out.extend(
            f"  {call.speaker(voice)} is left with no turns and disappears"
            for voice in gone
        )
        return out

    def _guess_notes(self) -> list[str]:
        out = [
            "",
            (
                f"Accepted on weaker evidence ({len(self.guesses)}); "
                "tell the user these are guesses"
            ),
        ]
        for line, confidence, basis in self.guesses[:60]:
            speaker = self.speaker(self.intended[line["words"][0]])
            moment = clock(line["start"])
            what = f"{line['id']:<5} {moment:>7}  -> {speaker}: {line['text'][:80]}"
            out.append(f"  {confidence:<6} {basis:<9} {what}")
        if len(self.guesses) > 60:
            out.append(f"  … and {len(self.guesses) - 60} more")
        return out

    def summary(self) -> str:
        out = [f"Plan for {self.call.name}"]
        if self.is_empty:
            return out[0] + "\n  Nothing to change."
        out += self._speaker_changes()
        out.append(
            f"  {len(self.added)} corrections move {self.moved_words()} "
            f"of {len(self.intended)} system words; "
            f"{len(self.before.turns)} turns become {len(self.after.turns)}"
        )
        rows = self.changed_turns()
        out += ["", f"Turns that change ({len(rows)})", *rows[:80]]
        if len(rows) > 80:
            changes = self.directory / "changes.txt"
            out.append(f"  … and {len(rows) - 80} more, in {changes}")
        if self.guesses:
            out += self._guess_notes()
        out += ["", "Voiceprints Hark will derive", *self.voiceprint_notes()]
        out += [
            "",
            (
                "Verified: Hark's rebuild of these corrections gives every word "
                "its intended speaker."
            ),
        ]
        return "\n".join(out)

    # Where it is kept

    @property
    def directory(self) -> Path:
        return Path(self.call.cache) / "plan"

    def save(self) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        store.write(
            self.directory / "conversation.jsonl",
            "conversation",
            self.conversation,
        )
        store.write(
            self.directory / "transcript.jsonl",
            "transcript",
            {"turns": self.after.records()},
        )
        with (self.directory / "changes.txt").open("w", encoding="utf-8") as handle:
            handle.write("\n".join(self.changed_turns()) + "\n")
        with (self.directory / "plan.json").open("w", encoding="utf-8") as handle:
            json.dump(
                {
                    "folder": self.call.name,
                    "state": self.call.state(),
                    "addedPeople": self.added_people,
                    "corrections": len(self.added),
                    "empty": self.is_empty,
                },
                handle,
            )


def load_evidence(call: Call) -> dict[str, Any]:
    file = Path(call.cache) / "evidence.json"
    if not file.exists():
        return {}
    with file.open(encoding="utf-8") as handle:
        record = json.load(handle)
    if record["state"] != call.state():
        raise StaleEvidenceError
    return record
