" Shell specific settings.

setlocal tabstop=8
setlocal shiftwidth=8
setlocal softtabstop=8

let b:is_bash = 1  " $( ... ) is POSIX compliant.
let b:ale_linters = ['shellcheck']
let b:ale_fixers = ['shfmt']
let b:ale_sh_shfmt_options = '--case-indent --space-redirects'

" highlight lines greater than 100 characters
match ErrorMsg '\%>100v.\+'
