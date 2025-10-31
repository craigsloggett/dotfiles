-- User AutoCmds should specify `clear = true`, but this is not true when a plugin manages them.
vim.api.nvim_create_augroup("UserAutoCmds", { clear = true })

-- Language specific tab lengths.
vim.api.nvim_create_autocmd("FileType", {
  group = "UserAutoCmds",
  pattern = { "go", "python" },
  callback = function()
    vim.opt_local.tabstop = 4
    vim.opt_local.shiftwidth = 4
    vim.opt_local.softtabstop = 4
  end
})

-- Language specific tab character.
vim.api.nvim_create_autocmd("FileType", {
  group = "UserAutoCmds",
  pattern = "go",
  callback = function()
    vim.opt_local.expandtab = false
  end
})

-- Lint files as you go.
vim.api.nvim_create_autocmd({ "BufEnter", "BufWritePost", "InsertLeave", "TextChanged" }, {
  group = "UserAutoCmds",
  callback = function()
    require("lint").try_lint()
  end
})
