"""Hark's library on disk: where it lives, how its files are framed and encoded."""

import json
import os
import re
import struct
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

CONTAINER = (
    Path.home()
    / "Library/Containers/com.craigsloggett.hark/Data/Library/Application Support"
)
SUPPORT = Path(os.environ.get("HARK_SUPPORT", CONTAINER))
LIBRARY = SUPPORT / "Hark"
CONVERSATIONS = LIBRARY / "Conversations"
PEOPLE_FILE = LIBRARY / "people.jsonl"
BACKUPS = SUPPORT / "Hark Backups"
MODELS = CONTAINER / "FluidAudio" / "Models" / "speaker-diarization"
CACHE = Path(
    os.environ.get("HARK_CACHE", Path.home() / "Library/Caches/hark-correct-speakers")
)

# The schema each file must carry for this port to be valid (Hark's
# Storage/Schema.swift).
SCHEMAS = {
    "conversation": 4,
    "transcript": 10,
    "recognition": 2,
    "diarization": 2,
    "chunks": 3,
    "voiceprints": 3,
    "people": 1,
}


class Float32(float):
    """A double holding a Float value, encoded the way Swift prints a Float."""

    __slots__ = ()


def float32(value: float) -> float:
    return struct.unpack("f", struct.pack("f", value))[0]


def _float32_text(value: float) -> str:
    for digits in range(1, 10):
        text = f"{value:.{digits}g}"
        if float32(float(text)) == value:
            return text
    return repr(value)


def encode(value: object) -> str:
    """JSONEncoder with .sortedKeys: compact, escaped slashes, whole doubles as ints."""
    if isinstance(value, dict):
        return (
            "{"
            + ",".join(f"{encode(key)}:{encode(value[key])}" for key in sorted(value))
            + "}"
        )
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(encode(item) for item in value) + "]"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False).replace("/", "\\/")
    return _encode_scalar(value)


def _encode_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, Float32):
        return _float32_text(value)
    if isinstance(value, float):
        return (
            str(int(value)) if value.is_integer() and abs(value) < 1e15 else repr(value)
        )
    raise TypeError(type(value))


class SchemaMismatchError(Exception):
    def __init__(self, file: Path, found: int, expected: int) -> None:
        super().__init__(
            f"{file} is schema {found}, this skill reads schema {expected}"
        )


class NoConversationError(LookupError):
    def __init__(self, query: str) -> None:
        super().__init__(f"No conversation matches {query!r}")


class AmbiguousConversationError(LookupError):
    def __init__(self, query: str, matches: list[str]) -> None:
        super().__init__(
            f"{query!r} matches {len(matches)} conversations: "
            + ", ".join(matches[-6:])
        )


def path_of(folder: Path, layer: str) -> Path:
    return folder / f"{layer}.jsonl"


def read(file: Path, layer: str) -> dict[str, Any]:
    """The value under a file's schema line, refusing a schema not checked against."""
    header, body = file.read_text(encoding="utf-8").split("\n", 1)
    found = json.loads(header)["schema"]
    if found != SCHEMAS[layer]:
        raise SchemaMismatchError(file, found, SCHEMAS[layer])
    return json.loads(body)


def text_of(layer: str, value: object) -> str:
    return (
        json.dumps({"schema": SCHEMAS[layer]}, separators=(",", ":"))
        + "\n"
        + encode(value)
        + "\n"
    )


def write(file: Path, layer: str, value: object) -> None:
    descriptor, temporary = tempfile.mkstemp(dir=file.parent, prefix=".hark-")
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(text_of(layer, value))
    Path(temporary).replace(file)


def as_voiceprints(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "byVoice": {
            voice: [Float32(float32(x)) for x in print_]
            for voice, print_ in value["byVoice"].items()
        }
    }


def round_trips(file: Path, layer: str) -> bool:
    raw = file.read_text(encoding="utf-8")
    value = read(file, layer)
    if layer == "voiceprints":
        value = as_voiceprints(value)
    return text_of(layer, value) == raw


def hark_is_running() -> bool:
    found = subprocess.run(["pgrep", "-x", "Hark"], capture_output=True, check=False)
    return found.returncode == 0


def folders() -> list[str]:
    if not CONVERSATIONS.is_dir():
        return []
    return sorted(
        entry.name
        for entry in CONVERSATIONS.iterdir()
        if not entry.name.startswith(".") and entry.is_dir()
    )


def folder_matching(query: str) -> str:
    """The one conversation a query names: a folder name, id prefix, or start time.

    A start time is written such as 08:00. A time alone means today's
    conversation, else the latest one that started then.
    """
    names = folders()
    if query in names:
        return query
    by_id = [name for name in names if name.split(" ")[-1].startswith(query.upper())]
    if len(by_id) == 1:
        return by_id[0]
    wanted = query.replace(":", ".")
    clock = re.fullmatch(r"(\d{1,2})\.(\d{2})", wanted)
    if clock:
        stamp = f"{int(clock.group(1)):02d}.{clock.group(2)}"
        at = [name for name in names if name[11:16] == stamp]
        today = [name for name in at if name.startswith(time.strftime("%Y-%m-%d"))]
        matches = today or at[-1:]
    else:
        matches = [name for name in names if wanted in name]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise NoConversationError(query)
    raise AmbiguousConversationError(query, matches)


def people() -> list[dict[str, Any]]:
    if not PEOPLE_FILE.exists():
        return []
    return read(PEOPLE_FILE, "people")["people"]
