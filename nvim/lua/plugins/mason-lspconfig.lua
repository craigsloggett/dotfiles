return {
  {
    "williamboman/mason-lspconfig.nvim",
    dependencies = {
      "williamboman/mason.nvim",
    },
    opts = {
      ensure_installed = {
        "gopls",
        "lua_ls",
        "terraformls",
      },
    },
  },
}
