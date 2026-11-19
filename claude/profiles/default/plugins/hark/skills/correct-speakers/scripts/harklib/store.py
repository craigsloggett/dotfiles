"""Hark's library on disk: where it lives, how its files are framed and encoded."""

import json
import os
import re
import struct
import subprocess
import tempfile
import time

CONTAINER = os.path.expanduser(
    "~/Library/Containers/com.craigsloggett.hark/Data/Library/Application Support"
)
SUPPORT = os.environ.get("HARK_SUPPORT", CONTAINER)
LIBRARY = os.path.join(SUPPORT, "Hark")
CONVERSATIONS = os.path.join(LIBRARY, "Conversations")
PEOPLE_FILE = os.path.join(LIBRARY, "people.jsonl")
BACKUPS = os.path.join(SUPPORT, "Hark Backups")
MODELS = os.path.join(CONTAINER, "FluidAudio", "Models", "speaker-diarization")
CACHE = os.environ.get("HARK_CACHE", os.path.expanduser("~/Library/Caches/hark-correct-speakers"))

# The schema each file must carry for this port to be valid (Hark's Storage/Schema.swift).
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


def float32(value):
    return struct.unpack("f", struct.pack("f", value))[0]


def _float32_text(value):
    for digits in range(1, 10):
        text = "%.*g" % (digits, value)
        if float32(float(text)) == value:
            return text
    return repr(value)


def encode(value):
    """JSONEncoder with .sortedKeys: compact, slashes escaped, whole doubles as integers."""
    if isinstance(value, dict):
        return "{" + ",".join(f"{encode(key)}:{encode(value[key])}" for key in sorted(value)) + "}"
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(encode(item) for item in value) + "]"
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False).replace("/", "\\/")
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, Float32):
        return _float32_text(value)
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() and abs(value) < 1e15 else repr(value)
    raise TypeError(type(value))


class SchemaMismatch(Exception):
    pass


def path_of(folder, layer):
    return os.path.join(folder, f"{layer}.jsonl")


def read(file, layer):
    """The value under a file's schema line, refusing a schema this port was not checked against."""
    with open(file, encoding="utf-8") as handle:
        header, body = handle.read().split("\n", 1)
    found = json.loads(header)["schema"]
    if found != SCHEMAS[layer]:
        raise SchemaMismatch(f"{file} is schema {found}, this skill reads schema {SCHEMAS[layer]}")
    return json.loads(body)


def text_of(layer, value):
    return json.dumps({"schema": SCHEMAS[layer]}, separators=(",", ":")) + "\n" + encode(value) + "\n"


def write(file, layer, value):
    directory = os.path.dirname(file)
    descriptor, temporary = tempfile.mkstemp(dir=directory, prefix=".hark-")
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        handle.write(text_of(layer, value))
    os.replace(temporary, file)


def as_voiceprints(value):
    return {"byVoice": {voice: [Float32(float32(x)) for x in print_] for voice, print_ in value["byVoice"].items()}}


def round_trips(file, layer):
    with open(file, encoding="utf-8") as handle:
        raw = handle.read()
    value = read(file, layer)
    if layer == "voiceprints":
        value = as_voiceprints(value)
    return text_of(layer, value) == raw


def hark_is_running():
    return subprocess.run(["pgrep", "-x", "Hark"], capture_output=True).returncode == 0


def folders():
    if not os.path.isdir(CONVERSATIONS):
        return []
    return sorted(
        name
        for name in os.listdir(CONVERSATIONS)
        if not name.startswith(".") and os.path.isdir(os.path.join(CONVERSATIONS, name))
    )


def folder_matching(query):
    """The one conversation a query names: a folder name, an id prefix, or a start time such as 08:00.

    A time alone means today's conversation, else the latest one that started then.
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
        raise LookupError(f"No conversation matches {query!r}")
    raise LookupError(f"{query!r} matches {len(matches)} conversations: " + ", ".join(matches[-6:]))


def people():
    if not os.path.exists(PEOPLE_FILE):
        return []
    return read(PEOPLE_FILE, "people")["people"]
