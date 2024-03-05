return {
  {
    "WhoIsSethDaniel/mason-tool-installer.nvim",
    dependencies = {
      "williamboman/mason.nvim",
    },
    opts = {
      ensure_installed = {
        "actionlint",
        "black",
        "isort",
        "shellcheck",
        "shfmt",
        "stylua",
        "yamlfmt",
        "yamllint",
      },
      auto_update = true,
    },
  },
}
