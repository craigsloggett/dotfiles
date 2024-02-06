return {
  {
    "mfussenegger/nvim-lint",
    event = {
      "BufReadPre",
      "BufNewFile",
    },
    dependencies = {
      "WhoIsSethDaniel/mason-tool-installer.nvim",
    },
    config = function()
      require("lint").linters_by_ft = {
        sh = { "shellcheck" },
      }
      vim.api.nvim_create_autocmd({
        "BufEnter",
        "BufWritePost",
        "InsertLeave",
      }, {
        callback = function()
          require("lint").try_lint()
        end,
      })
    end,
    keys = {
      {
        "<leader>ll",
        function()
          require("lint").try_lint()
        end,
      },
    },
  },
}
