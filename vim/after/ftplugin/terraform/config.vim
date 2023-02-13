" Terraform HCL specific settings.

setlocal tabstop=2
setlocal shiftwidth=2
setlocal softtabstop=2
setlocal expandtab

" ALE configuration settings.
let b:ale_linters = ['tflint']
let b:ale_fixers = ['terraform']
