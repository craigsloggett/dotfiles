## Hark Rebuild

Hark derives a conversation's transcript and voiceprints from three inputs: the
recognized words, the diarized segments, and the corrections. `transcript.jsonl`
and `voiceprints.jsonl` are caches of that derivation. `harklib/regroup.py` is a
line-for-line port of it, checked against Hark at commit `c7cccfa` (version
0.114.0), where it reproduced every conversation Hark had written byte for byte.

### Triggers

| Moment                                | Effect                                  |
| ------------------------------------- | --------------------------------------- |
| A correction is added or undone       | Rebuilds the transcript and voiceprints |
| Launch, `voiceprints.jsonl` missing   | The same rebuild                        |
| Launch, `transcript.jsonl` unreadable | The same rebuild                        |
| A speaker is named                    | Nothing; only `attributions` changes    |

### Rules

1. A word spans at most one second from its start. Longer stamps carry the
   pause after the word.
2. A label the diarizer heard for under 5 seconds in total doesn't own any
   words, unless every label is that short.
3. Each system word belongs to the segment nearest its start, and so to the
   voice bound to that segment's label in `speech`.
4. Corrections apply in order. `reassign` takes every word that starts inside
   its span and pins it. `merge` moves one voice's words to another. `discard`
   drops system words that start in its span, or a microphone turn inside it.
5. Words run together until the voice changes, the speaker pauses (1 second
   after a sentence end, 2 seconds inside a sentence), or a microphone turn
   cuts in. A microphone turn that starts in a pause of 0.4 seconds ends the
   run there; one that started any time during the run ends it at the next
   sentence end. The pause is measured between diarized segments unless a word
   is pinned or sits more than 0.25 seconds outside its segment.
6. When the next run is another voice, the last one or two unpinned words after
   a run's final sentence end move to that voice. Three or more stay, and so
   does a tail that is the whole run.
7. Each run is cut into turns of whole sentences up to 300 characters. Fillers
   ("um", "uh"), a restarted phrase, and a throwaway "like" leave the text but
   keep their time.
8. `voices` lists the voices that have a turn, in order of first appearance.
9. A voice's voiceprint is the mean of the diarizer's chunks that overlap its
   turns by 3 seconds or more. A voice that no chunk heard for that long
   doesn't get one.
10. A voiceprint suggests its person for other conversations only when the voice
    spoke for 15 seconds with one stretch of 5, and only above a similarity of
    0.7.

Rule 6 is why a correction can move words outside its span: pinning a run
changes what counts as its neighbour's stranded tail. `plan` re-runs the rebuild
after each correction and pins whatever moved, until nothing does.

### Sources

| Rule    | Hark source under `macOS/Sources`                        |
| ------- | -------------------------------------------------------- |
| 1       | `Analysis/Text/Recognition+SpokenWords.swift`            |
| 2 to 6  | `Analysis/Regrouping/Transcript+Regrouped.swift`         |
| 5       | `Analysis/Text/Turn+Breaks.swift`                        |
| 7       | `Analysis/Text/Turn+Paragraphs.swift`, `Turn+Text.swift` |
| 8       | `Models/Transcript.swift`                                |
| 9       | `Analysis/Identity/Voiceprints+Chunks.swift`             |
| 10      | `Analysis/Identity/Suggester.swift`, `Suggestions.swift` |
| Numbers | `Analysis/Calibration.swift`                             |
| Launch  | `Storage/Library.swift`, `Storage/Regrouper.swift`       |
| Schemas | `Storage/Schema.swift`                                   |

### Self-Test Failures

`hark selftest` replays every conversation through the port and compares the
result with the files Hark wrote. A conversation awaiting Hark's rebuild is
reported, not failed.

1. A schema error means Hark changed a file format. Read `Storage/Schema.swift`
   and the record it names before touching `harklib/store.py`.
2. A difference means a rule or a number moved. Run `git log` on the files in
   the table above, starting with `Calibration.swift`, and carry the change into
   `harklib/regroup.py`.
3. Run `hark selftest` again. Don't plan anything until it passes, and update
   the commit named at the top of this file.

Hark's source is at `~/Developer/GitHub/craigsloggett/hark`. The installed app
can be older than the checkout; compare `CFBundleShortVersionString` in
`/Applications/Hark.app/Contents/Info.plist` with the checkout's history before
blaming the port.
