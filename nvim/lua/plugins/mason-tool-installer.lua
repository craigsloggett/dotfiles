return {
  {
    "WhoIsSethDaniel/mason-tool-installer.nvim",
    dependencies = {
      "williamboman/mason.nvim",
    },
    opts = {
      ensure_installed = {
        "stylua",
        "shfmt",
        "shellcheck",
      },
      auto_update = true,
    },
  },
}
