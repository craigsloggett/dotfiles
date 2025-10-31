vim.pack.add({
  {
    src = "https://github.com/mfussenegger/nvim-lint.git"
  }
})

require("lint").linters_by_ft = {
  ghaction = { "actionlint" },
  sh = { "shellcheck" },
  yaml = { "yamllint" }
}
