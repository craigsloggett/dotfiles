"""From intended speakers to the corrections that make Hark's own rebuild produce them."""

import copy
import json
import os
import uuid

from . import regroup, store
from .call import clock


class PlanError(Exception):
    pass


def minted():
    return str(uuid.uuid4()).upper()


class Plan:
    def __init__(self, call, evidence, overrides):
        self.call = call
        self.evidence = evidence
        self.overrides = overrides
        self.before = call.rebuilt()
        self.people = dict(call.people)
        self.added_people = []
        self.attributions = dict(call.conversation["attributions"])
        self.new_voices = {}
        self.guesses = []
        self._name()
        self._intend()
        self._correct()

    # Who is who

    def person_named(self, name):
        matches = [person for person, known in self.people.items() if known.casefold() == name.casefold()]
        return matches[0] if matches else None

    def _name(self):
        for name in self.overrides.get("add_people", []):
            if self.person_named(name) is None:
                person = minted()
                self.people[person] = name
                self.added_people.append({"id": person, "name": name})
        names = dict(self.evidence.get("suggested", {}))
        names = {voice: self.people[person] for voice, person in names.items()}
        for speaker, name in self.overrides.get("name", {}).items():
            names[self._existing_voice(speaker)] = name
        for voice, name in names.items():
            if name is None:
                continue
            person = self.person_named(name)
            if person is None:
                raise PlanError(
                    f"No person is named {name!r}. Confirm the spelling with the user, then list it under add_people."
                )
            self.attributions[voice] = person

    def _existing_voice(self, speaker):
        labelled = [voice for voice, label in self.call.labels.items() if label == speaker]
        if labelled:
            return labelled[0]
        voices = set(self.before.voices) | set(self.call.labels)
        prefixed = [voice for voice in voices if len(speaker) >= 4 and voice.startswith(speaker.upper())]
        if len(prefixed) == 1:
            return prefixed[0]
        raise PlanError(f"{speaker!r} is not a label (S1, S2, …) or a voice id of this conversation")

    def _voice_of(self, state):
        """The voice a speaker's words go to, minting one for a speaker with none here."""
        kind, _, key = state.partition(":")
        if kind == "voice":
            return key
        if kind == "person":
            speaking = [voice for voice in self.before.voices if self.attributions.get(voice) == key]
            if len(speaking) == 1:
                return speaking[0]
        if state not in self.new_voices:
            self.new_voices[state] = minted()
            if kind == "person":
                self.attributions[self.new_voices[state]] = key
        return self.new_voices[state]

    def _state_of(self, speaker):
        if speaker.startswith("new:"):
            return speaker
        try:
            return "voice:" + self._existing_voice(speaker)
        except PlanError:
            pass
        person = self.person_named(speaker)
        if person is None:
            raise PlanError(f"{speaker!r} is not a label, a voice id, new:<tag>, or a known person's name")
        speaking = [voice for voice in self.before.voices if self.attributions.get(voice) == person]
        if len(speaking) > 1:
            raise PlanError(f"{speaker} has {len(speaking)} voices here; name the one you mean by its label")
        return f"voice:{speaking[0]}" if speaking else f"person:{person}"

    # What should be

    def _intend(self):
        owners = self.before.owners
        states = {index: f"voice:{voice}" for index, voice in owners.items()}
        lines = {line["id"]: line for line in self.evidence.get("lines", [])}
        kept = set(self.overrides.get("keep", []))
        for unknown in kept - set(lines):
            raise PlanError(f"keep names {unknown}, which is not a line of the evidence")
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
            if "lines" in move:
                missing = [name for name in move["lines"] if name not in lines]
                if missing:
                    raise PlanError(f"moves names {missing}, not lines of the evidence")
                indexes = [index for name in move["lines"] for index in lines[name]["words"]]
            else:
                indexes = [index for index, word in words.items() if move["from"] <= word.start < move["to"]]
            indexes = [index for index in indexes if index in owners]
            if not indexes:
                raise PlanError(f"A move holds no words: {move}")
            for index in indexes:
                states[index] = state
        self.intended = {index: self._voice_of(state) for index, state in states.items()}

    # What makes it so

    def _correct(self):
        """Append reassignments until Hark's rebuild gives every word its intended voice.

        A reassigned word is pinned, and pinning changes which stranded words Hark carries over to
        the next speaker, so each pass can unsettle a neighbour; pin those too until nothing moves.
        """
        call = self.call
        self.conversation = copy.deepcopy(call.conversation)
        self.conversation["attributions"] = self.attributions
        # Every system word in start order. One a discard already removed has no intended speaker, and
        # a reassignment reaching over it would bring it back, so it ends any run it sits in.
        order = [word for word, _ in call.grouping.placements]
        self.added = []
        for _ in range(50):
            owners = call.rebuilt(self.conversation).owners
            wrong = [
                position
                for position, word in enumerate(order)
                if word.index in self.intended and owners.get(word.index) != self.intended[word.index]
            ]
            if not wrong:
                break
            runs = []
            for position in wrong:
                voice = self.intended[order[position].index]
                if runs and runs[-1][-1] == position - 1 and self.intended.get(order[position - 1].index) == voice:
                    runs[-1].append(position)
                else:
                    runs.append([position])
            for run in runs:
                first, last = order[run[0]], order[run[-1]]
                end = last.end
                if run[-1] + 1 < len(order):
                    end = min(end, order[run[-1] + 1].start)
                if run[0] > 0 and order[run[0] - 1].start >= first.start or end <= last.start:
                    raise PlanError(f"Two words start together at {clock(first.start)}; no span separates them")
                correction = {
                    "correction": {
                        "reassign": {
                            "span": [first.start, end],
                            "voice": {"id": self.intended[first.index], "track": "system"},
                        }
                    },
                    "recognizer": call.recognizer,
                }
                self.conversation["corrections"].append(correction)
                self.added.append(correction)
        else:
            raise PlanError("The corrections did not settle; this is a bug in the plan, not in the conversation")
        self.after = call.rebuilt(self.conversation)
        if self.after.owners != {index: self.intended[index] for index in self.after.owners}:
            raise PlanError("The rebuild does not match the intended speakers")
        self.conversation["voices"] = [
            {"id": voice, "track": "microphone" if voice == call.microphone else "system"}
            for voice in self.after.voices
        ]

    # What it means

    @property
    def is_empty(self):
        return not self.added and self.attributions == self.call.conversation["attributions"]

    def speaker(self, voice):
        if voice == self.call.microphone:
            return "Me"
        person = self.people.get(self.attributions.get(voice))
        if person:
            return person
        tag = next((state for state, minted_voice in self.new_voices.items() if minted_voice == voice), None)
        return f"Unnamed {tag or self.call.labels.get(voice, '')} {voice[:4]}".replace("  ", " ")

    def moved_words(self):
        before = self.before.owners
        return sum(1 for index, voice in self.intended.items() if before.get(index) != voice)

    def changed_turns(self):
        old = {(turn.start, turn.end, turn.voice, turn.text) for turn in self.before.turns}
        before = self.before.owners
        rows = []
        for turn in self.after.turns:
            if turn.voice == self.call.microphone or (turn.start, turn.end, turn.voice, turn.text) in old:
                continue
            was = {before.get(word.index) for word in turn.words} - {turn.voice}
            note = ""
            if was:
                note = " (was " + ", ".join(sorted(self.call.speaker(voice) for voice in was if voice)) + ")"
            rows.append(f"  {clock(turn.start):>7}  {self.speaker(turn.voice)}{note}: {turn.text}")
        return rows

    def voiceprint_notes(self):
        """Which speakers Hark will hold a voiceprint for, and which of those it will trust as exemplars."""
        system = [voice for voice in self.after.voices if voice != self.call.microphone]
        prints = regroup.voiceprints(self.call.chunks, self.after, system)["byVoice"]
        rows = []
        for voice in system:
            spans = self.after.spans(voice)
            speech = sum(end - start for start, end in spans)
            stretch = regroup.longest_stretch(spans)
            if voice not in prints:
                standing = "no voiceprint (no chunk heard 3s of it)"
            elif speech >= regroup.MINIMUM_EXEMPLAR_SPEECH and stretch >= regroup.MINIMUM_EXEMPLAR_STRETCH:
                standing = "voiceprint, trusted to suggest this person elsewhere"
            else:
                standing = "voiceprint, too little speech to suggest anyone"
            rows.append(f"  {self.speaker(voice):<28} {speech:6.0f}s  {standing}")
        return rows

    def summary(self):
        call = self.call
        out = [f"Plan for {call.name}"]
        if self.is_empty:
            return out[0] + "\n  Nothing to change."
        was_named = call.conversation["attributions"]
        named = {voice: person for voice, person in self.attributions.items() if was_named.get(voice) != person}
        for voice, person in named.items():
            if voice not in self.new_voices.values():
                out.append(f"  Name {call.speaker(voice)} as {self.people[person]}")
        for state, voice in self.new_voices.items():
            out.append(f"  New voice for {self.speaker(voice)}")
        for person in self.added_people:
            out.append(f"  Add {person['name']} to people")
        gone = [voice for voice in self.before.voices if voice not in self.after.voices]
        for voice in gone:
            out.append(f"  {call.speaker(voice)} is left with no turns and disappears")
        out.append(
            f"  {len(self.added)} corrections move {self.moved_words()} of {len(self.intended)} system words; "
            f"{len(self.before.turns)} turns become {len(self.after.turns)}"
        )
        rows = self.changed_turns()
        out += ["", f"Turns that change ({len(rows)})"] + rows[:80]
        if len(rows) > 80:
            out.append(f"  … and {len(rows) - 80} more, in {os.path.join(self.directory, 'changes.txt')}")
        if self.guesses:
            out += ["", f"Accepted on weaker evidence ({len(self.guesses)}); tell the user these are guesses"]
            for line, confidence, basis in self.guesses[:60]:
                speaker = self.speaker(self.intended[line["words"][0]])
                moment = clock(line["start"])
                what = f"{line['id']:<5} {moment:>7}  -> {speaker}: {line['text'][:80]}"
                out.append(f"  {confidence:<6} {basis:<9} {what}")
            if len(self.guesses) > 60:
                out.append(f"  … and {len(self.guesses) - 60} more")
        out += ["", "Voiceprints Hark will derive"] + self.voiceprint_notes()
        out += ["", "Verified: Hark's rebuild of these corrections gives every word its intended speaker."]
        return "\n".join(out)

    # Where it is kept

    @property
    def directory(self):
        return os.path.join(self.call.cache, "plan")

    def save(self):
        os.makedirs(self.directory, exist_ok=True)
        store.write(os.path.join(self.directory, "conversation.jsonl"), "conversation", self.conversation)
        store.write(os.path.join(self.directory, "transcript.jsonl"), "transcript", {"turns": self.after.records()})
        with open(os.path.join(self.directory, "changes.txt"), "w", encoding="utf-8") as handle:
            handle.write("\n".join(self.changed_turns()) + "\n")
        with open(os.path.join(self.directory, "plan.json"), "w", encoding="utf-8") as handle:
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


def load_evidence(call):
    file = os.path.join(call.cache, "evidence.json")
    if not os.path.exists(file):
        return {}
    with open(file, encoding="utf-8") as handle:
        record = json.load(handle)
    if record["state"] != call.state():
        raise PlanError("The conversation changed since the evidence was gathered; run evidence again")
    return record
