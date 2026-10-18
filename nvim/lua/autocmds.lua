vim.api.nvim_create_augroup("UserAutoCmds", { clear = true })

vim.api.nvim_create_autocmd("FileType", {
  group = "UserAutoCmds",
  callback = function(ev)
    pcall(vim.treesitter.start, ev.buf)
  end
})

vim.api.nvim_create_autocmd("BufWritePre", {
  group = "UserAutoCmds",
  callback = function(ev)
    local editorconfig = vim.b[ev.buf].editorconfig or {}
    if editorconfig.trim_trailing_whitespace then
      return
    end
    local view = vim.fn.winsaveview()
    vim.cmd("silent! undojoin")
    vim.cmd([[silent keepjumps keeppatterns %s/\s\+$//e]])
    vim.fn.winrestview(view)
  end
})
