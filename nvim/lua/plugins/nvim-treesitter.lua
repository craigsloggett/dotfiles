local parsers = {
  "bash",
  "comment",
  "hcl",
  "json",
  "go",
  "terraform",
  "yaml",
  "zsh"
}

vim.api.nvim_create_autocmd("PackChanged", {
  group = "UserAutoCmds",
  callback = function(ev)
    if ev.data.spec.name == "nvim-treesitter" and ev.data.kind == "update" then
      require("nvim-treesitter").update()
    end
  end
})

vim.pack.add({
  {
    src = "https://github.com/nvim-treesitter/nvim-treesitter",
    version = "main"
  }
})

require("nvim-treesitter").install(parsers)
