-- Configure vim options before loading any plugins.
require("config.options")
require("config.keymaps")
-- Bootstrap the lazy.nvim plugin manager.
require("config.lazy")
-- Configure language servers.
require("language-servers.lua_ls")
require("language-servers.terraformls")
require("language-servers.tflint")
require("language-servers.gopls")
