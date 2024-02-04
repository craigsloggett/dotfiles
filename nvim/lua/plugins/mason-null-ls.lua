return {
  {
    "jay-babu/mason-null-ls.nvim",
    dependencies = {
      "williamboman/mason.nvim",
      "nvimtools/none-ls.nvim",
    },
    opts = {
      ensure_installed = {
        "stylua",
      },
      automatic_installation = false,
      automatic_setup = true,
    },
  },
}
