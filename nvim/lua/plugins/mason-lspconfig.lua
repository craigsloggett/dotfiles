-- Setup the mason language server manager.
require("mason").setup()
require("mason-lspconfig").setup()

-- Specify which language servers to install.
require("mason-lspconfig").setup {
  ensure_installed = { "lua_ls" }
}

-- Include the configuration for any of the language servers.
require("language-servers/lua_ls")
