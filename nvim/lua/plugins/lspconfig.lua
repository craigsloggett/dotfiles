return {
  {
    "neovim/nvim-lspconfig",
    dependencies = {
      "williamboman/mason-lspconfig.nvim",
    },
    keys = {
      { "<leader>rn", vim.lsp.buf.rename },
      { "<leader>ca", vim.lsp.buf.code_action },
      { "K", vim.lsp.buf.hover },
      { "gd", vim.lsp.buf.definition },
    },
  },
}
