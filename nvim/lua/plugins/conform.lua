vim.pack.add({
  {
    src = "https://github.com/stevearc/conform.nvim",
    version = vim.version.range("9.1.0")
  }
})

require("conform").setup({
  formatters_by_ft = {
    go = { "golangci-lint" },
    json = { "jq" },
    sh = { "shfmt" },
    yaml = { "yamlfmt" }
  },
  formatters = {
    ["golangci-lint"] = {
      cwd = require("conform.util").root_file({ ".golangci.yml", "go.mod" })
    },
    jq = {
      prepend_args = { "-S" }
    }
  },
  format_on_save = {
    lsp_format = "fallback"
  }
})
