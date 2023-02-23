# Vim Packages

**Note:** All packages added to this directory are started automatically when `vim` starts.

To add packages use `git submodules` which will enable the ability to clone
the repo with submodules included:

```shell
git clone --recurse-submodules https://github.com/craigsloggett/dotfiles
```

The following (system) packages are required on the host in order to fully utilize all of these 
(vim) packages:

 - `fzf`

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

## ALE

The Asynchronous Lint Engine provides linting and formatting for various languages.

The following command was used to add this package to the built-in package manager:

```shell
git submodule add --name ale https://github.com/dense-analysis/ale ./ale
```

### Shell

The following (system) packages are required on the host in order to lint and format `sh` source files:

 - `shellcheck`
 - `shfmt`

### YAML

The following (system) packages are required on the host in order to lint `yaml` source files:

 - `yamllint`

### Terraform

The following (system) packages are required on the host in order to lint and format `terraform` source files:

 - `terraform`
 - `tflint`

## vim-terraform

Add HCL syntax highlighting to `vim`.

The following command was used to add this package to the built-in package manager:

```shell
git submodule add --name vim-terraform https://github.com/hashivim/vim-terraform ./vim-terraform
```

The following (system) packages are required on the host in order to fully utilize this 
(vim) package:

 - `terraform`
