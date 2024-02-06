vim.api.nvim_create_autocmd({ "BufWritePost" }, {
  pattern = { "<buffer>" },
  callback = function()
    vim.lsp.buf.format()
  end,
})
