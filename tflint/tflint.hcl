config {
  format              = "default"
  force               = false
  disabled_by_default = false
}

rule "terraform_module_pinned_source" {
  enabled = true
  style   = "semver"
}

rule "terraform_module_version" {
  enabled = true
  exact   = true
}

rule "terraform_naming_convention" {
  enabled = true
  format  = "snake_case"
}

plugin "terraform" {
  enabled = true
  version = "0.5.0"
  source  = "github.com/terraform-linters/tflint-ruleset-terraform"
  preset  = "all"
}

