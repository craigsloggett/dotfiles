" Shell specific settings.

setlocal tabstop=8
setlocal shiftwidth=8
setlocal softtabstop=8

let b:is_bash = 1  " $( ... ) is POSIX compliant.

" highlight lines greater than 100 characters
match ErrorMsg '\%>100v.\+'
