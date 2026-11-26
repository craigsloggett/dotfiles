#!/usr/bin/env python3
"""Correct a Hark conversation's speakers. Run with no arguments for the commands."""

import argparse
import json
import sys
import time
from pathlib import Path

# This lives in a dotfiles checkout, which should not collect bytecode.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

from harklib import embed, evidence, install, plan, regroup, selftest, store  # noqa: E402
from harklib.call import Call, clock  # noqa: E402


class UnknownOverridesError(plan.PlanError):
    def __init__(self, unknown: set[str]) -> None:
        super().__init__(
            f"Overrides has keys this does not know: {', '.join(sorted(unknown))}"
        )


def call_named(query: str) -> Call:
    return Call(store.folder_matching(query))


def list_conversations(arguments: argparse.Namespace) -> None:
    names = store.folders()[-arguments.count :]
    people = {person["id"]: person["name"] for person in store.people()}
    for name in names:
        folder = store.CONVERSATIONS / name
        try:
            conversation = store.read(
                store.path_of(folder, "conversation"), "conversation"
            )
        except (OSError, ValueError, store.SchemaMismatchError) as failure:
            print(f"{name}  unreadable: {failure}")
            continue
        system = [
            voice["id"]
            for voice in conversation["voices"]
            if voice["track"] == "system"
        ]
        named = [
            people.get(conversation["attributions"].get(voice)) for voice in system
        ]
        unnamed = sum(1 for person in named if person is None)
        notes = [f"{len(system)} speakers"]
        if unnamed:
            notes.append(f"{unnamed} unnamed")
        if conversation["corrections"]:
            notes.append(f"{len(conversation['corrections'])} corrections")
        if not store.path_of(folder, "voiceprints").exists():
            notes.append("awaiting Hark's rebuild")
        title = next(iter(conversation["title"].values()))
        duration = clock(conversation["duration"])
        print(f"{name}  {duration:>8}  {title[:28]:<28}  {', '.join(notes)}")
        print(f"{'':30}{', '.join(person for person in named if person)}")


def show(arguments: argparse.Namespace) -> None:
    call = call_named(arguments.conversation)
    transcript = call.rebuilt()
    dropped = {segment.label for segment in call.grouping.segments} - {
        segment.label for segment in regroup.substantial(call.grouping.segments)
    }
    corrections = len(call.conversation["corrections"])
    duration = clock(call.conversation["duration"])
    print(f"{call.name}  {duration}  {corrections} corrections")
    hinted = call.diarization.get("hintedSpeakers")
    if hinted is not None:
        print(f"The diarizer was told to find {hinted} speaker(s).")
    if dropped:
        floor = f"{regroup.MINIMUM_LABEL_SPEECH:g}s"
        labels = ", ".join(sorted(dropped))
        print(f"Labels under {floor} of speech, which own no words: {labels}")
    for voice in transcript.voices:
        if voice is None or voice == call.microphone:
            continue
        speech = sum(end - start for start, end in transcript.spans(voice))
        label = call.labels.get(voice, "new")
        print(f"  {label:<4} {voice[:8]}  {call.speaker(voice):<28} {speech:6.0f}s")
    print()
    for turn in transcript.turns:
        print(f"{clock(turn.start):>7}  {call.speaker(turn.voice)}: {turn.text}")


def gather_evidence(arguments: argparse.Namespace) -> None:
    call = call_named(arguments.conversation)
    started = time.time()
    found = evidence.Evidence(call)
    found.save()
    print(found.report())
    elapsed = time.time() - started
    print(f"\nGathered in {elapsed:.0f}s. Next: plan {call.name.split(' ')[-1]}")


def make_plan(arguments: argparse.Namespace) -> None:
    call = call_named(arguments.conversation)
    overrides = {}
    if arguments.overrides:
        with Path(arguments.overrides).open(encoding="utf-8") as handle:
            overrides = json.load(handle)
    unknown = set(overrides) - {"moves", "keep", "name", "add_people"}
    if unknown:
        raise UnknownOverridesError(unknown)
    planned = plan.Plan(call, plan.load_evidence(call), overrides)
    planned.save()
    print(planned.summary())
    if not planned.is_empty:
        print(f"\nNext: install {call.name.split(' ')[-1]} (Hark must be closed)")


def install_plan(arguments: argparse.Namespace) -> None:
    call = call_named(arguments.conversation)
    kept = install.install(call)
    print(f"Installed. The files it replaced are in {kept}")
    print(
        "Hark rebuilds this conversation's transcript and voiceprints"
        " when it next launches."
    )
    print(f"After the user has opened Hark: check {call.name.split(' ')[-1]}")


def check(arguments: argparse.Namespace) -> None:
    call = call_named(arguments.conversation)
    matched, message = install.check(call)
    print(message)
    if matched is False:
        print(
            "Hark's rules have moved since this skill was checked against them."
            " Run selftest, then"
        )
        print(
            "compare harklib/regroup.py with macOS/Sources/Analysis"
            " in Hark's source before planning again."
        )
        sys.exit(1)


def restore(arguments: argparse.Namespace) -> None:
    call = call_named(arguments.conversation)
    print(f"Restored from {install.restore(call)}")


def rebuild(arguments: argparse.Namespace) -> None:
    call = call_named(arguments.conversation)
    kept = install.rebuild(call)
    print(
        f"Voiceprints set aside in {kept}."
        " Hark rebuilds this conversation when it next launches."
    )


def run_selftest(_: argparse.Namespace) -> None:
    started = time.time()
    matched = 0
    differing: list[selftest.Replay] = []
    waiting: list[str] = []
    skipped: list[str] = []
    for name in store.folders():
        folder = store.CONVERSATIONS / name
        try:
            result = selftest.replay(folder)
        except (OSError, ValueError, LookupError, store.SchemaMismatchError) as failure:
            skipped.append(f"{name}: {failure}")
            continue
        if result.skipped is not None:
            skipped.append(f"{name}: {result.skipped}")
        elif result.voiceprints is None:
            waiting.append(name)
        elif all(
            same is True
            for same in (result.transcript, result.voices, result.voiceprints)
        ):
            matched += 1
        else:
            differing.append(result)
    elapsed = time.time() - started
    print(
        f"{matched} conversations rebuild exactly as Hark wrote them ({elapsed:.0f}s)."
    )
    for name in waiting:
        print(f"  awaiting Hark's rebuild: {name}")
    for line in skipped:
        print(f"  skipped: {line}")
    for result in differing:
        compared = (
            ("transcript", result.transcript),
            ("speakers", result.voices),
            ("voiceprints", result.voiceprints),
        )
        parts = [part for part, same in compared if same is not True]
        difference = result.first_difference or ""
        print(f"  DIFFERS in {', '.join(parts)}: {result.folder}  {difference}")
    if differing:
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(prog="hark", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser(
        "list", help="recent conversations and their speakers"
    )
    listing.add_argument("count", nargs="?", type=int, default=12)
    listing.set_defaults(run=list_conversations)
    for name, run, text in (
        ("show", show, "the transcript as Hark rebuilds it now"),
        (
            "evidence",
            gather_evidence,
            "who each line sounds like, and the moves that need no judgment",
        ),
        ("install", install_plan, "write the plan into the library (Hark closed)"),
        ("check", check, "after Hark relaunches: did it rebuild as predicted"),
        ("restore", restore, "put back the files the last install or rebuild replaced"),
        (
            "rebuild",
            rebuild,
            "drop the voiceprints so Hark rebuilds the conversation itself",
        ),
    ):
        command = commands.add_parser(name, help=text)
        command.add_argument(
            "conversation", help="folder name, id prefix, or start time such as 08:00"
        )
        command.set_defaults(run=run)
    planning = commands.add_parser(
        "plan", help="turn evidence and overrides into corrections, without installing"
    )
    planning.add_argument("conversation")
    planning.add_argument(
        "--overrides", help="JSON file of moves, keep, name, add_people"
    )
    planning.set_defaults(run=make_plan)
    commands.add_parser(
        "selftest", help="replay the library through the port of Hark's rules"
    ).set_defaults(run=run_selftest)
    arguments = parser.parse_args()
    try:
        arguments.run(arguments)
    except (
        plan.PlanError,
        install.InstallError,
        embed.EmbedError,
        store.SchemaMismatchError,
        LookupError,
    ) as failure:
        print(f"hark: {failure}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
