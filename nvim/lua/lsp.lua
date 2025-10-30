vim.lsp.enable({
  "bashls",
  "lua_ls",
  "terraform-ls",
  "tflint"
})

vim.diagnostic.config({
  virtual_lines = true
})

-- Keymaps specific to LSP.
vim.keymap.set("n", "<leader>d", ":lua vim.lsp.buf.definition()<CR>", { noremap = true, silent = true })
vim.keymap.set("n", "<leader>h", ":lua vim.lsp.buf.hover()<CR>", { noremap = true, silent = true })
vim.keymap.set("n", "<leader>rn", ":lua vim.lsp.buf.rename()<CR>", { noremap = true, silent = true })

-- Hide all semantic highlights to prioritize treesitter parsers.
for _, group in ipairs(vim.fn.getcompletion("@lsp", "highlight")) do
  vim.api.nvim_set_hl(0, group, {})
end
