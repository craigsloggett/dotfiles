local opts = {
  noremap = true,
  silent = true
}

-- Window navigation.
vim.keymap.set("n", "<C-h>", "<C-w>h")
vim.keymap.set("n", "<C-j>", "<C-w>j")
vim.keymap.set("n", "<C-k>", "<C-w>k")
vim.keymap.set("n", "<C-l>", "<C-w>l")

-- Resize with arrows.
vim.keymap.set("n", "<C-Up>", "<Cmd>resize -2<CR>")
vim.keymap.set("n", "<C-Down>", "<Cmd>resize +2<CR>")
vim.keymap.set("n", "<C-Left>", "<Cmd>vertical resize -2<CR>")
vim.keymap.set("n", "<C-Right>", "<Cmd>vertical resize +2<CR>")

-- Open the Diagnostics floating window.
vim.keymap.set("n", "<leader>e", ":lua vim.diagnostic.open_float()<CR>", opts)

-- Keep lines selected after an indentation change.
vim.keymap.set("v", "<", "<gv")
vim.keymap.set("v", ">", ">gv")

-- Vertical split.
vim.keymap.set("n", "<leader>v", "<Cmd>vsplit<CR>")
