return {
  cmd = { "terraform-ls", "serve" },
  filetypes = { "terraform", "terraform-vars" },
  root_markers = {
    ".terraform",
    ".terraform.lock.hcl",
    ".terraform-docs.yml",
    ".tflint.hcl",
    ".git"
  }
}
