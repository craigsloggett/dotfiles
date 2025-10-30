-- Autocommand to set options for the Lua filetype
vim.api.nvim_create_augroup("LuaSettings", { clear = true })
vim.api.nvim_create_autocmd("BufWritePre", {
  group = "LuaSettings",
  pattern = "*.lua",
  callback = function()
    vim.lsp.buf.format({ async = false })
  end
})

-- Autocommand to set options for the Shell filetype
vim.api.nvim_create_augroup("ShellSettings", { clear = true })
vim.api.nvim_create_autocmd("BufWritePre", {
  group = "ShellSettings",
  pattern = { "*.sh", "*install*", "*setup*" },
  callback = function()
    vim.lsp.buf.format({ async = false })
  end
})

-- Autocommand to set options for the Terraform filetype
vim.api.nvim_create_augroup("TerraformSettings", { clear = true })
vim.api.nvim_create_autocmd("BufWritePre", {
  group = "TerraformSettings",
  pattern = { "*.tf", "*.tfvars" },
  callback = function()
    vim.lsp.buf.format({ async = false })
  end
})

-- Autocommand to set options for the Python filetype
vim.api.nvim_create_augroup("PythonSettings", { clear = true })
vim.api.nvim_create_autocmd("FileType", {
  group = "PythonSettings",
  pattern = "python",
  callback = function()
    vim.opt_local.tabstop = 4
    vim.opt_local.shiftwidth = 4
    vim.opt_local.softtabstop = 4
  end
})

-- Autocommand to set options for the Go filetype
vim.api.nvim_create_augroup("GoSettings", { clear = true })
vim.api.nvim_create_autocmd("FileType", {
  group = "GoSettings",
  pattern = "go",
  callback = function()
    vim.opt_local.tabstop = 4
    vim.opt_local.shiftwidth = 4
    vim.opt_local.softtabstop = 4
    vim.opt.expandtab = false
  end
})
