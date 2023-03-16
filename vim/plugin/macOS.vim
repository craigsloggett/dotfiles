" macOS Apple did change the default value for the 'regexpengine'
" option to 1.
" https://github.com/vim/vim/issues/7280
set regexpengine=0
" macOS ships with the modelines variable set to 0, essentially
" disabling the modeline feature.
" https://unix.stackexchange.com/a/20083
set modelines=1
