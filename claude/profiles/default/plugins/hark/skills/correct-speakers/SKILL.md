---
name: correct-speakers
description: >-
  Use when the user wants the speakers of a Hark conversation fixed: an unnamed
  or extra speaker, turns given to the wrong person, several people merged into
  one voice, or a voiceprint to clean up.
arguments:
  - conversation
allowed-tools:
  - Bash(${CLAUDE_SKILL_DIR}/scripts/hark.py list *)
  - Bash(${CLAUDE_SKILL_DIR}/scripts/hark.py show *)
  - Bash(${CLAUDE_SKILL_DIR}/scripts/hark.py evidence *)
  - Bash(${CLAUDE_SKILL_DIR}/scripts/hark.py plan *)
  - Bash(${CLAUDE_SKILL_DIR}/scripts/hark.py check *)
  - Bash(${CLAUDE_SKILL_DIR}/scripts/hark.py selftest)
---

## Correct Speakers

`${CLAUDE_SKILL_DIR}/scripts/hark.py` does everything that doesn't need
judgment. It scores each line of remote speech against every speaker, proposes
the moves the scores settle, writes them as Hark's own corrections, and proves
that Hark's rebuild of those corrections gives every word its intended speaker.
Your part is the lines it cannot settle, and what the user tells you. Run it by
that path; `hark` below is short for it.

Recent conversations:

!`${CLAUDE_SKILL_DIR}/scripts/hark.py list 8`

### Workflow

`<conversation>` is `$conversation`: a start time (`08:00` means today's), an id
prefix, or a folder name. Blank means the one the user described.

1. Read the transcript with `hark show <conversation>`. Note who is addressed by
   name, who introduces themselves, and which questions get answered.
2. Gather the evidence with `hark evidence <conversation>`. The first run embeds
   the audio, about a minute for a 40-minute conversation.
3. Decide every `Undecided` and `Possible` line, and read the `low` proposals
   against their context. Write your decisions to a JSON file shaped like
   `examples/overrides.json`.
4. Plan with `hark plan <conversation> --overrides <file>`. Read `Turns that
   change` as the user will see them, then fix the file and plan again until
   they are right. Planning doesn't write to the library.
5. For a conversation from before today, show the user the plan and wait for
   their approval.
6. Check `pgrep -x Hark`. If Hark is running, ask the user to quit it, because
   it may be recording. Then run `hark install <conversation>`.
7. Tell the user who each unnamed speaker turned out to be and what moved. List
   every line under `Accepted on weaker evidence` and every one you decided,
   with its timestamp, as guesses they can fix in Hark. Ask them to open Hark.
8. Once Hark is open, run `hark check <conversation>`.

### Overrides

| Key          | Holds                                                          |
| ------------ | -------------------------------------------------------------- |
| `moves`      | Line ids, or `from` and `to` in seconds, and their `speaker`   |
| `keep`       | Ids of proposals to reject                                     |
| `name`       | A label and the person it is, or `null` to refuse a suggestion |
| `add_people` | Names missing from Hark's people, spelled by the user          |

A `speaker` is a person's name, a label such as `S3`, or `new:<tag>` for someone
nobody can name yet. A person with no voice in the conversation gets one.

### Judging Lines

- What the user says about who spoke outranks every score.
- A `CATCH-ALL` voice is not a person. It holds the first second or two of
  whoever takes the floor, trailing phrases, and replies spoken over someone,
  and that audio sounds the same whoever said it. Place each of its lines by
  what it continues into, what it answers, and who it addresses.
- Scores under 0.35 for everyone mean the audio cannot tell you who spoke. Do
  not read meaning into which low score is highest.
- A reply belongs to the person addressed or to whoever asked the question, not
  to the speaker of the turn it was folded into.
- A burst of greetings or goodbyes is several people. Split it where the words
  let you and leave the rest; never give the whole burst to one speaker.
- Two people who sound alike score alike, so a `MERGED` voice can hide a third
  person the scores never separate.
  Look for the name being addressed.
- The recognizer spells names by ear. Ask the user for the
  spelling before using `add_people`, and never invent a person.
- Leave a line where it is when nothing settles it, and tell the user you did.

### Rules

- Change a conversation only through `hark install`. A hand-written
  `transcript.jsonl` or `voiceprints.jsonl` survives until the user's next edit
  in Hark. That edit rebuilds both from the corrections and can move words the
  hand edit never touched.
- Hark rebuilds any conversation without a `voiceprints.jsonl` when it
  launches. `install` removes the file on purpose, so the transcript and
  voiceprints the user sees are Hark's own.
- `install` appends its corrections after the user's own and leaves theirs in
  order.
- A plan is tied to the files it read. After the user edits anything in Hark,
  gather the evidence again; `plan` and `install` refuse stale work.
- `hark check` failing means Hark's rules changed since this skill was checked
  against them. Stop planning, run `hark selftest`, and follow
  `reference/hark-rebuild.md`.
- `hark restore <conversation>` puts back the files the last install or rebuild
  replaced. `hark rebuild <conversation>` hands a conversation back to Hark's
  own rebuild without changing its corrections.
