" Global netrw options.

let g:netrw_banner = 0
let g:netrw_liststyle = 3
let g:netrw_winsize = 15
let g:netrw_keepdir = 0

nnoremap <leader>dd :Lexplore %:p:h<CR>
nnoremap <Leader>da :Lexplore<CR>

" Checks if there is a file open after Vim starts up,
" and if not, open the current working directory in Netrw.
augroup ProjectDrawer
  autocmd!
  autocmd VimEnter * if expand("%") == "" | edit . | endif
augroup END
