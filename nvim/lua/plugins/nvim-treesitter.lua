vim.pack.add({
  {
    src = "https://github.com/nvim-treesitter/nvim-treesitter",
    version = vim.version.range("0.10.0")
  }
})

require("nvim-treesitter.configs").setup {
  ensure_installed = {
    "bash",
    "hcl",
    "terraform"
  },
  auto_install = false,
  highlight = {
    enable = true
  }
}
