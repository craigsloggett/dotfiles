" YAML specific settings.

setlocal tabstop=2
setlocal shiftwidth=2
setlocal softtabstop=2
setlocal expandtab

match NONE '\%>80v.\+'  " Allow long lines of text.

let b:ale_linters = ['yamllint']
