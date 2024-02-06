return {
  {
    "stevearc/conform.nvim",
    opts = {
      formatters_by_ft = {
        lua = { "stylua" },
        sh = { "shfmt" },
      },
      format_on_save = {
        lsp_fallback = true,
        timeout_ms = 500,
      },
    },
    config = function(_, opts)
      require("conform").setup(opts)
      require("conform").formatters.shfmt = {
        prepend_args = { "-i", "2" },
      }
    end,
  },
}
