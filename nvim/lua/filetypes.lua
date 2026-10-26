vim.filetype.add({
  filename = {
    [".yamlfmt"] = "yaml"
  }
})

vim.filetype.add({
  pattern = {
    [".*/%.github/workflows/.*%.ya?ml"] = "yaml.ghaction"
  }
})
