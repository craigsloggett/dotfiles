"""Speaker embeddings from Hark's own cached model, for spans Hark's diarizer never embedded."""

import hashlib
import json
import os
import shutil
import subprocess

from . import store

SOURCE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "embed.swift")
WINDOW = 10.0
PAD = 0.04


class EmbedError(Exception):
    pass


def tool():
    """The compiled embedder, rebuilt whenever its source changes."""
    with open(SOURCE, "rb") as handle:
        version = hashlib.sha256(handle.read()).hexdigest()[:12]
    binary = os.path.join(store.CACHE, "bin", f"embed-{version}")
    if os.path.exists(binary):
        return binary
    if shutil.which("swiftc") is None:
        raise EmbedError("swiftc is not on PATH; install the Xcode command line tools")
    os.makedirs(os.path.dirname(binary), exist_ok=True)
    built = subprocess.run(
        ["swiftc", "-O", "-swift-version", "6", SOURCE, "-o", binary], capture_output=True, text=True
    )
    if built.returncode != 0:
        raise EmbedError("swiftc failed:\n" + built.stderr[-2000:])
    return binary


def request_of(words, duration):
    """A ten-second window centred on the words, hearing only the frames inside them."""
    start, end = words[0].start, words[-1].end
    window = max(0.0, min((start + end) / 2 - WINDOW / 2, duration - WINDOW))
    mask = [[round(word.start - PAD, 3), round(word.end + PAD, 3)] for word in words]
    return {"windowStart": round(window, 3), "mask": mask}


def _key(request):
    return hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()[:20]


def embeddings(call, requests):
    """Unit-length embeddings by request id, computing only the ones this call has not cached."""
    cache_file = os.path.join(call.cache, "embeddings.json")
    cached = {}
    if os.path.exists(cache_file):
        with open(cache_file, encoding="utf-8") as handle:
            cached = json.load(handle)
    keys = {name: _key(request) for name, request in requests.items()}
    missing = {key: requests[name] for name, key in keys.items() if key not in cached}
    if missing:
        for needed in (call.audio, os.path.join(store.MODELS, "Embedding.mlmodelc")):
            if not os.path.exists(needed):
                raise EmbedError(f"{needed} does not exist")
        asked = os.path.join(call.cache, "requests.json")
        answered = os.path.join(call.cache, "answers.json")
        with open(asked, "w", encoding="utf-8") as handle:
            json.dump([{"id": key, **request} for key, request in missing.items()], handle)
        ran = subprocess.run([tool(), call.audio, store.MODELS, asked, answered], capture_output=True, text=True)
        if ran.returncode != 0:
            raise EmbedError("embed failed: " + ran.stderr[-2000:])
        with open(answered, encoding="utf-8") as handle:
            for entry in json.load(handle):
                cached[entry["id"]] = entry["embedding"]
        with open(cache_file, "w", encoding="utf-8") as handle:
            json.dump(cached, handle)
        os.remove(asked)
        os.remove(answered)
    return {name: unit(cached[key]) for name, key in keys.items()}


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def unit(vector):
    norm = dot(vector, vector) ** 0.5
    return [value / norm for value in vector] if norm > 0 else list(vector)


def mean(vectors):
    return [sum(column) / len(vectors) for column in zip(*vectors)]
