return {
  "nvimtools/none-ls.nvim",
  config = function()
    require("null-ls").setup({
      sources = {
        require("null-ls").builtins.formatting.stylua,
        require("null-ls").builtins.formatting.shfmt,
        require("null-ls").builtins.diagnostics.shfmt
      },
    })

    vim.keymap.set("n", "<leader>gf", vim.lsp.buf.format, {})
  end,
}
