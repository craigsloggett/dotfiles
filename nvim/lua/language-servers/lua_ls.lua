require("lspconfig").lua_ls.setup({
  settings = {
    Lua = {
      format = {
        enable = false,
      },
      diagnostics = {
        global = {
          "vim",
        },
      },
      workspace = {
        library = {
          vim.env.VIMRUNTIME,
        },
      },
    },
  },
})
