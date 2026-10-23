vim.diagnostic.config({
  virtual_lines = { current_line = true },
  float = { source = true }
})

vim.keymap.set("n", "gd", vim.lsp.buf.definition)

vim.lsp.enable({
  "lua_ls",
  "terraformls",
  "tflint"
})
