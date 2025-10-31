return {
  cmd = { "tflint", "--langserver" },
  filetypes = { "terraform" },
  root_markers = {
    ".terraform",
    ".terraform.lock.hcl",
    ".tflint.hcl",
    ".git"
  }
}
