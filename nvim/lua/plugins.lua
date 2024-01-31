-- Setup the lazy.nvim package manager.
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"

if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", -- latest stable release
    lazypath,
  })
end

vim.opt.rtp:prepend(lazypath)

-- Specify which plugins to install.
require("lazy").setup({
  {
    -- Highlight, edit, and navigate code.
    "nvim-treesitter/nvim-treesitter",
    dependencies = {
      "nvim-treesitter/nvim-treesitter-textobjects",
    },
    build = ":TSUpdate"
  },
  {
    -- Manage language servers configuration.
    "neovim/nvim-lspconfig",
    dependencies = {
      {
        "williamboman/mason.nvim",
        config = true
      },
      {
        "williamboman/mason-lspconfig.nvim"
      }
    }
  }
})

-- Include the configuration for each plugin.
require("plugins/treesitter")
require("plugins/mason-lspconfig")
