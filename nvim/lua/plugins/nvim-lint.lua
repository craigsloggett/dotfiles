vim.pack.add({
  {
    src = "https://github.com/mfussenegger/nvim-lint",
    version = "master"
  }
})

require("lint").linters_by_ft = {
  ghaction = { "actionlint" },
  go = { "golangcilint", "vale" },
  json = { "jq" },
  markdown = { "rumdl", "vale" },
  sh = { "shellcheck" },
  swift = { "swiftlint" },
  yaml = { "yamllint" }
}

require("lint").linters.rumdl.stream = "stdout"

vim.api.nvim_create_autocmd({ "FileType", "BufWritePost" }, {
  group = "UserAutoCmds",
  callback = function()
    require("lint").try_lint()
  end
})
