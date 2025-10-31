vim.filetype.add({
  pattern = {
    -- GitHub Actions
    [".*/%.github/workflows/.*%.ya?ml"] = "yaml.ghaction",
  },
})
