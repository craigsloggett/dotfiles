return {
  "nvimtools/none-ls.nvim",
  config = function()
    require("null-ls").setup({
      sources = {
        require("null-ls").builtins.formatting.stylua,
      },
    })

    vim.keymap.set("n", "<leader>gf", vim.lsp.buf.format, {})
  end,
}
