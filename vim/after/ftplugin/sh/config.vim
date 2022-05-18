" Shell specific settings.

setlocal tabstop=8
setlocal shiftwidth=8
setlocal softtabstop=8

let b:is_bash = 1  " $( ... ) is POSIX compliant.
let b:ale_linters = ['shellcheck']
