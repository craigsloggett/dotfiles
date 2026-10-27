vim.pack.add({
  {
    src = "https://github.com/mfussenegger/nvim-lint",
    version = "master"
  }
})

require("lint").linters_by_ft = {
  ghaction = { "actionlint" },
  go = { "golangcilint" },
  json = { "jq" },
  sh = { "shellcheck" },
  yaml = { "yamllint" }
}

vim.api.nvim_create_autocmd({ "FileType", "BufWritePost" }, {
  group = "UserAutoCmds",
  callback = function()
    require("lint").try_lint()
  end
})
