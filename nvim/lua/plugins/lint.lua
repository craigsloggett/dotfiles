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
        python = { "ruff" },
        sh = { "shellcheck" },
        yaml = { "yamllint" },
      }
      vim.api.nvim_create_autocmd({
        "BufEnter",
        "BufWritePost",
        "InsertLeave",
        "TextChanged",
      }, {
        callback = function()
          require("lint").try_lint()
          -- Lint GitHub Actions Workflow files.
          local current_path = vim.fn.expand("%:p")
          if vim.bo.filetype == "yaml" then
            if string.find(current_path, "%.github/workflows") then
              require("lint").try_lint("actionlint")
            end
          end
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
