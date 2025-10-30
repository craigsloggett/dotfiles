return {
  cmd = { "tflint", "--langserver" },
  filetypes = { "terraform" },
  root_markers = {
    ".terraform",
    ".terraform.lock.hcl",
    ".terraform-docs.yml",
    ".tflint.hcl",
    ".git"
  }
}
