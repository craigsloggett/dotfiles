"""Who each line of system speech sounds like, and the moves that need no judgment.

A line is a sentence-sized run of words in one voice. Each is embedded with Hark's own
model and scored against every speaker the conversation could hold: the voices already
in it, and people heard in other conversations. Rules that need no judgment turn the
scores into proposals; the lines no rule settles are listed for whoever is driving.
"""

import json
from pathlib import Path
from typing import Any

from . import embed, regroup, store
from .call import Call, clock
from .embed import dot, mean, unit

# A line shorter than this embeds too noisily to stand as evidence on its own.
EVIDENT_SPEECH = 0.8
LONG_SPEECH = 2.0
LINE_PAUSE = 0.6
LINE_LENGTH = 9.5

# Scores are cosine similarities. On the conversations these were tuned against, a
# person's clean lines scored 0.6 to 0.9 against their own voice and under 0.4 against
# anyone else's.
MATCH = 0.5
STRONG_MATCH = 0.55
CANDIDATE_MATCH = 0.6
NO_MATCH = 0.35
LEAD = 0.2
STRONG_LEAD = 0.3

# A voice is a merge of several people once this much of its long speech sounds like
# someone else.
SPLIT_SPEECH = 10.0
SPLIT_SHARE = 0.15
# How strongly a line's score pulls against the cost of changing speaker between lines;
# changing mid-sentence costs most, and across turns least. Carried over from the merges
# this was tuned on.
SEQUENCE_WEIGHT = 13.0
SEQUENCE_FULL_SPEECH = 1.5
CHANGE_MID_SENTENCE = 3.0
CHANGE_AFTER_SENTENCE = 1.5
CHANGE_ACROSS_TURNS = 1.0
CHANGE_AFTER_INTERJECTION = 0.5

CONTINUATION_GAP = 0.8
CHUNK_EDGE = 0.5
CHUNK_SLACK = 0.3
# The diarizer embeds ten-second windows two seconds apart, so a chunk edge on that grid
# is where the window stopped, not where the speaker did.
CHUNK_GRID = 2.0


class Line:
    def __init__(
        self, number: int, words: list[regroup.Word], voice: str, turn: int
    ) -> None:
        self.id = f"s{number}"
        self.words = words
        self.voice = voice
        self.turn = turn
        self.start = words[0].start
        self.end = words[-1].end
        self.speech = sum(word.end - word.start for word in words)
        self.text = " ".join(word.text for word in words)
        self.embedding: list[float] = []
        self.scores: dict[str, float] = {}
        self.proposal: Proposal | None = None

    @property
    def ends_sentence(self) -> bool:
        return self.words[-1].ends_sentence

    def ranked(self, among: list[str] | None = None) -> list[tuple[str, float]]:
        scores = (
            self.scores if among is None else {key: self.scores[key] for key in among}
        )
        return sorted(scores.items(), key=lambda item: -item[1])


class Proposal:
    def __init__(self, to: str, confidence: str, basis: str) -> None:
        self.to = to
        self.confidence = confidence
        self.basis = basis


def lines_of(transcript: regroup.Transcript, microphone: str | None) -> list[Line]:
    lines: list[Line] = []
    for index, turn in enumerate(transcript.turns):
        voice = turn.voice
        if voice is None or voice == microphone:
            continue
        current: list[regroup.Word] = []
        for word in turn.words:
            pauses = current and word.start - current[-1].end >= LINE_PAUSE
            runs_long = current and word.end - current[0].start > LINE_LENGTH
            if pauses or runs_long:
                lines.append(Line(len(lines), current, voice, index))
                current = []
            current.append(word)
            if word.ends_sentence:
                lines.append(Line(len(lines), current, voice, index))
                current = []
        if current:
            lines.append(Line(len(lines), current, voice, index))
    return lines


def exemplars(excluding: str) -> dict[str, list[list[float]]]:
    """Each person's voiceprints from other conversations.

    Only voices past the floor Hark's own suggester applies count.
    """
    trusted: dict[str, list[list[float]]] = {}
    for name in store.folders():
        if name == excluding:
            continue
        folder = store.CONVERSATIONS / name
        files = [
            store.path_of(folder, layer)
            for layer in ("conversation", "transcript", "voiceprints")
        ]
        if not all(file.exists() for file in files):
            continue
        try:
            conversation = store.read(files[0], "conversation")
            turns = store.read(files[1], "transcript")["turns"]
            prints = store.read(files[2], "voiceprints")["byVoice"]
        except (store.SchemaMismatchError, ValueError):
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
    def __init__(self, call: Call) -> None:
        self.call = call
        self.transcript = call.rebuilt()
        self.lines = lines_of(self.transcript, call.microphone)
        self.voices = [
            voice
            for voice in self.transcript.voices
            if voice is not None and voice != call.microphone
        ]
        self.attributions = call.conversation["attributions"]
        self.mic_starts = [
            turn.start
            for turn in self.transcript.turns
            if turn.voice == call.microphone
        ]
        self._embed()
        self.people = {
            person: unit(mean(prints))
            for person, prints in exemplars(call.name).items()
        }
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

    def _embed(self) -> None:
        duration = self.call.conversation["duration"]
        requests = {
            line.id: embed.request_of(line.words, duration) for line in self.lines
        }
        vectors = embed.embeddings(self.call, requests)
        for line in self.lines:
            line.embedding = vectors[line.id]

    def _best_person(self, vector: list[float]) -> tuple[str | None, float, float]:
        ranked = sorted(
            ((dot(vector, print_), person) for person, print_ in self.people.items()),
            reverse=True,
        )
        if not ranked:
            return None, 0.0, 0.0
        runner_up = ranked[1][0] if len(ranked) > 1 else 0.0
        return ranked[0][1], ranked[0][0], ranked[0][0] - runner_up

    def _reference_voices(self) -> None:
        """Each voice's own sound.

        Its long lines that match the person it mostly is, else all of them.
        """
        self.references: dict[str, list[float]] = {}
        self.mostly: dict[str, str | None] = {}
        self.suggested: dict[str, str] = {}
        self.votes: dict[str, dict[str, list[Line]]] = {}
        for voice in self.voices:
            long = [
                line
                for line in self.lines
                if line.voice == voice and line.speech >= LONG_SPEECH
            ]
            votes: dict[str, list[Line]] = {}
            for line in long:
                person, score, lead = self._best_person(line.embedding)
                if person is not None and score >= CANDIDATE_MATCH and lead >= 0.1:
                    votes.setdefault(person, []).append(line)
            self.votes[voice] = votes
            named = self.attributions.get(voice)
            person = named if named in self.people else None
            if person is None and votes:
                top = max(
                    votes, key=lambda key: sum(line.speech for line in votes[key])
                )
                if sum(line.speech for line in votes[top]) >= 8.0:
                    person = top
                    if named is None:
                        self.suggested[voice] = top
            self.mostly[voice] = person
            if person is not None:
                own = [
                    line.embedding
                    for line in long
                    if dot(line.embedding, self.people[person]) >= MATCH
                ]
                self.references[voice] = (
                    unit(mean(own)) if len(own) >= 2 else self.people[person]
                )
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

    def _find_candidates(self) -> None:
        """People with no voice here, heard in long lines more than their own voice."""
        present = {self.mostly[voice] for voice in self.voices} | set(
            self.attributions.values()
        )
        heard: dict[str, list[Line]] = {}
        for line in self.lines:
            if line.speech < LONG_SPEECH:
                continue
            person, score, lead = self._best_person(line.embedding)
            if (
                person is None
                or person in present
                or score < CANDIDATE_MATCH
                or lead < 0.1
            ):
                continue
            if score - dot(line.embedding, self.references[line.voice]) >= 0.15:
                heard.setdefault(person, []).append(line)
        self.candidates = {
            person: lines
            for person, lines in heard.items()
            if sum(line.speech for line in lines) >= 3.0
        }

    def _score(self) -> None:
        if not hasattr(self, "states"):
            self.states = {
                f"voice:{voice}": self.references[voice] for voice in self.voices
            }
            for person in self.candidates:
                self.states[f"person:{person}"] = self.people[person]
        for line in self.lines:
            line.scores = {
                state: dot(line.embedding, reference)
                for state, reference in self.states.items()
            }

    def _find_catch_all(self) -> None:
        """Speech cut off at a turn's edges or spoken over embeds to one point.

        It does so whoever said it. The diarizer often gathers it into a voice of its
        own. That voice is nobody, and no score against it means anything.
        """
        self.degraded_direction: list[float] | None = None
        self.catch_all: set[str] = set()
        evident = [line for line in self.lines if line.speech >= EVIDENT_SPEECH]
        for voice in self.voices:
            if voice in self.attributions:
                continue
            own = [line for line in self.lines if line.voice == voice]
            if (
                not own
                or sorted(line.speech for line in own)[len(own) // 2] >= LONG_SPEECH
            ):
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
        real = [
            state
            for state in self.states
            if state.removeprefix("voice:") not in self.catch_all
        ]
        self.real_states = real
        lost = [
            line
            for line in evident
            if max(line.scores[state] for state in real) < NO_MATCH
        ]
        if len(lost) >= 4:
            centre = unit(mean([line.embedding for line in lost]))
            close = [
                line.embedding
                for line in lost
                if dot(line.embedding, centre) >= CANDIDATE_MATCH
            ]
            if len(close) >= 4:
                self.degraded_direction = unit(mean(close))

    def is_degraded(self, line: Line) -> bool:
        if line.speech < EVIDENT_SPEECH:
            return True
        best = max(line.scores[state] for state in self.real_states)
        if best < NO_MATCH:
            return True
        if self.degraded_direction is None:
            return False
        return (
            dot(line.embedding, self.degraded_direction) >= CANDIDATE_MATCH
            and best < 0.45
        )

    def is_suspect(self, line: Line) -> bool:
        """A line unlike its own voice, or one in a voice that is nobody's."""
        if line.voice in self.catch_all:
            return True
        return (
            line.speech >= 0.4
            and line.scores[f"voice:{line.voice}"] < NO_MATCH
            and self.is_degraded(line)
        )

    # Proposals

    def resolved(self, line: Line) -> str:
        return line.proposal.to if line.proposal else f"voice:{line.voice}"

    def _is_real(self, state: str) -> bool:
        return state.removeprefix("voice:") not in self.catch_all

    def _refine_references(self) -> bool:
        """Re-centre each speaker on the long lines clearly theirs in this conversation.

        A print from another conversation is a different room and microphone; a
        speaker's own lines here score higher against each other. Only long, clearly
        matched lines move a reference, so the speech that sounds like nobody cannot
        drift into whoever has the fewest lines.
        """
        changed = False
        for state in self.real_states:
            own = []
            for line in self.lines:
                if line.speech < LONG_SPEECH or self.is_degraded(line):
                    continue
                if line.proposal is not None:
                    is_own = (
                        line.proposal.to == state and line.proposal.confidence == "high"
                    )
                else:
                    best, score = line.ranked(self.real_states)[0]
                    is_own = (
                        f"voice:{line.voice}" == state
                        and best == state
                        and score >= MATCH
                    )
                if is_own:
                    own.append(line)
            if len(own) < 3 or sum(line.speech for line in own) < 8.0:
                continue
            centre = unit(mean([line.embedding for line in own]))
            if dot(centre, self.states[state]) < 0.98:
                changed = True
            self.states[state] = centre
        return changed

    def _sequence(self) -> None:
        """In a merged voice, give every line the speaker its neighbours imply."""
        self.split: dict[str, list[str]] = {}
        for voice in self.voices:
            if voice in self.catch_all:
                continue
            own = [line for line in self.lines if line.voice == voice]
            leaving: dict[str, float] = {}
            for line in own:
                if line.proposal is not None and line.speech >= LONG_SPEECH:
                    leaving[line.proposal.to] = (
                        leaving.get(line.proposal.to, 0.0) + line.speech
                    )
            long_speech = sum(line.speech for line in own if line.speech >= LONG_SPEECH)
            if sum(leaving.values()) < max(SPLIT_SPEECH, SPLIT_SHARE * long_speech):
                continue
            states = [
                f"voice:{voice}",
                *(state for state, speech in leaving.items() if speech >= 3.0),
            ]
            self.split[voice] = states
            for line, state in zip(own, self._path(own, states), strict=True):
                current = f"voice:{voice}"
                if line.proposal is not None and line.proposal.confidence == "high":
                    continue
                if state == current:
                    line.proposal = None
                    continue
                lead = line.scores[state] - line.scores[current]
                evident = line.speech >= EVIDENT_SPEECH and lead >= 0.1
                line.proposal = Proposal(
                    state, "medium" if evident else "low", "sequence"
                )

    def _path(self, lines: list[Line], states: list[str]) -> list[str]:
        def pull(line: Line, state: str) -> float:
            return (
                SEQUENCE_WEIGHT
                * min(1.0, line.speech / SEQUENCE_FULL_SPEECH)
                * line.scores[state]
            )

        def change(previous: Line, line: Line) -> float:
            if previous.turn != line.turn:
                interjected = self._interjected(previous.end, line.start)
                return CHANGE_AFTER_INTERJECTION if interjected else CHANGE_ACROSS_TURNS
            return (
                CHANGE_AFTER_SENTENCE if previous.ends_sentence else CHANGE_MID_SENTENCE
            )

        totals = [[pull(lines[0], state) for state in states]]
        came_from = [[0] * len(states)]
        for index in range(1, len(lines)):
            cost = change(lines[index - 1], lines[index])
            row: list[float] = []
            back: list[int] = []
            for to in range(len(states)):
                best = max(
                    range(len(states)),
                    key=lambda prior: totals[-1][prior] - (0 if prior == to else cost),
                )
                row.append(
                    totals[-1][best]
                    - (0 if best == to else cost)
                    + pull(lines[index], states[to])
                )
                back.append(best)
            totals.append(row)
            came_from.append(back)
        at = max(range(len(states)), key=lambda state: totals[-1][state])
        path = [at]
        for index in range(len(lines) - 1, 0, -1):
            at = came_from[index][at]
            path.append(at)
        return [states[state] for state in reversed(path)]

    def _settle_suspects(self) -> None:
        for _ in range(4):
            before = sum(line.proposal is not None for line in self.lines)
            for index, line in enumerate(self.lines):
                if line.proposal is not None or not self.is_suspect(line):
                    continue
                if self._propose_by_chunk(line):
                    continue
                if line.voice in self.catch_all and self._propose_by_continuation(
                    index
                ):
                    continue
                self._propose_by_neighbours(index)
            if sum(line.proposal is not None for line in self.lines) == before:
                break

    def _propose_by_voice(self, line: Line) -> None:
        if line.speech < EVIDENT_SPEECH or self.is_degraded(line):
            return
        ranked = line.ranked(self.real_states)
        (best, score), runner_up = ranked[0], ranked[1][1] if len(ranked) > 1 else 0.0
        current = f"voice:{line.voice}"
        if best == current:
            return
        over_others = score - runner_up
        over_current = (
            over_others
            if line.voice in self.catch_all
            else score - line.scores[current]
        )
        if (
            line.speech >= LONG_SPEECH
            and score >= STRONG_MATCH
            and over_current >= LEAD
            and over_others >= 0.15
        ):
            line.proposal = Proposal(best, "high", "voice")
        elif score >= MATCH and over_current >= STRONG_LEAD and over_others >= LEAD:
            line.proposal = Proposal(best, "medium", "voice")

    def _chunk_states(self) -> list[tuple[float, float, str, float]]:
        if not hasattr(self, "_chunks"):
            self._chunks: list[tuple[float, float, str, float]] = []
            captured = next(
                (
                    entry["chunks"]
                    for entry in self.call.chunks["tracks"]
                    if entry["track"] == "system"
                ),
                [],
            )
            for chunk in captured:
                vector = unit(chunk["embedding"])
                if (
                    self.degraded_direction is not None
                    and dot(vector, self.degraded_direction) >= MATCH
                ):
                    continue
                ranked = sorted(
                    (
                        (dot(vector, self.states[state]), state)
                        for state in self.real_states
                    ),
                    reverse=True,
                )
                runner_up = ranked[1][0] if len(ranked) > 1 else 0.0
                if ranked[0][0] >= CANDIDATE_MATCH and ranked[0][0] - runner_up >= LEAD:
                    self._chunks.append(
                        (chunk["span"][0], chunk["span"][1], ranked[0][1], ranked[0][0])
                    )
        return self._chunks

    def _propose_by_chunk(self, line: Line) -> bool:
        """The diarizer's own chunk starting or ending at this line.

        The chunk must run into one person's clear speech.
        """

        def is_heard_edge(edge: float, moment: float) -> bool:
            on_grid = abs(edge / CHUNK_GRID - round(edge / CHUNK_GRID)) < 1e-6
            return not on_grid and abs(moment - edge) <= CHUNK_EDGE

        covering: dict[str, list[float]] = {}
        for start, end, state, score in self._chunk_states():
            reaches = (
                start <= line.start + CHUNK_SLACK and end >= line.end - CHUNK_SLACK
            )
            if reaches and (
                is_heard_edge(start, line.start) or is_heard_edge(end, line.end)
            ):
                covering.setdefault(state, []).append(score)
        if not covering:
            return False
        ranked = sorted(covering.items(), key=lambda item: -len(item[1]))
        state, scores = ranked[0]
        if len(ranked) > 1 and len(scores) < 2 * len(ranked[1][1]):
            return False
        if state == f"voice:{line.voice}":
            return False
        rival = max(
            (line.scores[other] for other in self.real_states if other != state),
            default=0.0,
        )
        if rival >= MATCH and line.scores[state] < rival - 0.1:
            return False
        line.proposal = Proposal(state, "medium", "chunk")
        return True

    def _interjected(self, start: float, end: float) -> bool:
        return any(start <= moment < end for moment in self.mic_starts)

    def _propose_by_continuation(self, index: int) -> bool:
        """A sentence cut in two across voices belongs to whichever side has a voice."""
        line = self.lines[index]
        targets: list[str] = []
        if index + 1 < len(self.lines) and not line.ends_sentence:
            following = self.lines[index + 1]
            if following.start - line.end <= CONTINUATION_GAP and not self._interjected(
                line.end, following.start
            ):
                targets.append(self.resolved(following))
        if index > 0 and not self.lines[index - 1].ends_sentence:
            previous = self.lines[index - 1]
            if line.start - previous.end <= CONTINUATION_GAP and not self._interjected(
                previous.end, line.start
            ):
                targets.append(self.resolved(previous))
        real = {state for state in targets if self._is_real(state)}
        if len(real) != 1:
            return False
        (state,) = real
        if state == f"voice:{line.voice}":
            return False
        line.proposal = Proposal(state, "high", "continues")
        return True

    def _propose_by_neighbours(self, index: int) -> bool:
        """A suspect line with one other speaker close on both sides, nobody in between.

        In a catch-all voice the neighbours' present speaker counts. In a real voice
        only neighbours that are themselves moving count, so a line never leaves on the
        strength of standing still.
        """
        line = self.lines[index]
        around: list[str] = []
        for other in (index - 1, index + 1):
            if not 0 <= other < len(self.lines):
                return False
            neighbour = self.lines[other]
            gap = (
                line.start - neighbour.end
                if other < index
                else neighbour.start - line.end
            )
            if gap > 1.5 or self._interjected(
                min(line.end, neighbour.end), max(line.start, neighbour.start)
            ):
                return False
            if line.voice not in self.catch_all and neighbour.proposal is None:
                return False
            around.append(self.resolved(neighbour))
        if (
            around[0] != around[1]
            or not self._is_real(around[0])
            or around[0] == f"voice:{line.voice}"
        ):
            return False
        line.proposal = Proposal(around[0], "medium", "between")
        return True

    # What is left for judgment

    def undecided(self) -> list[tuple[Line, str]]:
        """Lines no rule settles, each with why it is in doubt."""
        left: list[tuple[Line, str]] = []
        for index, line in enumerate(self.lines):
            if line.proposal is not None:
                continue
            if line.voice in self.catch_all:
                left.append((line, "in a catch-all voice"))
            elif self._is_contested(line):
                left.append(
                    (
                        line,
                        "sounds more like another speaker, not clearly enough to move",
                    )
                )
            elif self.is_suspect(line) and self._opens_or_closes_turn(index):
                left.append((line, "sounds like nobody, where a turn changes hands"))
        return left

    def _is_contested(self, line: Line) -> bool:
        if line.speech < EVIDENT_SPEECH or self.is_degraded(line):
            return False
        best, score = line.ranked(self.real_states)[0]
        current = f"voice:{line.voice}"
        return (
            best != current and score >= MATCH and score - line.scores[current] >= 0.1
        )

    def _opens_or_closes_turn(self, index: int) -> bool:
        """Whether only suspect lines lie between this one and an end of its turn.

        Counted after a sentence end.
        """
        line = self.lines[index]

        def same_turn(other: int) -> bool:
            return 0 <= other < len(self.lines) and self.lines[other].turn == line.turn

        for step in (-1, 1):
            other = index + step
            while same_turn(other) and self.is_suspect(self.lines[other]):
                other += step
            if not same_turn(other):
                inward = index - step
                while same_turn(inward) and self.is_suspect(self.lines[inward]):
                    inward -= step
                if (
                    not same_turn(inward)
                    or (step == 1 and self.lines[inward].ends_sentence)
                    or step == -1
                ):
                    return True
        return False

    def unheard(self) -> list[Line]:
        """Suspect lines inside a turn, listed so a reader can check the words.

        They are seldom another speaker.
        """
        listed = {line.id for line, _ in self.undecided()}
        return [
            line
            for line in self.lines
            if line.proposal is None
            and line.id not in listed
            and line.speech >= 0.4
            and self.is_suspect(line)
        ]

    def possible(self) -> list[tuple[Line, str, float]]:
        """Short lines that sound like someone with no voice here.

        They hold too little speech to move on their own.
        """
        found: list[tuple[Line, str, float]] = []
        present = {self.mostly[voice] for voice in self.voices} | set(
            self.attributions.values()
        )
        for line in self.lines:
            if (
                line.proposal is not None
                or not EVIDENT_SPEECH <= line.speech < LONG_SPEECH
            ):
                continue
            person, score, lead = self._best_person(line.embedding)
            if person is None or person in present or person in self.candidates:
                continue
            if (
                score >= MATCH
                and lead >= 0.1
                and score - line.scores[f"voice:{line.voice}"] >= STRONG_LEAD
            ):
                found.append((line, person, score))
        return found

    # Output

    def name_of(self, state: str) -> str:
        kind, _, key = state.partition(":")
        if kind == "person":
            return f"{self.call.people.get(key, key[:8])} (new voice)"
        return self.call.speaker(key)

    def record(self) -> dict[str, Any]:
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
                    else {
                        "to": line.proposal.to,
                        "confidence": line.proposal.confidence,
                        "basis": line.proposal.basis,
                    },
                }
                for line in self.lines
            ],
            "catchAll": sorted(self.catch_all),
            "suggested": self.suggested,
        }

    def save(self) -> None:
        with (Path(self.call.cache) / "evidence.json").open(
            "w", encoding="utf-8"
        ) as handle:
            json.dump(self.record(), handle)

    def row(self, line: Line, target: str | None = None) -> str:
        ranked = line.ranked()[:3]
        scores = " ".join(
            f"{self.name_of(state).split()[0][:8]} {score:.2f}"
            for state, score in ranked
        )
        move = self.call.speaker(line.voice)
        if target is not None:
            move += " -> " + self.name_of(target)
        return (
            f"{line.id:<5} {clock(line.start):>7} {line.speech:4.1f}s  "
            f"{move:<44} [{scores}]  {line.text[:90]}"
        )

    def context(self, index: int, width: int = 2) -> list[str]:
        """The lines and microphone turns around one line, in the order said."""
        line = self.lines[index]
        nearby = self.lines[max(0, index - width) : index + width + 1]
        said = [
            (other.start, self.name_of(self.resolved(other)), other.text)
            for other in nearby
            if other is not line
        ]
        said.extend(
            (turn.start, "Me", turn.text)
            for turn in self.transcript.turns
            if turn.voice == self.call.microphone
            and nearby[0].start - 1 <= turn.start <= nearby[-1].end + 1
        )
        rows = []
        for start, speaker, text in sorted(said):
            side = "before" if start < line.start else "after "
            rows.append(f"{side} {clock(start):>7}  {speaker:<20} {text[:100]}")
        return rows

    def _speaker_rows(self) -> list[str]:
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
                notes.append(
                    f"unnamed; sounds like {name}, and the plan will name it so"
                )
            elif voice not in self.attributions:
                person, score, _ = self._best_person(self.states[f"voice:{voice}"])
                closest = (
                    call.people.get(person, "none") if person is not None else "none"
                )
                notes.append(f"unnamed; closest known person {closest} {score:.2f}")
            if voice in self.split:
                notes.append(
                    "MERGED: "
                    + " + ".join(self.name_of(state) for state in self.split[voice])
                )
            also = [
                f"{call.people.get(person)} {sum(line.speech for line in lines):.0f}s"
                for person, lines in self.votes[voice].items()
                if person != self.mostly[voice]
            ]
            if also:
                notes.append("also heard in it: " + ", ".join(also))
            label = call.labels.get(voice, "new")
            rows.append(
                f"  {label:<4} {voice[:8]}  {call.speaker(voice):<28} "
                f"{speech:6.0f}s {len(own):4d} lines  " + "; ".join(notes)
            )
        for person, lines in self.candidates.items():
            speech = sum(line.speech for line in lines)
            name = call.people.get(person)
            rows.append(
                f"  no voice yet   {name:<28} {speech:6.0f}s "
                f"{len(lines):4d} long lines sound like them"
            )
        return rows

    def report(self) -> str:
        call = self.call
        duration = clock(call.conversation["duration"])
        out = [
            (
                f"{call.name}  ({duration}, {len(call.grouping.system_words)} "
                f"system words, {len(self.lines)} lines)"
            )
        ]
        out += ["", "Speakers", *self._speaker_rows()]
        proposed = [line for line in self.lines if line.proposal is not None]
        out += ["", f"Proposals ({len(proposed)})"]
        for confidence in ("high", "medium", "low"):
            for line in proposed:
                proposal = line.proposal
                if proposal is not None and proposal.confidence == confidence:
                    out.append(
                        f"  {confidence:<6} {proposal.basis:<9} "
                        + self.row(line, proposal.to)
                    )
        left = self.undecided()
        out += [
            "",
            (
                f"Undecided ({len(left)}): "
                "decide each from the words around it, or leave it"
            ),
        ]
        index_of = {line.id: index for index, line in enumerate(self.lines)}
        for line, reason in left:
            out.append(f"  {self.row(line)}   ({reason})")
            out += ["      " + row for row in self.context(index_of[line.id])]
        possible = self.possible()
        if possible:
            out += [
                "",
                (
                    f"Possible ({len(possible)}): "
                    "short lines that sound like someone with no voice here"
                ),
            ]
            for line, person, score in possible:
                out.append(
                    f"  {self.row(line)}   "
                    f"sounds like {call.people.get(person)} {score:.2f}"
                )
        unheard = self.unheard()
        if unheard:
            out += [
                "",
                (
                    f"Unheard ({len(unheard)}): "
                    "inside a turn, sounding like nobody; read in context"
                ),
            ]
            out += ["  " + self.row(line) for line in unheard]
        return "\n".join(out)
