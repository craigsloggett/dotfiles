"""Who each line of system speech sounds like, and the moves that follow without judgment.

A line is a sentence-sized run of words in one voice. Each is embedded with Hark's own model and
scored against every speaker the conversation could hold: the voices already in it, and people
heard in other conversations. Rules that need no judgment turn the scores into proposals; the
lines no rule settles are listed for whoever is driving.
"""

import json
import os

from . import embed, regroup, store
from .call import clock
from .embed import dot, mean, unit

# A line shorter than this embeds too noisily to stand as evidence on its own.
EVIDENT_SPEECH = 0.8
LONG_SPEECH = 2.0
LINE_PAUSE = 0.6
LINE_LENGTH = 9.5

# Scores are cosine similarities. On the conversations these were tuned against, a person's
# clean lines scored 0.6 to 0.9 against their own voice and under 0.4 against anyone else's.
MATCH = 0.5
STRONG_MATCH = 0.55
CANDIDATE_MATCH = 0.6
NO_MATCH = 0.35
LEAD = 0.2
STRONG_LEAD = 0.3

# A voice is a merge of several people once this much of its long speech sounds like someone else.
SPLIT_SPEECH = 10.0
SPLIT_SHARE = 0.15
# How strongly a line's score pulls against the cost of changing speaker between lines; changing
# mid-sentence costs most, and across turns least. Carried over from the merges this was tuned on.
SEQUENCE_WEIGHT = 13.0
SEQUENCE_FULL_SPEECH = 1.5
CHANGE_MID_SENTENCE = 3.0
CHANGE_AFTER_SENTENCE = 1.5
CHANGE_ACROSS_TURNS = 1.0
CHANGE_AFTER_INTERJECTION = 0.5

CONTINUATION_GAP = 0.8
CHUNK_EDGE = 0.5
CHUNK_SLACK = 0.3
# The diarizer embeds ten-second windows two seconds apart, so a chunk edge on that grid is where
# the window stopped, not where the speaker did.
CHUNK_GRID = 2.0


class Line:
    def __init__(self, number, words, voice, turn):
        self.id = f"s{number}"
        self.words = words
        self.voice = voice
        self.turn = turn
        self.start = words[0].start
        self.end = words[-1].end
        self.speech = sum(word.end - word.start for word in words)
        self.text = " ".join(word.text for word in words)
        self.embedding = None
        self.scores = {}
        self.proposal = None

    @property
    def ends_sentence(self):
        return self.words[-1].ends_sentence

    def ranked(self, among=None):
        scores = self.scores if among is None else {key: self.scores[key] for key in among}
        return sorted(scores.items(), key=lambda item: -item[1])


class Proposal:
    def __init__(self, to, confidence, basis):
        self.to = to
        self.confidence = confidence
        self.basis = basis


def lines_of(transcript, microphone):
    lines = []
    for index, turn in enumerate(transcript.turns):
        if turn.voice == microphone:
            continue
        current = []
        for word in turn.words:
            pauses = current and word.start - current[-1].end >= LINE_PAUSE
            runs_long = current and word.end - current[0].start > LINE_LENGTH
            if pauses or runs_long:
                lines.append(Line(len(lines), current, turn.voice, index))
                current = []
            current.append(word)
            if word.ends_sentence:
                lines.append(Line(len(lines), current, turn.voice, index))
                current = []
        if current:
            lines.append(Line(len(lines), current, turn.voice, index))
    return lines


def exemplars(excluding):
    """Each person's voiceprints from other conversations, by the floor Hark's own suggester applies."""
    trusted = {}
    for name in store.folders():
        if name == excluding:
            continue
        folder = os.path.join(store.CONVERSATIONS, name)
        files = [store.path_of(folder, layer) for layer in ("conversation", "transcript", "voiceprints")]
        if not all(os.path.exists(file) for file in files):
            continue
        try:
            conversation = store.read(files[0], "conversation")
            turns = store.read(files[1], "transcript")["turns"]
            prints = store.read(files[2], "voiceprints")["byVoice"]
        except (store.SchemaMismatch, ValueError):
            continue
        if conversation.get("deletedAt") is not None:
            continue
        for voice, person in conversation["attributions"].items():
            if voice not in prints:
                continue
            spans = [tuple(turn["span"]) for turn in turns if turn["voiceID"] == voice]
            speech = sum(end - start for start, end in spans)
            if speech < regroup.MINIMUM_EXEMPLAR_SPEECH:
                continue
            if regroup.longest_stretch(spans) < regroup.MINIMUM_EXEMPLAR_STRETCH:
                continue
            trusted.setdefault(person, []).append(unit(prints[voice]))
    return trusted


class Evidence:
    def __init__(self, call):
        self.call = call
        self.transcript = call.rebuilt()
        self.lines = lines_of(self.transcript, call.microphone)
        self.voices = [voice for voice in self.transcript.voices if voice != call.microphone]
        self.attributions = call.conversation["attributions"]
        self.mic_starts = [turn.start for turn in self.transcript.turns if turn.voice == call.microphone]
        self._embed()
        self.people = {person: unit(mean(prints)) for person, prints in exemplars(call.name).items()}
        self._reference_voices()
        self._find_candidates()
        for _ in range(3):
            self._score()
            self._find_catch_all()
            for line in self.lines:
                line.proposal = None
                self._propose_by_voice(line)
            if not self._refine_references():
                break
        self._sequence()
        self._settle_suspects()

    # References

    def _embed(self):
        duration = self.call.conversation["duration"]
        requests = {line.id: embed.request_of(line.words, duration) for line in self.lines}
        vectors = embed.embeddings(self.call, requests)
        for line in self.lines:
            line.embedding = vectors[line.id]

    def _best_person(self, vector):
        ranked = sorted(((dot(vector, print_), person) for person, print_ in self.people.items()), reverse=True)
        if not ranked:
            return None, 0.0, 0.0
        runner_up = ranked[1][0] if len(ranked) > 1 else 0.0
        return ranked[0][1], ranked[0][0], ranked[0][0] - runner_up

    def _reference_voices(self):
        """Each voice's own sound: its long lines that match the person it mostly is, else all of them."""
        self.references = {}
        self.mostly = {}
        self.suggested = {}
        self.votes = {}
        for voice in self.voices:
            long = [line for line in self.lines if line.voice == voice and line.speech >= LONG_SPEECH]
            votes = {}
            for line in long:
                person, score, lead = self._best_person(line.embedding)
                if person is not None and score >= CANDIDATE_MATCH and lead >= 0.1:
                    votes.setdefault(person, []).append(line)
            self.votes[voice] = votes
            named = self.attributions.get(voice)
            person = named if named in self.people else None
            if person is None and votes:
                top = max(votes, key=lambda key: sum(line.speech for line in votes[key]))
                if sum(line.speech for line in votes[top]) >= 8.0:
                    person = top
                    if named is None:
                        self.suggested[voice] = top
            self.mostly[voice] = person
            if person is not None:
                own = [line.embedding for line in long if dot(line.embedding, self.people[person]) >= MATCH]
                self.references[voice] = unit(mean(own)) if len(own) >= 2 else self.people[person]
                continue
            kept = [line.embedding for line in long] or [
                line.embedding for line in self.lines if line.voice == voice
            ]
            for _ in range(2):
                centre = unit(mean(kept))
                close = [vector for vector in kept if dot(vector, centre) >= MATCH]
                if len(close) * 2 >= len(kept) and close:
                    kept = close
            self.references[voice] = unit(mean(kept))

    def _find_candidates(self):
        """People with no voice here whose sound some long lines carry more than their own voice's."""
        present = {self.mostly[voice] for voice in self.voices} | set(self.attributions.values())
        heard = {}
        for line in self.lines:
            if line.speech < LONG_SPEECH:
                continue
            person, score, lead = self._best_person(line.embedding)
            if person is None or person in present or score < CANDIDATE_MATCH or lead < 0.1:
                continue
            if score - dot(line.embedding, self.references[line.voice]) >= 0.15:
                heard.setdefault(person, []).append(line)
        self.candidates = {
            person: lines for person, lines in heard.items() if sum(line.speech for line in lines) >= 3.0
        }

    def _score(self):
        if not hasattr(self, "states"):
            self.states = {f"voice:{voice}": self.references[voice] for voice in self.voices}
            for person in self.candidates:
                self.states[f"person:{person}"] = self.people[person]
        for line in self.lines:
            line.scores = {state: dot(line.embedding, reference) for state, reference in self.states.items()}

    def _find_catch_all(self):
        """Speech cut off at a turn's edges or spoken over someone embeds to one point whoever said it.

        The diarizer often gathers it into a voice of its own. That voice is nobody, and no score
        against it means anything.
        """
        self.degraded_direction = None
        self.catch_all = set()
        evident = [line for line in self.lines if line.speech >= EVIDENT_SPEECH]
        for voice in self.voices:
            if voice in self.attributions:
                continue
            own = [line for line in self.lines if line.voice == voice]
            if not own or sorted(line.speech for line in own)[len(own) // 2] >= LONG_SPEECH:
                continue
            state = f"voice:{voice}"
            drawn = [
                line
                for line in evident
                if line.voice != voice
                and line.scores[state] >= 0.65
                and line.scores[f"voice:{line.voice}"] < NO_MATCH
            ]
            if len(drawn) >= 2:
                self.catch_all.add(voice)
        real = [state for state in self.states if state.removeprefix("voice:") not in self.catch_all]
        self.real_states = real
        lost = [line for line in evident if max(line.scores[state] for state in real) < NO_MATCH]
        if len(lost) >= 4:
            centre = unit(mean([line.embedding for line in lost]))
            close = [line.embedding for line in lost if dot(line.embedding, centre) >= CANDIDATE_MATCH]
            if len(close) >= 4:
                self.degraded_direction = unit(mean(close))

    def is_degraded(self, line):
        if line.speech < EVIDENT_SPEECH:
            return True
        best = max(line.scores[state] for state in self.real_states)
        if best < NO_MATCH:
            return True
        if self.degraded_direction is None:
            return False
        return dot(line.embedding, self.degraded_direction) >= CANDIDATE_MATCH and best < 0.45

    def is_suspect(self, line):
        """A line whose own voice it does not sound like, or one in a voice that is nobody's."""
        if line.voice in self.catch_all:
            return True
        return line.speech >= 0.4 and line.scores[f"voice:{line.voice}"] < NO_MATCH and self.is_degraded(line)

    # Proposals

    def resolved(self, line):
        return line.proposal.to if line.proposal else f"voice:{line.voice}"

    def _is_real(self, state):
        return state.removeprefix("voice:") not in self.catch_all

    def _refine_references(self):
        """Re-centre each speaker on the long lines that clearly are theirs in this conversation.

        A print from another conversation is a different room and microphone; a speaker's own lines
        here score higher against each other. Only long, clearly matched lines move a reference, so
        the speech that sounds like nobody cannot drift into whoever has the fewest lines.
        """
        changed = False
        for state in self.real_states:
            own = []
            for line in self.lines:
                if line.speech < LONG_SPEECH or self.is_degraded(line):
                    continue
                if line.proposal is not None:
                    is_own = line.proposal.to == state and line.proposal.confidence == "high"
                else:
                    best, score = line.ranked(self.real_states)[0]
                    is_own = f"voice:{line.voice}" == state and best == state and score >= MATCH
                if is_own:
                    own.append(line)
            if len(own) < 3 or sum(line.speech for line in own) < 8.0:
                continue
            centre = unit(mean([line.embedding for line in own]))
            if dot(centre, self.states[state]) < 0.98:
                changed = True
            self.states[state] = centre
        return changed

    def _sequence(self):
        """Inside a voice that merges several people, give every line the speaker its neighbours imply."""
        self.split = {}
        for voice in self.voices:
            if voice in self.catch_all:
                continue
            own = [line for line in self.lines if line.voice == voice]
            leaving = {}
            for line in own:
                if line.proposal is not None and line.speech >= LONG_SPEECH:
                    leaving[line.proposal.to] = leaving.get(line.proposal.to, 0.0) + line.speech
            long_speech = sum(line.speech for line in own if line.speech >= LONG_SPEECH)
            if sum(leaving.values()) < max(SPLIT_SPEECH, SPLIT_SHARE * long_speech):
                continue
            states = [f"voice:{voice}"] + [state for state, speech in leaving.items() if speech >= 3.0]
            self.split[voice] = states
            for line, state in zip(own, self._path(own, states)):
                current = f"voice:{voice}"
                if line.proposal is not None and line.proposal.confidence == "high":
                    continue
                if state == current:
                    line.proposal = None
                    continue
                lead = line.scores[state] - line.scores[current]
                evident = line.speech >= EVIDENT_SPEECH and lead >= 0.1
                line.proposal = Proposal(state, "medium" if evident else "low", "sequence")

    def _path(self, lines, states):
        def pull(line, state):
            return SEQUENCE_WEIGHT * min(1.0, line.speech / SEQUENCE_FULL_SPEECH) * line.scores[state]

        def change(previous, line):
            if previous.turn != line.turn:
                interjected = self._interjected(previous.end, line.start)
                return CHANGE_AFTER_INTERJECTION if interjected else CHANGE_ACROSS_TURNS
            return CHANGE_AFTER_SENTENCE if previous.ends_sentence else CHANGE_MID_SENTENCE

        totals = [[pull(lines[0], state) for state in states]]
        came_from = [[0] * len(states)]
        for index in range(1, len(lines)):
            cost = change(lines[index - 1], lines[index])
            row, back = [], []
            for to in range(len(states)):
                best = max(range(len(states)), key=lambda prior: totals[-1][prior] - (0 if prior == to else cost))
                row.append(totals[-1][best] - (0 if best == to else cost) + pull(lines[index], states[to]))
                back.append(best)
            totals.append(row)
            came_from.append(back)
        at = max(range(len(states)), key=lambda state: totals[-1][state])
        path = [at]
        for index in range(len(lines) - 1, 0, -1):
            at = came_from[index][at]
            path.append(at)
        return [states[state] for state in reversed(path)]

    def _settle_suspects(self):
        for _ in range(4):
            before = sum(line.proposal is not None for line in self.lines)
            for index, line in enumerate(self.lines):
                if line.proposal is not None or not self.is_suspect(line):
                    continue
                if self._propose_by_chunk(line):
                    continue
                if line.voice in self.catch_all and self._propose_by_continuation(index):
                    continue
                self._propose_by_neighbours(index)
            if sum(line.proposal is not None for line in self.lines) == before:
                break

    def _propose_by_voice(self, line):
        if line.speech < EVIDENT_SPEECH or self.is_degraded(line):
            return
        ranked = line.ranked(self.real_states)
        (best, score), runner_up = ranked[0], ranked[1][1] if len(ranked) > 1 else 0.0
        current = f"voice:{line.voice}"
        if best == current:
            return
        over_others = score - runner_up
        over_current = over_others if line.voice in self.catch_all else score - line.scores[current]
        if line.speech >= LONG_SPEECH and score >= STRONG_MATCH and over_current >= LEAD and over_others >= 0.15:
            line.proposal = Proposal(best, "high", "voice")
        elif score >= MATCH and over_current >= STRONG_LEAD and over_others >= LEAD:
            line.proposal = Proposal(best, "medium", "voice")

    def _chunk_states(self):
        if not hasattr(self, "_chunks"):
            self._chunks = []
            captured = next(
                (entry["chunks"] for entry in self.call.chunks["tracks"] if entry["track"] == "system"), []
            )
            for chunk in captured:
                vector = unit(chunk["embedding"])
                if self.degraded_direction is not None and dot(vector, self.degraded_direction) >= MATCH:
                    continue
                ranked = sorted(
                    ((dot(vector, self.states[state]), state) for state in self.real_states), reverse=True
                )
                runner_up = ranked[1][0] if len(ranked) > 1 else 0.0
                if ranked[0][0] >= CANDIDATE_MATCH and ranked[0][0] - runner_up >= LEAD:
                    self._chunks.append((chunk["span"][0], chunk["span"][1], ranked[0][1], ranked[0][0]))
        return self._chunks

    def _propose_by_chunk(self, line):
        """The diarizer's own chunk starting or ending at this line and running into one person's clear speech."""

        def is_heard_edge(edge, moment):
            on_grid = abs(edge / CHUNK_GRID - round(edge / CHUNK_GRID)) < 1e-6
            return not on_grid and abs(moment - edge) <= CHUNK_EDGE

        covering = {}
        for start, end, state, score in self._chunk_states():
            reaches = start <= line.start + CHUNK_SLACK and end >= line.end - CHUNK_SLACK
            if reaches and (is_heard_edge(start, line.start) or is_heard_edge(end, line.end)):
                covering.setdefault(state, []).append(score)
        if not covering:
            return False
        ranked = sorted(covering.items(), key=lambda item: -len(item[1]))
        state, scores = ranked[0]
        if len(ranked) > 1 and len(scores) < 2 * len(ranked[1][1]):
            return False
        if state == f"voice:{line.voice}":
            return False
        rival = max((line.scores[other] for other in self.real_states if other != state), default=0.0)
        if rival >= MATCH and line.scores[state] < rival - 0.1:
            return False
        line.proposal = Proposal(state, "medium", "chunk")
        return True

    def _interjected(self, start, end):
        return any(start <= moment < end for moment in self.mic_starts)

    def _propose_by_continuation(self, index):
        """A sentence cut in two across voices belongs to whichever side has a voice."""
        line = self.lines[index]
        targets = []
        if index + 1 < len(self.lines) and not line.ends_sentence:
            following = self.lines[index + 1]
            if following.start - line.end <= CONTINUATION_GAP and not self._interjected(line.end, following.start):
                targets.append(self.resolved(following))
        if index > 0 and not self.lines[index - 1].ends_sentence:
            previous = self.lines[index - 1]
            if line.start - previous.end <= CONTINUATION_GAP and not self._interjected(previous.end, line.start):
                targets.append(self.resolved(previous))
        targets = {state for state in targets if self._is_real(state)}
        if len(targets) != 1:
            return False
        (state,) = targets
        if state == f"voice:{line.voice}":
            return False
        line.proposal = Proposal(state, "high", "continues")
        return True

    def _propose_by_neighbours(self, index):
        """A suspect line with one other speaker close on both sides, and nobody else in between.

        In a catch-all voice the neighbours' present speaker counts. In a real voice only neighbours
        that are themselves moving count, so a line never leaves on the strength of standing still.
        """
        line = self.lines[index]
        around = []
        for other in (index - 1, index + 1):
            if not 0 <= other < len(self.lines):
                return False
            neighbour = self.lines[other]
            gap = line.start - neighbour.end if other < index else neighbour.start - line.end
            if gap > 1.5 or self._interjected(min(line.end, neighbour.end), max(line.start, neighbour.start)):
                return False
            if line.voice not in self.catch_all and neighbour.proposal is None:
                return False
            around.append(self.resolved(neighbour))
        if around[0] != around[1] or not self._is_real(around[0]) or around[0] == f"voice:{line.voice}":
            return False
        line.proposal = Proposal(around[0], "medium", "between")
        return True

    # What is left for judgment

    def undecided(self):
        """Lines no rule settles, each with why it is in doubt."""
        left = []
        for index, line in enumerate(self.lines):
            if line.proposal is not None:
                continue
            if line.voice in self.catch_all:
                left.append((line, "in a catch-all voice"))
            elif self._is_contested(line):
                left.append((line, "sounds more like another speaker, not clearly enough to move"))
            elif self.is_suspect(line) and self._opens_or_closes_turn(index):
                left.append((line, "sounds like nobody, where a turn changes hands"))
        return left

    def _is_contested(self, line):
        if line.speech < EVIDENT_SPEECH or self.is_degraded(line):
            return False
        best, score = line.ranked(self.real_states)[0]
        current = f"voice:{line.voice}"
        return best != current and score >= MATCH and score - line.scores[current] >= 0.1

    def _opens_or_closes_turn(self, index):
        """Whether only suspect lines lie between this one and an end of its turn, after a sentence end."""
        line = self.lines[index]
        same_turn = lambda other: 0 <= other < len(self.lines) and self.lines[other].turn == line.turn
        for step in (-1, 1):
            other = index + step
            while same_turn(other) and self.is_suspect(self.lines[other]):
                other += step
            if not same_turn(other):
                inward = index - step
                while same_turn(inward) and self.is_suspect(self.lines[inward]):
                    inward -= step
                if not same_turn(inward) or step == 1 and self.lines[inward].ends_sentence or step == -1:
                    return True
        return False

    def unheard(self):
        """Suspect lines inside a turn: seldom another speaker, listed so a reader can check the words."""
        listed = {line.id for line, _ in self.undecided()}
        return [
            line
            for line in self.lines
            if line.proposal is None and line.id not in listed and line.speech >= 0.4 and self.is_suspect(line)
        ]

    def possible(self):
        """Short lines that sound like someone with no voice here: too little speech to move on their own."""
        found = []
        present = {self.mostly[voice] for voice in self.voices} | set(self.attributions.values())
        for line in self.lines:
            if line.proposal is not None or not EVIDENT_SPEECH <= line.speech < LONG_SPEECH:
                continue
            person, score, lead = self._best_person(line.embedding)
            if person is None or person in present or person in self.candidates:
                continue
            if score >= MATCH and lead >= 0.1 and score - line.scores[f"voice:{line.voice}"] >= STRONG_LEAD:
                found.append((line, person, score))
        return found

    # Output

    def name_of(self, state):
        kind, _, key = state.partition(":")
        if kind == "person":
            return self.call.people.get(key, key[:8]) + " (new voice)"
        return self.call.speaker(key)

    def record(self):
        return {
            "state": self.call.state(),
            "lines": [
                {
                    "id": line.id,
                    "first": min(word.index for word in line.words),
                    "last": max(word.index for word in line.words),
                    "words": [word.index for word in line.words],
                    "start": line.start,
                    "end": line.end,
                    "voice": line.voice,
                    "text": line.text,
                    "proposal": None
                    if line.proposal is None
                    else {"to": line.proposal.to, "confidence": line.proposal.confidence, "basis": line.proposal.basis},
                }
                for line in self.lines
            ],
            "catchAll": sorted(self.catch_all),
            "suggested": self.suggested,
        }

    def save(self):
        with open(os.path.join(self.call.cache, "evidence.json"), "w", encoding="utf-8") as handle:
            json.dump(self.record(), handle)

    def row(self, line, target=None):
        ranked = line.ranked()[:3]
        scores = " ".join(f"{self.name_of(state).split()[0][:8]} {score:.2f}" for state, score in ranked)
        move = self.call.speaker(line.voice)
        if target is not None:
            move += " -> " + self.name_of(target)
        return f"{line.id:<5} {clock(line.start):>7} {line.speech:4.1f}s  {move:<44} [{scores}]  {line.text[:90]}"

    def context(self, index, width=2):
        """The lines and microphone turns around one line, in the order they were said."""
        line = self.lines[index]
        nearby = self.lines[max(0, index - width) : index + width + 1]
        said = [
            (other.start, self.name_of(self.resolved(other)), other.text)
            for other in nearby
            if other is not line
        ]
        for turn in self.transcript.turns:
            if turn.voice == self.call.microphone and nearby[0].start - 1 <= turn.start <= nearby[-1].end + 1:
                said.append((turn.start, "Me", turn.text))
        rows = []
        for start, speaker, text in sorted(said):
            side = "before" if start < line.start else "after "
            rows.append(f"{side} {clock(start):>7}  {speaker:<20} {text[:100]}")
        return rows

    def _speaker_rows(self):
        call = self.call
        rows = []
        for voice in self.voices:
            own = [line for line in self.lines if line.voice == voice]
            speech = sum(end - start for start, end in self.transcript.spans(voice))
            notes = []
            if voice in self.catch_all:
                notes.append("CATCH-ALL: fragments of several people, not a person")
            elif voice in self.suggested:
                name = call.people.get(self.suggested[voice])
                notes.append(f"unnamed; sounds like {name}, and the plan will name it so")
            elif voice not in self.attributions:
                person, score, _ = self._best_person(self.states[f"voice:{voice}"])
                notes.append(f"unnamed; closest known person {call.people.get(person, 'none')} {score:.2f}")
            if voice in self.split:
                notes.append("MERGED: " + " + ".join(self.name_of(state) for state in self.split[voice]))
            also = [
                f"{call.people.get(person)} {sum(line.speech for line in lines):.0f}s"
                for person, lines in self.votes[voice].items()
                if person != self.mostly[voice]
            ]
            if also:
                notes.append("also heard in it: " + ", ".join(also))
            label = call.labels.get(voice, "new")
            rows.append(
                f"  {label:<4} {voice[:8]}  {call.speaker(voice):<28} {speech:6.0f}s {len(own):4d} lines  "
                + "; ".join(notes)
            )
        for person, lines in self.candidates.items():
            speech = sum(line.speech for line in lines)
            name = call.people.get(person)
            rows.append(f"  no voice yet   {name:<28} {speech:6.0f}s {len(lines):4d} long lines sound like them")
        return rows

    def report(self):
        call = self.call
        duration = clock(call.conversation["duration"])
        out = [f"{call.name}  ({duration}, {len(call.grouping.system_words)} system words, {len(self.lines)} lines)"]
        out += ["", "Speakers"] + self._speaker_rows()
        proposed = [line for line in self.lines if line.proposal is not None]
        out += ["", f"Proposals ({len(proposed)})"]
        for confidence in ("high", "medium", "low"):
            for line in proposed:
                if line.proposal.confidence == confidence:
                    out.append(f"  {confidence:<6} {line.proposal.basis:<9} " + self.row(line, line.proposal.to))
        left = self.undecided()
        out += ["", f"Undecided ({len(left)}): decide each from the words around it, or leave it"]
        index_of = {line.id: index for index, line in enumerate(self.lines)}
        for line, reason in left:
            out.append(f"  {self.row(line)}   ({reason})")
            out += ["      " + row for row in self.context(index_of[line.id])]
        possible = self.possible()
        if possible:
            out += ["", f"Possible ({len(possible)}): short lines that sound like someone with no voice here"]
            for line, person, score in possible:
                out.append(f"  {self.row(line)}   sounds like {call.people.get(person)} {score:.2f}")
        unheard = self.unheard()
        if unheard:
            out += ["", f"Unheard ({len(unheard)}): inside a turn, sounding like nobody; read in context"]
            out += ["  " + self.row(line) for line in unheard]
        return "\n".join(out)
