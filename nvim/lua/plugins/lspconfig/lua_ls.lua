-- Configure the Lua language server.
require("lspconfig").lua_ls.setup {
  settings = {
    Lua  = {
      diagnostics = {
        globals = {
	  "vim"
        }
      },
      workspace = {
        library = {
	  vim.env.VIMRUNTIME
	}
      }
    }
  }
}
