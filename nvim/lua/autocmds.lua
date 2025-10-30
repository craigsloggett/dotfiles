-- Autocommand to set options for Python filetype
vim.api.nvim_create_augroup("PythonSettings", { clear = true })
vim.api.nvim_create_autocmd("FileType", {
  group = "PythonSettings",
  pattern = "python",
  callback = function()
    vim.opt_local.tabstop = 4
    vim.opt_local.shiftwidth = 4
    vim.opt_local.softtabstop = 4
  end,
})

-- Autocommand to set options for Go filetype
vim.api.nvim_create_augroup("GoSettings", { clear = true })
vim.api.nvim_create_autocmd("FileType", {
  group = "GoSettings",
  pattern = "go",
  callback = function()
    vim.opt_local.tabstop = 4
    vim.opt_local.shiftwidth = 4
    vim.opt_local.softtabstop = 4
    vim.opt.expandtab = false
  end,
})
