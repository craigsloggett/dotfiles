return {
  {
    "stevearc/conform.nvim",
    event = {
      "BufReadPre",
      "BufNewFile",
    },
    dependencies = {
      "WhoIsSethDaniel/mason-tool-installer.nvim",
    },
    opts = {
      formatters_by_ft = {
        lua = { "stylua" },
        python = { "ruff" },
        sh = { "shfmt" },
        terraform = { "terraform_fmt" },
        hcl = { "terraform_fmt" },
        yaml = { "yamlfmt" },
        zsh = { "shfmt" },
      },
      format_on_save = {
        lsp_fallback = true,
        timeout_ms = 500,
      },
    },
    config = function(_, opts)
      require("conform").setup(opts)
      require("conform").formatters.shfmt = {
        prepend_args = { "-i", "2", "-ci" },
      }
    end,
    keys = {
      {
        "<leader>f",
        function()
          require("conform").format()
        end,
      },
    },
  },
}
