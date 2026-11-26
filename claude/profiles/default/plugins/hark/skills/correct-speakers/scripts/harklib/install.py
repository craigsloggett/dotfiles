"""Putting a plan into the library, and taking it back out."""

import json
import re
import shutil
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from . import selftest, store

if TYPE_CHECKING:
    from .call import Call

CACHES = ("conversation", "transcript", "voiceprints")


class InstallError(Exception):
    pass


class HarkRunningError(InstallError):
    def __init__(self) -> None:
        super().__init__(
            "Hark is running. Ask the user to quit it first; it may be recording."
        )


class NoPlanError(InstallError):
    def __init__(self) -> None:
        super().__init__("There is no plan for this conversation; run plan first")


class EmptyPlanError(InstallError):
    def __init__(self) -> None:
        super().__init__("The plan changes nothing")


class StalePlanError(InstallError):
    def __init__(self) -> None:
        super().__init__(
            "The conversation changed since the plan was made; "
            "run evidence and plan again"
        )


class MissingLayerError(InstallError):
    def __init__(self, layer: str) -> None:
        super().__init__(
            f"{layer}.jsonl is missing, so Hark could not rebuild this conversation"
        )


class EncodingMismatchError(InstallError):
    def __init__(self, layer: str) -> None:
        super().__init__(
            f"The planned {layer}.jsonl does not encode the way Hark writes it"
        )


class NoVoiceprintsError(InstallError):
    def __init__(self) -> None:
        super().__init__(
            "This conversation already has no voiceprints; "
            "Hark rebuilds it at its next launch"
        )


class NoBackupError(InstallError):
    def __init__(self, name: str) -> None:
        super().__init__(f"No backup of {name} under {store.BACKUPS}")


def require_closed() -> None:
    """Refuse while Hark runs: it holds the library in memory and writes it back."""
    if store.SUPPORT == store.CONTAINER and store.hark_is_running():
        raise HarkRunningError


def backup(call: Call, *, with_people: bool = False) -> Path:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    directory = store.BACKUPS / call.name / stamp
    again = 1
    while directory.exists():
        again += 1
        directory = store.BACKUPS / call.name / f"{stamp}-{again}"
    directory.mkdir(parents=True)
    for layer in CACHES:
        if call.has(layer):
            shutil.copy2(call.path(layer), directory)
    if with_people and store.PEOPLE_FILE.exists():
        shutil.copy2(store.PEOPLE_FILE, directory)
    return directory


def latest_backup(call: Call) -> Path | None:
    root = store.BACKUPS / call.name
    names = [entry.name for entry in root.iterdir()] if root.is_dir() else []
    stamped = sorted(
        name for name in names if re.fullmatch(r"\d{8}-\d{6}(-\d+)?", name)
    )
    stamped = [
        name for name in stamped if (root / name / "conversation.jsonl").exists()
    ]
    return root / stamped[-1] if stamped else None


def _check_plan(call: Call, directory: Path, record: dict[str, Any]) -> None:
    if record["empty"]:
        raise EmptyPlanError
    if record["state"] != call.state():
        raise StalePlanError
    require_closed()
    for layer in ("chunks", "diarization", "recognition"):
        if not call.has(layer):
            raise MissingLayerError(layer)
    for layer in ("conversation", "transcript"):
        if not store.round_trips(directory / f"{layer}.jsonl", layer):
            raise EncodingMismatchError(layer)


def install(call: Call) -> Path:
    directory = Path(call.cache) / "plan"
    record_file = directory / "plan.json"
    if not record_file.exists():
        raise NoPlanError
    with record_file.open(encoding="utf-8") as handle:
        record = json.load(handle)
    _check_plan(call, directory, record)

    kept = backup(call, with_people=bool(record["addedPeople"]))
    if record["addedPeople"]:
        store.write(
            store.PEOPLE_FILE,
            "people",
            {"people": store.people() + record["addedPeople"]},
        )
    for layer in ("conversation", "transcript"):
        target = Path(call.path(layer))
        staged = target.with_name(target.name + ".planned")
        shutil.copyfile(directory / f"{layer}.jsonl", staged)
        staged.replace(target)
    # Hark rebuilds any conversation without voiceprints when it launches, so
    # removing them hands the transcript and the voiceprints back to Hark's code.
    if call.has("voiceprints"):
        Path(call.path("voiceprints")).unlink()
    record_file.unlink()
    return kept


def rebuild(call: Call) -> Path:
    require_closed()
    if not call.has("voiceprints"):
        raise NoVoiceprintsError
    kept = backup(call)
    Path(call.path("voiceprints")).unlink()
    return kept


def restore(call: Call) -> Path:
    kept = latest_backup(call)
    if kept is None:
        raise NoBackupError(call.name)
    require_closed()
    for layer in CACHES:
        saved = kept / f"{layer}.jsonl"
        if saved.exists():
            shutil.copy2(saved, call.path(layer))
        elif call.has(layer):
            Path(call.path(layer)).unlink()
    return kept


def check(call: Call) -> tuple[bool | None, str]:
    """Whether Hark has rebuilt the conversation, and whether the port predicted it."""
    if not call.has("voiceprints"):
        return (
            None,
            (
                "Hark has not rebuilt this conversation yet. "
                "Have the user open Hark, then check again."
            ),
        )
    result = selftest.replay(call.folder)
    if result.skipped is not None:
        return None, f"Nothing to compare: {result.skipped}"
    if result.transcript is result.voices is result.voiceprints is True:
        return (
            True,
            "Hark's rebuild matches the port: transcript, speakers, and voiceprints.",
        )
    compared = (
        ("transcript", result.transcript),
        ("speakers", result.voices),
        ("voiceprints", result.voiceprints),
    )
    parts = [name for name, matched in compared if matched is not True]
    detail = (
        f" First difference: {result.first_difference}"
        if result.first_difference is not None
        else ""
    )
    return (
        False,
        "Hark's rebuild differs from the port in its "
        + ", ".join(parts)
        + "."
        + detail,
    )
