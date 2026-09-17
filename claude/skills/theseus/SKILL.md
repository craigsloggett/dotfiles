---
name: theseus
description: Use when working on the hark Theseus rebuild (branch refactor/theseus), the whole-app ship-of-Theseus rewrite the user runs as a Swift and SwiftUI learning exercise, where every line is designed, explained, and reviewed before it lands.
---

## What this is

hark is being rebuilt whole, not just its UI, one capability at a time on the branch
`refactor/theseus`, with one draft PR (#248) and one commit per step. The rebuild took the app
over on 2026-08-23: the old surfaces are gone, `macOS/Sources/` is the rebuilt tree, and every
change since is designed against the ledger rather than against what the old app did.

The point is not to finish fast. The user is learning Swift and SwiftUI by understanding every
line that lands. Code you write that he cannot explain back is a failure even if it works.

## How to work

- **Design before code.** State the structural decision, the alternatives, and your
  recommendation. Wait for agreement. Do not write the change while proposing it.
- **One commit-sized step, then stop.** Small diffs he can review in full. If a step grows,
  split it and land the first half.
- **Teach as you go.** When a Swift or SwiftUI mechanism explains a choice (view identity,
  actor isolation, pattern matching, transitions), explain the mechanism, not just the fix.
- **Change nothing unasked.** No drive-by refactors, no "while I was in there".
- **Verify, never recall.** Check APIs against the SDK's `.swiftinterface`
  (`xcrun --sdk macosx --show-sdk-path`) or current docs. Apple's HIG pages are JS-rendered:
  fetch `developer.apple.com/tutorials/data/design/human-interface-guidelines/<page>.json`.
  Say "unverified" when you cannot confirm something.
- **Report honestly.** If a gate fails, a verdict was confounded, or you were wrong earlier,
  say so plainly and correct the record.

## Start of session

Read the ledger before proposing anything:
`~/.claude/projects/-Users-Craig-Developer-GitHub-craigsloggett-hark/memory/theseus-rebuild.md`

Its STATE OF THE REBUILD header owns direction and the plank queue; the chronological record
below it is decisions, traps, and evidence, where recency is not priority. The user sets the
queue at session start, so take direction from the header and his word, never from the tail's
most recent momentum. It carries every ratified decision, every deliberate non-change, and the
traps already paid for. Commit hashes in it drift with each rebase, so trust the prose over
the hashes. If the memory directory is absent (fresh machine or cloud session), say so and
rebuild context from `git log` and the draft PR instead of guessing.

## Gates

- `make format` then `make lint` must pass before every commit.
- `make analyze` (restored 2026-09-14, macOS only: a full build into a throwaway DerivedData
  plus `swiftlint analyze --strict`) runs the two analyzer rules, `unused_import` (the umbrella
  allowances in `.swiftlint.yml` say what Foundation, OSLog, and AVFoundation stand for) and
  `unused_declaration`. It runs in CI after Build on the macOS runner and locally on request,
  not inside `make lint`, which runs on Linux without a build. When a change reroutes
  **ownership** (who holds what), still grep for every symbol the removed code used and confirm
  each still has a caller, then run `make analyze` before the commit; that is how a dead
  property once survived three commits. The same gate applies when a declaration merely
  **leaves a file**: the move can strand that file's last framework name, and "constants
  moved, no ownership" let a dead `import Foundation` fail CI for three pushes on 2026-09-15.
  Periphery (installed here, 3.8.0) is an on-demand audit,
  not a gate, by his 2026-09-14 call: `periphery scan --project hark.xcodeproj --schemes Hark
  --clean-build --retain-codable-properties --retain-equatable-properties
  --retain-hashable-properties --retain-objc-accessible --retain-swift-ui-previews`; the clean
  build is load-bearing ([[periphery-stale-index-ghosts]]). Measured 2026-09-14: both tools
  catch an unused property, method, and type alike; the tree was clean by both.
- Build with the `build-logs` agent rather than in-session, so xcodebuild output stays out of
  context. Warnings are errors; expect zero.
- **Zero tests during Theseus**, by the user's explicit decision. He will write them in a
  focused session once behavior and interfaces settle. Do not add test files.
- SourceKit diagnostics in-editor are usually stale-index noise. The build is the truth.

## Commits

Message style, which the user is happy with and wants kept:

- Conventional prefix, capitalized first word after it: `feat: Add X`, never `feat: add X`.
- Imperative subject, under 70 characters, no trailing period.
- **Subject only, no body.** Squash-merge concatenates branch commit messages into main's
  history. The why goes in the PR description.
- The subject must describe what the commit contains *now*. If folding a change alters what a
  commit does, reword it.

History workflow:

- Refinements to a step **fold into the commit that introduced it**, rather than stacking a
  fix commit: `git commit --fixup=<sha>` then
  `GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <base>`. If the target is the tip,
  `git commit --amend` is simpler.
- Verify every rewrite: `git range-diff <old-range> <new-range>` (untouched commits show `=`),
  a byte-compare of the final tree against the pre-rebase tip, and a build of each rewritten
  commit's tree.
- Push with `git push --force-with-lease`.
- Every commit is GPG-signed. Verify with `%G?` = `G`. Never probe whether the key is
  unlocked; probing reports false negatives. If signing fails, ask the user to unlock and hand
  the session back. Never disable the check.
- No AI or Claude attribution anywhere, in commits, PRs, comments, or code.

## Layout and naming

The takeover landed 2026-08-23: there is no Theseus folder, window, or scene. `macOS/Sources/`
holds the entry point `HarkApp.swift` (the composition root, above every capability), the
Foundation-only helpers consumed by three or more capabilities (`Logger+Hark.swift`,
`Duration+TimeInterval.swift`), and six umbrellas in a ring order: `Models/` (Foundation only;
value types, IDs, enums), `Analysis/` (Foundation and Accelerate; the pure computations over
Models and every calibrated constant, the future test target: `Regrouping/`, `Text/`,
`Identity/`, `Diarization/`, `Importing/`), `Storage/` and `Engine/` (siblings; both import
Models and Analysis, neither the other; Engine is one folder per mechanism that touches the
world, `Audio/`, `Diarization/`, `Importing/`, `Playback/`, `Recording/`, `Transcription/`, and
its passes and sessions take file URLs and values, never a folder), `App/` (what touches the app
object plus the orchestrators that drive the engine over the store: `Orchestration/` with
Diarizer, Transcriber, and Importer, `Transport/`, `Lifecycle/`, `Notifications/`), and `UI/`.
Anything narrower than three capabilities lives in its consumer's folder. A log line carries the
category of the stage it describes, wherever the speaker lives. The five top-level concepts
were ratified 2026-09-10 for Xcode navigation and lint-checkable boundaries; Analysis was added
2026-09-14 when the Storage-Engine cycle was measured (the ledger's "THE ANALYSIS LAYER"
bullet); umbrellas nest whole capability folders, and the residence rules below still decide
where a file goes inside them. A file belongs in Analysis when it imports only Foundation (and
Accelerate) and names only Models: nothing there knows where its inputs came from, callers
fetch, Analysis computes, callers persist. If a function there seems to need a Storage, Engine,
or App type, either it is not pure and belongs in Engine or App, or the value arrives as a
parameter. Packages are not split during Theseus; the folder boundary is the package boundary
later.

Boundaries, enforced by seventeen custom rules in `.swiftlint.yml` that `make lint` runs with
`--strict`. The import rules take the negated form `^import (?!Foundation$)`, which names what
a folder may import and rejects everything else: `Models/` imports Foundation alone; `Analysis/`
Foundation and Accelerate alone; `UI/Presentation/` Foundation and Observation alone (Pipeline
must be Observable to ride the environment; Presentation decides what to show and never draws);
SwiftUI only in `UI/` and `HarkApp.swift`; AppKit only in `UI/` and `App/` (the prompt names
running apps and the quit guard is the app's delegate, neither is UI); UserNotifications only in
`App/Notifications/`; AVFoundation, Speech, FluidAudio, and CoreMedia only in `Engine/` (the
layers above ask a stage, never a framework; the microphone permission is
`RecordingDevice.requestAccess()`, the model warm-ups are `SpeechModels.download()` and
`ParakeetModels.download()`); Accelerate only in `Analysis/` and `Engine/`; CoreAudio only in
`Engine/Recording/AudioHardware.swift`. The name rules are `(?x)`-wrapped rosters of top-level
type names with `match_kinds` identifier and typeidentifier, so a comment or string stays
silent; a new type in Analysis, Storage, Engine, or App must be added to the rosters by hand,
UI's names are in no roster, and `Scripts/Lint/SwiftLayering.sh` (POSIX sh + awk, the fourth
line of `lint-swift`) gates the folder graph the rosters cannot see, extension members included:
the ring below, a feature naming another feature, a feature reading a surface that never mounts
it, and a Features folder that is not a gerund or is a Models noun; the two accepted edges are
listed in the script with their reason until the two-column plank retires them, and a listed
edge that stops firing fails the gate. The ring: `Models/` names no other layer; `Analysis/` names only Models;
`Storage/` names no Engine or App type; `Engine/` names no Storage type; `Transport`,
`QuitGuard`, `RecordingPrompt`, `Diarizer`, `Transcriber`, and `Importer` named only in `App/`,
`UI/`, and `HarkApp.swift` (the app objects stay above the engine); `Catalog`, `LibraryStore`,
and `SidecarStore` named only in `Storage/` (Library is the door; the Suggester reads the
catalog through closures Library hands it); numbers for gaps, insets, corners, and sizes, `.font(`,
and `.foregroundStyle(.secondary)` only in `UI/Design/` (a view names a role); and no domain
type name under `UI/Design/` (the `Models/` roster plus `Library`, `Pipeline`, `Transport`,
`ConversationPhase`, and `SpeakerNames`; Design is a leaf of the graph, and a look that needs a
domain value is a component). A new rule is a regex scoped by a per-rule `included` or
`excluded` path pattern, with the layering fact in its `message`, fired once by a scratch probe
before it lands. Arrows point down: `App/` names Storage, Engine, and Analysis; Storage and
Engine name Analysis and Models; Analysis names Models; Models names nothing. Inside App,
`Notifications/` names Transport and Recording, `Lifecycle/` names Transport and, in `Launch`, Library and the orchestrators, Transport names
the orchestrators and Recording, and the orchestrators and Transport resolve the conversation
folder into the URLs the engine takes.
`UI/` holds six sibling folders and one file, `Binding+Presence.swift`, the SwiftUI analogue
of the root trio: a helper with no owner that neither draws a look nor decides what to show,
admitted at the root by the same threshold as `Sources/`. `Shell/` and `Features/` split the
views by one test, ratified 2026-09-13: strip every verb from the app, and what remains, a
window with three columns showing the conversations, a settled transcript, and its
participants, is the shell, the baseline presentation of Core with one folder per surface
noun: `Window/` (the split view, its toolbar, its state, and the quit dialog), `MenuBar/` (the
Commands structs the shell owns plus `FocusedValues+Hark.swift`, the table of everything the
window publishes to the menus, declared with `@Entry`), `Sidebar/`, `List/`, `Transcript/`
(the pane, its landing, column, stage status, the turn row, and its alignment
guide; `FlowLayout` is Correcting's, its only caller being the word picker), and
`Inspector/` (the three pages; the speaker page is the participant's page, a surface, not a
feature). `Features/` holds the verbs, what the user can do beyond
looking, one folder per interaction named as a gerund: `Recording/`, `Importing/`, `Playing/`,
`Searching/`, `Correcting/`, `ManagingPeople/`, `Restoring/`, `Copying/`, `NamingSpeakers/`. A
feature hangs off a shell
surface as a `View+<Feature>.swift` modifier or a subview: the shell holds the value and
mounts the seam, the feature defines the behaviour, and a feature's menu items are its own
Commands struct. A verb gets a folder the day it has a file. Needs Review is a scope, not a
verb (ruled 2026-09-14): a way of looking, the shell's by the Recently Deleted precedent, where
the scope is the sidebar's and the list's and the verb on it, Restoring, is the feature; the
verb on a conversation needing review is NamingSpeakers, so there is no `Reviewing/`. A shell file
may name a feature; no feature names another feature, and sharing goes through a hook on a
shell spine, a rendering in `Presentation/`, or a drawing in `Components/`. A feature folder
named for a Core noun (`Transcript`, `Speaker`) is a smuggled noun and is rejected. Three
folders hold what no surface or verb owns. `Design/` is the look, the one spot every
look tweak lives in, and it names no domain type: `Theme.swift` holds the tokens
(`Theme.Spacing` by purpose: lines, fields, groups, turns; `Theme.Inset` and `Theme.Corner`
per surface role plus the highlight corner; `Theme.Opacity` for the selection tint and the
shimmer's resting dim; `Theme.Reading` for the transcript column's cap and share;
`Theme.Window.defaultSize`, `Theme.Sheet`, and `Theme.Column` for every window, sheet, split-view,
and inspector size; a role or effect names a token, never a number, and since 2026-09-15 the
layout rule fails an inline frame size too), `Roles/` holds the roles (`TextRole`
with `.textRole(_:)`, a font, a hierarchy level, and a line limit per role, `SurfaceRole` with
`.surface(_:)` for card, strip, chip, and listRow, `View+Provisional`, `FloatingButtonStyle` as
`.buttonStyle(.floating)`, and `AttributedString+Emphasized` for find hits), `Effects/` holds
the effects (`View+Shimmer` as `.shimmer()`, `View+SymbolEffects`), and nothing else goes in; a
view outside `Design/` names a role, never a number, font, or colour. A behaviour that hangs off
a surface's spine is a `View+<Feature>.swift` modifier (`.lands(at:)`, `.followsTail`,
`.playsFrom`, `.correctionMenu`), never an inline if/else wrap in a body.
`Components/` is the shared drawing code, domain or not (`StagePlaceholder`,
`SpeakerNames+Label`, `ConversationRow`, `TimestampSlot`, `NoResultsPlaceholder`), admitted when
two or more surfaces draw it AND it mounts no seam (relaxed and sharpened 2026-09-14: Design is
closed to views and Presentation never draws, so a shared view has no other home; but a component
is a leaf that names Presentation and Design only, so a view that mounts feature seams, as
`TurnRow` mounts five, is a spine and stays with its surface however many surfaces draw it), and a
component names roles like any view since the layout rule covers it. `Presentation/`
is the Foundation side (display rules and text renderings over domain values: phases, names,
titles, timestamps, readable text, the observable `Pipeline`, and the
turn row's hook bundles `TurnEditing`, `TurnEmphasis`, and `TurnPlayhead`, the data a feature
hands the row, held below both Shell and Features);
a rendering one verb owns lives with the verb (`TransportState+RecordToggle` is Recording's).
Design says how a thing looks, Components draw a domain value, Presentation says what it says;
Shell and Features name Components, Components name Presentation and Design, Design names
nothing. Kind folders under `Shell/` or `Features/` (`Modifiers/`, `Dialogs/`, a per-surface
`Components/`) are rejected; the `Shell/` and `Features/` roots hold no files.

Residence: a file lives with the surface or the verb that **owns** it, and usage verifies
ownership. The shell test comes first: a file that would exist with every verb removed is its
surface's, otherwise it is its verb's. A one-consumer file's consumer is its owner unless the
platform forced the mount (`HarkToolbar` is the window's, mounted in the transcript pane for
macOS 26 toolbar placement; the import dialogs are Importing's, mounted by the window because
sheets attach there). Panes, `MenuBar/`, and features may read `Window/`, since the window
owns the state they show; nothing else reads into a shell folder from outside it except the
window mounting its panes and a feature hanging off its surface. A shared
file with no owner goes to `Presentation/` if it does not draw, `Design/` if it draws and names
no domain type, and `Components/` if it draws and does; the `UI/` root takes only a SwiftUI
helper that is none of those, never a view. A type that needs both sides splits into a
Foundation core in `Presentation/` and a `Type+Member.swift` extension in `Components/`, as
`SpeakerNames` does. `Models/` stays closed to display copy and policy.

Naming: a file is named for its one primary type, `Type+Member.swift` for an extension, or
`View+<Feature>.swift` for a modifier or builder extension, which may hold a private helper
type as `View+ImportDialogs.swift` does. The formatter owns `MARK` lines; member order is
kept by hand. Every parameter list a caller reads (a function, an explicit init, or a struct's
stored properties, its memberwise init) runs data before closures, required before optional,
defaulted last (ratified 2026-09-14; view-builder slots are closures); no lint rule can parse
it, so `memory/paramorder.py` is the audit, run on request and whenever a review touches a
signature. A view reads dependencies, `body`, private state, then knowledge and builders
in the order `body` uses them with a helper directly after its sole caller, then actions.
Every type is named for its final hark identity. The `View` suffix follows the noun: a view named
for a surface carries it (window, sidebar, list, transcript, inspector); a view named for a part
does not (row, strip, slot, placeholder, sheet, picker, choices, highlight, label, text, field,
button).

The old app's code, comments, and accumulated memories are **not** design constraints on the
rebuild. Process memories (gates, CI, GPG, automation traps) still apply.

## Queued planks

This file carries no queue; a frozen copy here once steered a session wrong. The plank queue
and backlog live in the ledger's STATE OF THE REBUILD header, and each plank gets its own
design conversation before any code.

## After a step lands

Update the ledger with what was ratified, what was deliberately not done, and any trap that
cost real time. That file is the reason a fresh session can pick this up at all.
