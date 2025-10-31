vim.pack.add({
  {
    src = "https://github.com/mfussenegger/nvim-lint.git"
  }
})

require("lint").linters_by_ft = {
  sh = { "shellcheck" },
  yaml = { "yamllint" },
  ghaction = { "actionlint" }
}
