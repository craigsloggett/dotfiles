---
name: review-prose
description: >-
  Use when the user asks to check writing for LLM-isms or to make it sound less
  machine-written, whether a named file, a PR description, or the prose this
  session wrote, and before posting a PR description or document you drafted
  for them.
---

## Review Prose

Edit the text so it reads like a careful human expert wrote it. The reader is
technical and short on time, so every sentence has to carry information. Delete
a sentence that only announces, restates, or emphasises.

Preserve every fact, claim, number, and technical term, and do not add content.
Leave code blocks, commands, and quotes untouched.

Every bullet in the three "to Fix" sections is a pattern to find and remove,
followed by what to write instead. Real before and after pairs for each are in
`examples/before-after.md`.

### Scope

- A file, PR number, or URL in the arguments means review that text.
- Quoted text in the arguments means find it and review the paragraph around it.
- No arguments means review the prose this session wrote or edited, such as PR
  descriptions, Markdown files, commit subjects, and comments in the branch
  diff.

### Wording to Fix

- Stock vocabulary such as delve, leverage, robust, seamless, crucial, pivotal,
  comprehensive, nuanced, landscape, realm, tapestry, testament, foster,
  underscore, navigate (figurative), streamline, unlock, and elevate. Use the
  plain word.
- Intensifiers and sincerity markers such as really, truly, genuinely,
  honestly, simply, incredibly, and very. Delete them.
- Throat-clearing such as "It's worth noting that", "Here's the thing", "When
  it comes to", and "A few things that should help". Delete it and open with
  the content.
- Stacked hedges such as "may potentially" and "can often help to". Hedge once,
  where the uncertainty is real, and say what it is.
- An action verb followed by "no", "nothing", or "none of", as in "registers no
  routes" or "uses none of the backoff". Write the plain negative ("doesn't
  register any routes") or the positive ("takes effect without a restart").
- "Only" after a verb to imply what is left out, as in "would be using the
  library only to send the request". Say what it does and what it leaves out
  ("would keep its own retries and share the code that sends the request").
- A made-up label for something that has a name, as in "the kind of account"
  for a field called `userIdentityType`. Use the name the code or the API uses.

### Sentences to Fix

- Contrast against something nobody claimed, as in "It's not X, it's Y" or
  "errors rather than wrong output". State Y directly.
- A justification that rules out an alternative the reader was never shown.
  Introduce the alternative and then give the reasons, or delete the
  justification.
- "Noun phrase, which..." clauses. Split them into two sentences.
- Reflexive groups of three. Keep the number of items the content has.
- Rhetorical questions answered at once ("The result? ..."). State the answer.
- Colon or dash reveals used for drama, and short quotable lines that close a
  paragraph by restating it. State the point plainly, and delete the
  restatement.
- Em dashes. Use commas, parentheses, or two sentences, and do not swap them
  all for semicolons.
- Repetitive structure, such as sentences of the same length and rhythm,
  sibling bullets that open the same way, or two parallel "never" clauses in
  one sentence. Vary it.
- A thing that acts with nothing said about what it acts on, as in "the account
  type decides alone". Say what happens to what ("every directory account
  counts as in the tenant").

### Structure to Fix

- Openers that restate the topic or praise the question, and closers that
  summarise, offer further help, or ask a follow-up. Delete them.
- Headings and table column headers that sound like a guide, such as "How to
  read this", "What the service does", or a column headed "What it adds". Use a
  plain label ("Commits", "Behaviour", "Adds"). Keep a template's headings
  verbatim, even when they sound like a guide, and do not add headings to short
  sections.
- A list introduced by a line ending in a colon. End the intro with a period,
  or fold the list into the paragraph.
- Bullets that fragment connected reasoning. Convert them to prose, and keep
  lists for parallel items a reader scans.
- Bullets that start with a bold label and colon. Write a sentence that names
  its subject.
- Bold scattered for emphasis. Remove it, except on terms a reader would scan
  for.
- Emoji, and tables for content that isn't tabular. Remove the emoji, and write
  the table's content as prose or a list.
- History of how the branch got here, and the names of people, in a PR
  description. Describe what the branch introduces as it stands.

### Steps

1. Save the original before editing. For a PR, write
   `gh pr view <n> --json body -q .body` to `original.md` in the scratchpad and
   copy it to `draft.md`.
2. Scan for candidates and read each hit in context, because a hit is a
   candidate and not a verdict.

   ```sh
   grep -nE ':$|, which|rather than|instead of|not just|\b(no|nothing|never|none|only)\b|—|\*\*' draft.md
   grep -niwE 'delve|leverage|robust|seamless|crucial|pivotal|comprehensive|nuanced|landscape|realm|tapestry|testament|foster|underscore|navigate|streamline|unlock|elevate|really|truly|genuinely|honestly|simply|incredibly|very|worth noting' draft.md
   grep -nE '^#|^\|' draft.md
   ```

3. Read the whole text as well. Groups of three, repetitive structure, unseen
   alternatives, made-up labels, things that act on nothing, and most contrast
   framing don't show up in the scan.
4. Fix each finding in the draft, then run the scan again and reread every line
   you changed.
5. Write the draft back. For a PR, run `gh pr edit <n> --body-file draft.md`,
   then diff `gh pr view` against the draft to confirm it landed.
6. Report the fixes grouped by pattern. List separately each sentence whose
   claim shifted and each hit you kept, with the reason, and give the path to
   the saved original.

### Gotchas

- Do not replace a removed pattern with its nearest equivalent. Colon-led lists
  turned into subheadings, em dashes turned into semicolons, and a "which"
  clause turned into "; it" each swap one tic for another.
- Rewording a negative can change the claim. "Knows nothing about the core" and
  "doesn't import anything from the core" say different things, so list each
  shift for the user to check.
- A "not X" that warns about a mistake a reader could make is information, as
  in "the directory id, not a domain name". Keep it.
- An "only" that states a condition is information, as in "tries again only if
  the failure is retryable". Keep it.
- If a fix needs a fact the text doesn't give, leave the sentence and flag it.
- Check later edits against the patterns, not against the text they changed.
  An edit to cleaned-up prose brings patterns back, and using the old text as
  the baseline misses them.
- New text has to match its neighbours. A table cell twice as long as the
  others, a bullet three times the length of its siblings, a colon gloss in one
  cell, or an undefined shorthand reads as added later.
- Before changing a heading, find the template the text was written from, such
  as the repo's PR template or an RFC template, and compare. A heading that
  comes from the template stays as it is, as in "Risk and how to revert" in a
  PR description or "Why this matters to the customer" in an RFC.
- Fixing a commit subject rewrites history. Propose the new subjects and wait
  for approval before rebasing or force-pushing.
- Code comments follow their language's doc conventions first, such as a Go
  doc comment starting with the name. Trimming comments belongs to
  `conventions:reduce-comments`.
- The report is prose too. Write it in plain sentences, without bold-label
  bullets.
