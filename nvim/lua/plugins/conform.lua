vim.pack.add({
  {
    src = "https://github.com/stevearc/conform.nvim",
    version = vim.version.range("9.1.0")
  }
})

require("conform").setup({
  formatters_by_ft = {
    sh = { "shfmt" }
  },
  format_on_save = {
    lsp_format = "fallback"
  }
})
