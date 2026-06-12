---
paths:
  - '**/Makefile'
  - '**/makefile'
  - '**/GNUmakefile'
  - '**/*.mk'
---

## Recipe Shell

- Write recipe shell as strictly POSIX sh; make runs recipes with `/bin/sh`, so no bashisms (no `[[ ]]`, no arrays, no `local`, no `set -o pipefail`).
- Use `printf` for all output, never `echo`.
