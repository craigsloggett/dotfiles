"""Putting a plan into the library, and taking it back out."""

import json
import os
import re
import shutil
import time

from . import selftest, store

CACHES = ("conversation", "transcript", "voiceprints")


class InstallError(Exception):
    pass


def require_closed():
    """Hark holds the library in memory and writes it back, so nothing here is safe while it runs."""
    if store.SUPPORT == store.CONTAINER and store.hark_is_running():
        raise InstallError("Hark is running. Ask the user to quit it first; it may be recording.")


def backup(call, with_people=False):
    stamp = time.strftime("%Y%m%d-%H%M%S")
    directory = os.path.join(store.BACKUPS, call.name, stamp)
    again = 1
    while os.path.exists(directory):
        again += 1
        directory = os.path.join(store.BACKUPS, call.name, f"{stamp}-{again}")
    os.makedirs(directory)
    for layer in CACHES:
        if call.has(layer):
            shutil.copy2(call.path(layer), directory)
    if with_people and os.path.exists(store.PEOPLE_FILE):
        shutil.copy2(store.PEOPLE_FILE, directory)
    return directory


def latest_backup(call):
    root = os.path.join(store.BACKUPS, call.name)
    names = os.listdir(root) if os.path.isdir(root) else []
    stamped = sorted(name for name in names if re.fullmatch(r"\d{8}-\d{6}(-\d+)?", name))
    stamped = [name for name in stamped if os.path.exists(os.path.join(root, name, "conversation.jsonl"))]
    return os.path.join(root, stamped[-1]) if stamped else None


def install(call):
    directory = os.path.join(call.cache, "plan")
    record_file = os.path.join(directory, "plan.json")
    if not os.path.exists(record_file):
        raise InstallError("There is no plan for this conversation; run plan first")
    with open(record_file, encoding="utf-8") as handle:
        record = json.load(handle)
    if record["empty"]:
        raise InstallError("The plan changes nothing")
    if record["state"] != call.state():
        raise InstallError("The conversation changed since the plan was made; run evidence and plan again")
    require_closed()
    for layer in ("chunks", "diarization", "recognition"):
        if not call.has(layer):
            raise InstallError(f"{layer}.jsonl is missing, so Hark could not rebuild this conversation")
    for layer in ("conversation", "transcript"):
        if not store.round_trips(os.path.join(directory, f"{layer}.jsonl"), layer):
            raise InstallError(f"The planned {layer}.jsonl does not encode the way Hark writes it")

    kept = backup(call, with_people=bool(record["addedPeople"]))
    if record["addedPeople"]:
        store.write(store.PEOPLE_FILE, "people", {"people": store.people() + record["addedPeople"]})
    for layer in ("conversation", "transcript"):
        staged = call.path(layer) + ".planned"
        shutil.copyfile(os.path.join(directory, f"{layer}.jsonl"), staged)
        os.replace(staged, call.path(layer))
    # Hark rebuilds any conversation without voiceprints when it launches, so removing them hands
    # the transcript and the voiceprints back to Hark's own code.
    if call.has("voiceprints"):
        os.remove(call.path("voiceprints"))
    os.remove(record_file)
    return kept


def rebuild(call):
    require_closed()
    if not call.has("voiceprints"):
        raise InstallError("This conversation already has no voiceprints; Hark rebuilds it at its next launch")
    kept = backup(call)
    os.remove(call.path("voiceprints"))
    return kept


def restore(call):
    kept = latest_backup(call)
    if kept is None:
        raise InstallError(f"No backup of {call.name} under {store.BACKUPS}")
    require_closed()
    for layer in CACHES:
        saved = os.path.join(kept, f"{layer}.jsonl")
        if os.path.exists(saved):
            shutil.copy2(saved, call.path(layer))
        elif call.has(layer):
            os.remove(call.path(layer))
    return kept


def check(call):
    """Whether Hark has rebuilt the conversation, and whether the port predicted that rebuild exactly."""
    if not call.has("voiceprints"):
        return None, "Hark has not rebuilt this conversation yet. Have the user open Hark, then check again."
    result = selftest.replay(call.folder)
    if result.skipped:
        return None, f"Nothing to compare: {result.skipped}"
    if result.transcript and result.voices and result.voiceprints:
        return True, "Hark's rebuild matches the port: transcript, speakers, and voiceprints."
    compared = (("transcript", result.transcript), ("speakers", result.voices), ("voiceprints", result.voiceprints))
    parts = [name for name, matched in compared if not matched]
    detail = f" First difference: {result.first_difference}" if result.first_difference else ""
    return False, "Hark's rebuild differs from the port in its " + ", ".join(parts) + "." + detail
