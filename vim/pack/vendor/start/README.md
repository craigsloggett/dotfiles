# Vim Packages

**Note:** All packages added here are started automatically.

To add packages here, use git submodules which will allow me to clone
the repo with submodules includes:

```shell
git clone --recurse-submodules https://github.com/craigsloggett/dotfiles
```

The following submodules have been added to this repository:

## ALE

The Asynchronous Lint Engine provides linting for various languages. Currently,
the following tools are required to support the configured linters:

 - terraform
 - tflint
 - shellcheck
 - shfmt

The following command was used to add this package to the built-in package manager:

```shell
git submodule add --name ale https://github.com/dense-analysis/ale ./ale
```

## fzf

A fuzzy finder (opens files), used to navigate files in the project directory.

The following command was used to add this package to the built-in package manager:

```shell
git submodule add --name fzf https://github.com/junegunn/fzf ./fzf
```

## fzf-vim

A plugin that has a set of defaults to easily support `fzf` in `vim`.

The following command was used to add this package to the built-in package manager:

```shell
git submodule add --name fzf-vim https://github.com/junegunn/fzf.vim ./fzf-vim
```

## vim-terraform

Add HCL syntax highlighting to `vim`.

The following command was used to add this package to the built-in package manager:

```shell
git submodule add --name vim-terraform https://github.com/hashivim/vim-terraform ./vim-terraform
```
