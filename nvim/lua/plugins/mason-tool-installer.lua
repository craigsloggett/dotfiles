return {
  {
    "WhoIsSethDaniel/mason-tool-installer.nvim",
    dependencies = {
      "williamboman/mason.nvim",
    },
    opts = {
      ensure_installed = {
        "black",
        "isort",
        "stylua",
        "shfmt",
        "shellcheck",
      },
      auto_update = true,
    },
  },
}
