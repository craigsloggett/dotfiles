"""Speaker embeddings from Hark's cached model, for spans its diarizer did not embed."""

import hashlib
import json
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from . import regroup, store

if TYPE_CHECKING:
    from .call import Call

SOURCE = Path(__file__).resolve().parent.parent / "embed.swift"
WINDOW = 10.0
PAD = 0.04


class EmbedError(Exception):
    pass


class SwiftcMissingError(EmbedError):
    def __init__(self) -> None:
        super().__init__("swiftc is not on PATH; install the Xcode command line tools")


class SwiftcFailedError(EmbedError):
    def __init__(self, stderr: str) -> None:
        super().__init__("swiftc failed:\n" + stderr[-2000:])


class MissingInputError(EmbedError):
    def __init__(self, needed: Path) -> None:
        super().__init__(f"{needed} does not exist")


class EmbedFailedError(EmbedError):
    def __init__(self, stderr: str) -> None:
        super().__init__("embed failed: " + stderr[-2000:])


def tool() -> Path:
    """The compiled embedder, rebuilt whenever its source changes."""
    version = hashlib.sha256(SOURCE.read_bytes()).hexdigest()[:12]
    binary = store.CACHE / "bin" / f"embed-{version}"
    if binary.exists():
        return binary
    if shutil.which("swiftc") is None:
        raise SwiftcMissingError
    binary.parent.mkdir(parents=True, exist_ok=True)
    built = subprocess.run(
        ["swiftc", "-O", "-swift-version", "6", SOURCE, "-o", binary],
        capture_output=True,
        text=True,
        check=False,
    )
    if built.returncode != 0:
        raise SwiftcFailedError(built.stderr)
    return binary


def request_of(words: Sequence[regroup.Word], duration: float) -> dict[str, Any]:
    """A ten-second window centred on the words, hearing only the frames inside them."""
    start, end = words[0].start, words[-1].end
    window = max(0.0, min((start + end) / 2 - WINDOW / 2, duration - WINDOW))
    mask = [[round(word.start - PAD, 3), round(word.end + PAD, 3)] for word in words]
    return {"windowStart": round(window, 3), "mask": mask}


def _key(request: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()[:20]


def _compute(
    call: Call, missing: dict[str, dict[str, Any]], cached: dict[str, list[float]]
) -> None:
    """Run the embedder on the missing requests and add its answers to the cache."""
    for needed in (call.audio, store.MODELS / "Embedding.mlmodelc"):
        if not needed.exists():
            raise MissingInputError(needed)
    asked = call.cache / "requests.json"
    answered = call.cache / "answers.json"
    with asked.open("w", encoding="utf-8") as handle:
        json.dump([{"id": key, **request} for key, request in missing.items()], handle)
    ran = subprocess.run(
        [tool(), call.audio, store.MODELS, asked, answered],
        capture_output=True,
        text=True,
        check=False,
    )
    if ran.returncode != 0:
        raise EmbedFailedError(ran.stderr)
    with answered.open(encoding="utf-8") as handle:
        for entry in json.load(handle):
            cached[entry["id"]] = entry["embedding"]
    with (call.cache / "embeddings.json").open("w", encoding="utf-8") as handle:
        json.dump(cached, handle)
    asked.unlink()
    answered.unlink()


def embeddings(
    call: Call, requests: dict[str, dict[str, Any]]
) -> dict[str, list[float]]:
    """Unit-length embeddings by request id, computing only those not yet cached."""
    cache_file = call.cache / "embeddings.json"
    cached: dict[str, list[float]] = {}
    if cache_file.exists():
        with cache_file.open(encoding="utf-8") as handle:
            cached = cast("dict[str, list[float]]", json.load(handle))
    keys = {name: _key(request) for name, request in requests.items()}
    missing = {key: requests[name] for name, key in keys.items() if key not in cached}
    if missing:
        _compute(call, missing, cached)
    return {name: unit(cached[key]) for name, key in keys.items()}


def dot(left: Sequence[float], right: Sequence[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=False))


def unit(vector: Sequence[float]) -> list[float]:
    norm = dot(vector, vector) ** 0.5
    return [value / norm for value in vector] if norm > 0 else list(vector)


def mean(vectors: Sequence[Sequence[float]]) -> list[float]:
    return [sum(column) / len(vectors) for column in zip(*vectors, strict=False)]
