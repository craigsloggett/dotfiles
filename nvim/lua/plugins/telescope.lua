vim.pack.add({
  {
    src = "https://github.com/nvim-telescope/telescope.nvim",
    version = vim.version.range("0.1.8")
  }
})

require("telescope").setup {
  defaults = {
    history = {
      path = vim.fn.stdpath("data") .. "/telescope/history"
    },
    vimgrep_arguments = {
      "rg",
      "--color=never",
      "--no-heading",
      "--with-filename",
      "--line-number",
      "--column",
      "--smart-case",
      "--hidden"
    }
  },
  pickers = {
    find_files = {
      find_command = { "rg", "--files", "--hidden", "--glob", "!**/.git/*" }
    },
    live_grep = {
      glob_pattern = "!**/.git/*"
    }
  }
}
