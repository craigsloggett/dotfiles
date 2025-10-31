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

vim.keymap.set("n", "<C-p>", ":lua require('telescope.builtin').find_files()<CR>", { noremap = true, silent = true })
vim.keymap.set("n", "<leader>fg", ":lua require('telescope.builtin').live_grep()<CR>", { noremap = true, silent = true })
vim.keymap.set("n", "<leader>fb", ":lua require('telescope.builtin').buffers()<CR>", { noremap = true, silent = true })
