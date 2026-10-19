-- Parsers to install beyond those bundled with Neovim. The FileType
-- autocommand in autocmds.lua starts highlighting once a parser exists.
local parsers = {
  "bash",
  "comment",
  "go",
  "gomod",
  "gosum",
  "gowork",
  "hcl",
  "terraform",
  "yaml",
  "zsh"
}

-- Parsers only work with the revisions the plugin pins, so rebuild them
-- whenever vim.pack updates it.
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
