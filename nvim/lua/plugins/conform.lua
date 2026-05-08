vim.pack.add({
  {
    src = "https://github.com/stevearc/conform.nvim.git",
    version = vim.version.range("9.1.0")
  }
})

require("conform").setup {
  formatters_by_ft = {
    hcl = { "terraform_fmt" },
    json = { "jq" },
    sh = { "shfmt" },
    yaml = { "yamlfmt" },
    zsh = { "shfmt" },
    ["*"] = { "trim_whitespace", "trim_newlines" }
  },
  formatters = {
    jq = {
      command = "jq",
      args = { "." },
      stdin = true
    },
    shfmt = {
      prepend_args = { "-i", "2", "-ci" }
    }
  },
  format_on_save = {
    timeout_ms = 500,
    lsp_format = "first"
  }
}
