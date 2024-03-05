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
        python = { "flake8" },
        sh = { "shellcheck" },
      }
      vim.api.nvim_create_autocmd({
        "BufEnter",
        "BufWritePost",
        "InsertLeave",
        "TextChanged",
      }, {
        callback = function()
          require("lint").try_lint()
          -- Handle YAML files and Actions separately.
          local current_path = vim.fn.expand("%:p")
          if vim.bo.filetype == "yaml" then
            if string.find(current_path, "%.github/workflows") then
              require("lint").try_lint("actionlint")
            else
              require("lint").try_lint("yamllint")
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
