require("lspconfig").lua_ls.setup({
  capabilities = require("cmp_nvim_lsp").default_capabilities(),
  settings = {
    Lua = {
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

vim.keymap.set("n", "K", vim.lsp.buf.hover, {})
vim.keymap.set("n", "gd", vim.lsp.buf.definition, {})
vim.keymap.set({ "n", "v" }, "<leader>ca", vim.lsp.buf.code_action, {})
