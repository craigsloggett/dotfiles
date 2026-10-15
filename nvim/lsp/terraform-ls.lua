return {
  cmd = { "terraform-ls", "serve", "-log-file", "/dev/null" },
  filetypes = { "terraform", "terraform-vars" },
  root_markers = {
    ".terraform",
    ".terraform.lock.hcl",
    ".git"
  }
}
