"""Hark's regrouping, ported line for line from macOS/Sources/Analysis at c7cccfa.

Hark rebuilds a conversation's turns and voiceprints from its recognized words, its
diarized segments, and its corrections. `selftest` replays the whole library through
this port, so a change in Hark shows up as a mismatch there before it can mislead a
plan.
"""

import math
from collections.abc import Iterable, Sequence
from typing import Any

from . import store

type Span = tuple[float, float]

MINIMUM_LABEL_SPEECH = 5.0
SEGMENT_JITTER = 0.25
MAXIMUM_STRANDED_WORDS = 2
LANDING_SILENCE = 0.4
TURN_BREAKING_SILENCE = 1.0
MID_SENTENCE_BREAKING_SILENCE = 2.0
MAXIMUM_WORD_DURATION = 1.0
FILLERS = {"um", "uh"}
WORDS_KEEPING_LIKE = {
    "be", "is", "was", "were", "are", "am", "been", "being",
    "im", "youre", "hes", "shes", "its", "theyre", "thats",
    "feel", "feels", "felt", "feeling",
    "look", "looks", "looked", "looking",
    "sound", "sounds", "sounded", "sounding",
    "seem", "seems", "seemed",
    "just",
    "dont",
    "things",
}  # fmt: skip
PHRASES_KEEPING_LIKE = [
    ["i", "said"], ["i", "say"], ["i", "mentioned"],
    ["you", "said"], ["you", "mentioned"],
    ["we", "talked"],
]  # fmt: skip
MAXIMUM_RESTART_WORDS = 4
ECHO_SHARE = 0.8
ECHO_MINIMUM_WORDS = 3
MAXIMUM_PARAGRAPH_CHARACTERS = 300
MINIMUM_CHUNK_SPEECH = 3.0
MINIMUM_EXEMPLAR_SPEECH = 15.0
MINIMUM_EXEMPLAR_STRETCH = 5.0
STRETCH_PAUSE = 0.5
SIMILARITY_BAR = 0.7
SENTENCE_TERMINALS = ".?!…"


class Word:
    __slots__ = ("end", "ends_sentence", "index", "key", "start", "text")

    def __init__(self, text: str, start: float, end: float, index: int) -> None:
        self.text = text
        self.start = start
        self.end = end
        self.index = index
        self.key = "".join(c for c in text.lower() if c.isalpha() or c.isnumeric())
        self.ends_sentence = bool(text) and text[-1] in SENTENCE_TERMINALS

    def starts_in(self, span: Sequence[float]) -> bool:
        return span[0] <= self.start < span[1]


class Turn:
    __slots__ = ("end", "start", "text", "voice", "words")

    def __init__(self, voice: str | None, words: list[Word], text: str) -> None:
        self.voice = voice
        self.start = words[0].start
        self.end = words[-1].end
        self.text = text
        self.words = words

    def record(self) -> dict[str, Any]:
        return {
            "span": [self.start, self.end],
            "text": self.text,
            "voiceID": self.voice,
        }


def spoken_words(recognition: dict[str, Any], track: str) -> list[Word]:
    """A word stamped longer than a second is carrying the pause after it."""
    stamped = next(
        (entry["words"] for entry in recognition["tracks"] if entry["track"] == track),
        [],
    )
    return [
        Word(
            word["text"],
            word["span"][0],
            min(word["span"][1], word["span"][0] + MAXIMUM_WORD_DURATION),
            index,
        )
        for index, word in enumerate(stamped)
    ]


# Turn+Text.swift


def shown(words: list[Word]) -> list[Word]:
    kept: list[Word] = []
    for index, word in enumerate(words):
        if word.key in FILLERS or _is_throwaway_like(index, words):
            continue
        kept.append(word)
        while True:
            earlier = _restart(kept)
            if earlier is None:
                break
            del kept[earlier[0] : earlier[1]]
    return kept


def text_of(words: list[Word]) -> str:
    return " ".join(word.text for word in shown(words))


def _is_throwaway_like(index: int, words: list[Word]) -> bool:
    if words[index].key != "like":
        return False
    following = [word.key for word in words[index + 1 :]]
    if any(following[: len(phrase)] == phrase for phrase in PHRASES_KEEPING_LIKE):
        return False
    neighbours: list[str] = []
    if index > 0:
        neighbours.append(words[index - 1].key)
    if index + 1 < len(words):
        neighbours.append(words[index + 1].key)
    leans = any(key in FILLERS for key in neighbours) or "like" in neighbours
    if index == 0 or words[index - 1].ends_sentence:
        return words[index].text.endswith(",") or leans
    return words[index - 1].key not in WORDS_KEEPING_LIKE and leans


def _restart(kept: list[Word]) -> tuple[int, int] | None:
    count = len(kept)
    for length in range(min(MAXIMUM_RESTART_WORDS, count // 2), 0, -1):
        earlier = kept[count - 2 * length : count - length]
        later = kept[count - length :]
        if [word.key for word in earlier] != [word.key for word in later]:
            continue
        junction = earlier[-1]
        is_one_word = len({word.key for word in earlier}) == 1
        if junction.ends_sentence or (is_one_word and junction.text.endswith(",")):
            continue
        return (count - 2 * length, count - length)
    return None


# Turn+Paragraphs.swift, Turn+Breaks.swift, Turn+Words.swift


def paragraphs(words: list[Word]) -> list[list[Word]]:
    sentences: list[list[Word]] = []
    sentence: list[Word] = []
    for word in words:
        sentence.append(word)
        if word.ends_sentence:
            sentences.append(sentence)
            sentence = []
    if sentence:
        sentences.append(sentence)

    result: list[list[Word]] = []
    paragraph: list[Word] = []
    for sentence in sentences:
        extended = paragraph + sentence
        if paragraph and len(text_of(extended)) <= MAXIMUM_PARAGRAPH_CHARACTERS:
            paragraph = extended
        else:
            if paragraph:
                result.append(paragraph)
            paragraph = sentence
    if paragraph:
        result.append(paragraph)
    return result


def breaks(
    last: Word,
    following: Word,
    running_since: float,
    gap: Span,
    interjections: Sequence[float],
) -> bool:
    if last.ends_sentence and any(
        running_since < moment <= following.start for moment in interjections
    ):
        return True
    silence = gap[1] - gap[0]
    if silence >= LANDING_SILENCE and any(
        gap[0] <= moment < gap[1] for moment in interjections
    ):
        return True
    if last.ends_sentence:
        return silence >= TURN_BREAKING_SILENCE
    return silence >= MID_SENTENCE_BREAKING_SILENCE


def _turns_of(runs: Iterable[tuple[str | None, list[Word]]]) -> list[Turn]:
    turns: list[Turn] = []
    for voice, words in runs:
        for paragraph in paragraphs(words):
            text = text_of(paragraph)
            if text:
                turns.append(Turn(voice, paragraph, text))
    return turns


def turns_grouping(
    words: list[Word], voice: str | None, interjections: Sequence[float] = ()
) -> list[Turn]:
    groups: list[list[Word]] = []
    for word in words:
        if groups and not breaks(
            groups[-1][-1],
            word,
            groups[-1][0].start,
            (groups[-1][-1].end, word.start),
            interjections,
        ):
            groups[-1].append(word)
        else:
            groups.append([word])
    return _turns_of([(voice, group) for group in groups])


# Transcript+WithoutEcho.swift, Transcript+Recognized.swift


def _words_in(text: str) -> list[str]:
    words: list[str] = []
    word: list[str] = []
    for character in text.lower():
        if character.isalpha() or character.isnumeric():
            word.append(character)
        elif word:
            words.append("".join(word))
            word = []
    if word:
        words.append("".join(word))
    return words


def without_echo(microphone: list[Turn], system: list[Turn]) -> list[Turn]:
    heard = [(turn.start, turn.end, set(_words_in(turn.text))) for turn in system]

    def is_echo(turn: Turn) -> bool:
        said = _words_in(turn.text)
        if len(said) < ECHO_MINIMUM_WORDS:
            return False
        system_words: set[str] = set()
        for start, end, words in heard:
            overlaps = (
                start < turn.end
                and turn.start < end
                and start < end
                and turn.start < turn.end
            )
            if overlaps:
                system_words |= words
        return sum(word in system_words for word in said) / len(said) >= ECHO_SHARE

    return [turn for turn in microphone if not is_echo(turn)]


def microphone_turns(
    microphone_words: list[Word], system_words: list[Word], voice: str | None
) -> list[Turn]:
    if voice is None:
        return []
    system = turns_grouping(system_words, None)
    on_microphone = turns_grouping(
        microphone_words, voice, [turn.start for turn in system]
    )
    return without_echo(on_microphone, system)


# Transcript+Regrouped.swift


class Segment:
    __slots__ = ("end", "label", "start")

    def __init__(self, label: str, start: float, end: float) -> None:
        self.label = label
        self.start = start
        self.end = end

    def distance(self, instant: float) -> float:
        if self.start <= instant < self.end:
            return 0.0
        return self.start - instant if instant < self.start else instant - self.end


class Owned:
    __slots__ = ("pinned", "segment", "voice", "word")

    def __init__(
        self, word: Word, segment: Segment, voice: str, *, pinned: bool = False
    ) -> None:
        self.word = word
        self.segment = segment
        self.voice = voice
        self.pinned = pinned

    @property
    def keeps_own_timing(self) -> bool:
        return self.pinned or self.segment.distance(self.word.start) > SEGMENT_JITTER


def substantial(segments: list[Segment]) -> list[Segment]:
    """A label diarized under five seconds owns no words, unless all labels are."""
    diarized: dict[str, float] = {}
    for segment in segments:
        diarized[segment.label] = diarized.get(segment.label, 0.0) + (
            segment.end - segment.start
        )
    if not any(total >= MINIMUM_LABEL_SPEECH for total in diarized.values()):
        return segments
    return [
        segment
        for segment in segments
        if diarized[segment.label] >= MINIMUM_LABEL_SPEECH
    ]


class Grouping:
    """What Hark keeps between corrections: system word segments, microphone turns."""

    def __init__(
        self,
        recognition: dict[str, Any],
        diarization: dict[str, Any],
        microphone: str | None,
    ) -> None:
        self.system_words = spoken_words(recognition, "system")
        self.microphone_words = spoken_words(recognition, "microphone")
        stamped = next(
            (
                entry["segments"]
                for entry in diarization["tracks"]
                if entry["track"] == "system"
            ),
            [],
        )
        self.segments = [
            Segment(entry["label"], entry["span"][0], entry["span"][1])
            for entry in stamped
        ]
        self.microphone = microphone
        self.exists = bool(self.system_words) and bool(self.segments)
        self.placements: list[tuple[Word, Segment]] = []
        self.microphone_turns: list[Turn] = []
        if not self.exists:
            return
        owning = substantial(self.segments)
        for word in sorted(self.system_words, key=lambda word: word.start):
            nearest = min(
                owning,
                key=lambda segment, start=word.start: segment.distance(start),
            )
            self.placements.append((word, nearest))
        self.microphone_turns = microphone_turns(
            self.microphone_words, self.system_words, microphone
        )


def _reassign(owned: list[Owned], detail: dict[str, Any], discarded: set[int]) -> None:
    for index, entry in enumerate(owned):
        if entry.word.starts_in(detail["span"]):
            entry.voice = detail["voice"]["id"]
            entry.pinned = True
            discarded.discard(index)


def _merge(owned: list[Owned], detail: dict[str, Any]) -> None:
    for entry in owned:
        if entry.voice == detail["voice"]["id"]:
            entry.voice = detail["into"]["id"]


def _discard(owned: list[Owned], detail: dict[str, Any], discarded: set[int]) -> None:
    for index, entry in enumerate(owned):
        if entry.word.starts_in(detail["span"]):
            discarded.add(index)


def _corrected(owned: list[Owned], corrections: list[dict[str, Any]]) -> list[Owned]:
    discarded: set[int] = set()
    for drawn in corrections:
        ((kind, detail),) = drawn["correction"].items()
        if kind == "reassign":
            _reassign(owned, detail, discarded)
        elif kind == "merge":
            _merge(owned, detail)
        elif kind == "discard" and detail["track"] == "system":
            _discard(owned, detail, discarded)
    return [entry for index, entry in enumerate(owned) if index not in discarded]


def _is_discarded(turn: Turn, corrections: list[dict[str, Any]]) -> bool:
    for drawn in corrections:
        detail = drawn["correction"].get("discard")
        if (
            detail
            and detail["track"] == "microphone"
            and detail["span"][0] <= turn.start
            and turn.end <= detail["span"][1]
        ):
            return True
    return False


def _runs(owned: list[Owned], interjections: Sequence[float]) -> list[list[Owned]]:
    runs: list[list[Owned]] = []
    run: list[Owned] = []
    for entry in owned:
        if run and _ends(run, entry, interjections):
            runs.append(run)
            run = []
        run.append(entry)
    if run:
        runs.append(run)
    return runs


def _ends(run: list[Owned], following: Owned, interjections: Sequence[float]) -> bool:
    first, last = run[0], run[-1]
    if last.voice != following.voice:
        return True
    if last.keeps_own_timing or following.keeps_own_timing:
        gap = (last.word.end, following.word.start)
    else:
        gap = (last.segment.end, following.segment.start)
    return breaks(last.word, following.word, first.word.start, gap, interjections)


def _stranded_tail(run: list[Owned]) -> list[Owned]:
    tail: list[Owned] = []
    for entry in reversed(run):
        if entry.word.ends_sentence or entry.pinned:
            break
        tail.append(entry)
        if len(tail) > MAXIMUM_STRANDED_WORDS:
            return []
    return tail[::-1]


def _settled(runs: list[list[Owned]]) -> list[list[Owned]]:
    """A run's last word or two after its final sentence end belong to the next speaker.

    The diarizer cut them late.
    """
    settled: list[list[Owned]] = []
    carried: list[Owned] = []
    for index, original in enumerate(runs):
        run = carried + original
        carried = []
        head = runs[index + 1][0] if index + 1 < len(runs) else None
        if run and head is not None and head.voice != run[0].voice:
            tail = _stranded_tail(run)
            if tail and len(tail) < len(run):
                del run[-len(tail) :]
                carried = [
                    Owned(entry.word, head.segment, head.voice) for entry in tail
                ]
        settled.append(run)
    return settled


class Transcript:
    def __init__(
        self,
        turns: list[Turn],
        voices: list[str | None],
        owners: dict[int, str],
    ) -> None:
        self.turns = sorted(turns, key=lambda turn: turn.start)
        speaking = {turn.voice for turn in self.turns}
        self.voices: list[str | None] = []
        for turn in self.turns:
            if turn.voice not in self.voices:
                self.voices.append(turn.voice)
        self.voices += [
            voice for voice in voices if voice in speaking and voice not in self.voices
        ]
        # A filler leaves the text, and a turn of nothing else is dropped, but the
        # word keeps a voice.
        self.owners = owners

    def records(self) -> list[dict[str, Any]]:
        return [turn.record() for turn in self.turns]

    def spans(self, voice: str | None) -> list[Span]:
        return [(turn.start, turn.end) for turn in self.turns if turn.voice == voice]


class UnvoicedLabelError(LookupError):
    def __init__(self, label: str) -> None:
        super().__init__(f"Label {label} has no voice in the conversation's speech")


def regrouped(
    grouping: Grouping,
    speech: dict[str, Any],
    corrections: list[dict[str, Any]],
) -> Transcript | None:
    """Transcript.regrouped: None when Hark would leave the transcript as it is."""
    if not grouping.exists:
        return None
    voice_of_label = {entry["label"]: voice for voice, entry in speech.items()}
    owned: list[Owned] = []
    for word, segment in grouping.placements:
        if segment.label not in voice_of_label:
            raise UnvoicedLabelError(segment.label)
        owned.append(Owned(word, segment, voice_of_label[segment.label]))
    owned = _corrected(owned, corrections)
    kept = [
        turn
        for turn in grouping.microphone_turns
        if not _is_discarded(turn, corrections)
    ]
    runs = [run for run in _settled(_runs(owned, [turn.start for turn in kept])) if run]
    system = _turns_of([(run[0].voice, [entry.word for entry in run]) for run in runs])
    microphone = grouping.microphone
    voices: list[str | None] = [microphone] if microphone not in {None, ""} else []
    for entry in owned:
        if entry.voice not in voices:
            voices.append(entry.voice)
    owners = {entry.word.index: entry.voice for run in runs for entry in run}
    return Transcript(kept + system, voices, owners)


# Diarization+Speech.swift, Voiceprints+Chunks.swift


def overlap(
    spans: Iterable[tuple[float, ...]], others: Iterable[tuple[float, ...]]
) -> float:
    left, right = sorted(spans), sorted(others)
    total, i, j = 0.0, 0, 0
    while i < len(left) and j < len(right):
        total += max(0.0, min(left[i][1], right[j][1]) - max(left[i][0], right[j][0]))
        if left[i][1] < right[j][1]:
            i += 1
        else:
            j += 1
    return total


def longest_stretch(
    spans: Iterable[tuple[float, ...]], pause: float = STRETCH_PAUSE
) -> float:
    merged: list[Span] = []
    for start, end in sorted(spans):
        if merged and start - merged[-1][1] <= pause:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return max((end - start for start, end in merged), default=0.0)


def voiceprints(
    chunks: dict[str, Any], transcript: Transcript, system_voices: Iterable[str]
) -> dict[str, Any]:
    """One voiceprint per system voice: the mean of chunks with 3s of its speech."""
    captured = next(
        (entry["chunks"] for entry in chunks["tracks"] if entry["track"] == "system"),
        [],
    )
    usable: list[tuple[tuple[float, ...], list[float]]] = []
    for chunk in captured:
        embedding = [store.float32(value) for value in chunk["embedding"]]
        if all(math.isfinite(value) for value in embedding):
            usable.append((tuple(chunk["span"]), embedding))
    by_voice: dict[str, list[store.Float32]] = {}
    for voice in system_voices:
        spans = transcript.spans(voice)
        heard = [
            embedding
            for span, embedding in usable
            if overlap([span], spans) >= MINIMUM_CHUNK_SPEECH
        ]
        if heard:
            sums = [sum(column) for column in zip(*heard, strict=False)]
            by_voice[voice] = [
                store.Float32(store.float32(total / len(heard))) for total in sums
            ]
    return {"byVoice": by_voice}
