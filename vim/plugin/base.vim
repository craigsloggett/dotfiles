"" XDG Directories defined in the specification:
" https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html

set runtimepath^=$XDG_CONFIG_HOME/vim
set runtimepath+=$XDG_DATA_HOME/vim
set runtimepath+=$XDG_CONFIG_HOME/vim/after

set packpath^=$XDG_DATA_HOME/vim,$XDG_CONFIG_HOME/vim
set packpath+=$XDG_CONFIG_HOME/vim/after,$XDG_DATA_HOME/vim/after

let g:netrw_home = $XDG_STATE_HOME."/vim"
set viewdir=$XDG_DATA_HOME/vim/view

set backupdir=$XDG_CACHE_HOME/vim/backup
set directory=$XDG_CACHE_HOME/vim/swap
set undodir=$XDG_CACHE_HOME/vim/undo

set viminfofile=$XDG_STATE_HOME/vim/viminfo

"" Terminal Settings

" Ensure 256 colours
set t_Co=256

" Disable Background Color Erase (BCE) so that color schemes
" work properly when Vim is used inside tmux and GNU screen.
if &term =~ '256color'
  set t_ut=
endif

"" UI Settings

" Enable syntax highlighting
syntax on

set number			" show line numbers
set showcmd			" show command in bottom bar
set ruler			" show ruler in bottom bar
match ErrorMsg '\%>80v.\+'	" highlight lines greater than 80 characters

" Statusline
set laststatus=2
set noshowmode

" Search Highlighting
set hlsearch			" highlight search terms
				" clear highlights by pressing enter
nnoremap <CR> :noh<CR>

" Split Behaviour
set splitright			" split to the right by default
set splitbelow			" split to the bottom by default
				" create a new window by default
nnoremap <C-w>v :vnew<CR>
nnoremap <C-w>s :new<CR>
