return {
  {
    "WhoIsSethDaniel/mason-tool-installer.nvim",
    dependencies = {
      "williamboman/mason.nvim",
    },
    opts = {
      ensure_installed = {
        "actionlint",
        "ruff",
        "shellcheck",
        "shfmt",
        "stylua",
        "tflint",
        "yamlfmt",
        "yamllint",
      },
      auto_update = true,
    },
  },
}
