" Shell specific settings.

setlocal tabstop=4
setlocal shiftwidth=4
setlocal softtabstop=4

let b:is_bash = 1  " $( ... ) is POSIX compliant.

" highlight lines greater than 80 characters
match ErrorMsg '\%>80v.\+'
