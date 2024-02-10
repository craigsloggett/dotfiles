return {
  {
    "nvim-telescope/telescope.nvim",
    dependencies = {
      "nvim-lua/plenary.nvim",
    },
    opts = {
      defaults = {
        history = {
          path = vim.fn.stdpath("data") .. "/telescope/history",
        },
        vimgrep_arguments = {
          "rg",
          "--color=never",
          "--no-heading",
          "--with-filename",
          "--line-number",
          "--column",
          "--smart-case",
          "--hidden",
        },
      },
      pickers = {
        find_files = {
          find_command = { "rg", "--files", "--hidden", "--glob", "!**/.git/*" },
        },
      },
    },
    keys = {
      {
        "<C-p>",
        function()
          require("telescope.builtin").find_files()
        end,
      },
      {
        "<leader>ff",
        function()
          require("telescope.builtin").live_grep()
        end,
      },
    },
  },
}
