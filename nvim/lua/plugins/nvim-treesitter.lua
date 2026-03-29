vim.pack.add({
  {
    src = "https://github.com/nvim-treesitter/nvim-treesitter",
    version = "main"
  }
})

-- Non-bundled parsers to install on demand. Bundled languages (markdown, lua,
-- vim, query) auto-start via their ftplugins. For everything else, the FileType
-- autocommand below starts treesitter if the parser exists, or installs it
-- asynchronously if it doesn't. Reopen the file after install to get highlighting.
local parsers = { "bash", "gitcommit", "gitignore", "hcl", "terraform", "yaml" }

vim.api.nvim_create_autocmd("FileType", {
  callback = function(args)
    local lang = vim.treesitter.language.get_lang(args.match) or args.match
    if pcall(vim.treesitter.start, args.buf, lang) then
      -- Parser exists, highlighting started.
    elseif vim.list_contains(parsers, lang) then
      require("nvim-treesitter").install({ lang })
    end
  end
})
