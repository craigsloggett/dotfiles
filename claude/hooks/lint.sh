#!/bin/sh
#
# hooks/lint.sh
#
# Lint files after Claude finishes responding

set -euf

HOOK_INPUT="$(cat)"
readonly HOOK_INPUT

check_stop_hook_active_field() (
  # https://code.claude.com/docs/en/hooks-guide#stop-hook-runs-forever
  if [ "$(printf '%s' "${HOOK_INPUT}" | jq -r '.stop_hook_active')" = "true" ]; then
    return 1
  fi
)

check_prerequisites() {
  for utility in actionlint golangci-lint jq shellcheck tflint yamllint; do
    command -v "${utility}" >/dev/null 2>&1 || return 1
  done
}

block_with_reason() (
  reason="$1"
  jq -n --arg reason "${reason}" '{decision: "block", reason: $reason}'
)

lint_github_actions() (
  actionlint 2>&1
)

lint_go() (
  golangci-lint run --fix ./... >/dev/null 2>&1 || true

  if golangci_lint_output="$(golangci-lint run ./... 2>&1)"; then
    return 0
  else
    printf '%s' "${golangci_lint_output}"
    return 1
  fi
)

lint_shell() (
  find . -name '*.sh' -not -path '*/.git/*' -print0 |
    xargs -0 shellcheck 2>&1
)

lint_terraform() (
  tflint_plugin_dir="${TFLINT_PLUGIN_DIR:-.tflint.d}"

  [ -d "${tflint_plugin_dir}" ] || tflint --init >/dev/null 2>&1 || true

  tflint --recursive --format=compact 2>&1
)

lint_yaml() (
  yamllint . 2>&1
)

main() {
  check_stop_hook_active_field || return 0
  check_prerequisites || return 0

  [ -n "${CLAUDE_PROJECT_DIR:-}" ] || return 0
  cd "${CLAUDE_PROJECT_DIR}" || return 0

  combined_output=""

  # GitHub Actions
  if [ -d .github/workflows ]; then
    if ! lint_github_actions_output="$(lint_github_actions)"; then
      combined_output="${combined_output}
=== GitHub Actions ===
${lint_github_actions_output}"
    fi
  fi

  # Go
  if [ -f go.mod ]; then
    if ! lint_go_output="$(lint_go)"; then
      combined_output="${combined_output}
=== Go ===
${lint_go_output}"
    fi
  fi

  # Shell
  if find . -name '*.sh' -not -path '*/.git/*' | grep -q .; then
    if ! lint_shell_output="$(lint_shell)"; then
      combined_output="${combined_output}
=== Shell ===
${lint_shell_output}"
    fi
  fi

  # Terraform
  if find . -name '*.tf' -not -path '*/.terraform/*' | grep -q .; then
    if ! lint_terraform_output="$(lint_terraform)"; then
      combined_output="${combined_output}
=== Terraform ===
${lint_terraform_output}"
    fi
  fi

  # YAML
  if find . \( -name '*.yaml' -o -name '*.yml' \) -not -path '*/.git/*' | grep -q .; then
    if ! lint_yaml_output="$(lint_yaml)"; then
      combined_output="${combined_output}
=== YAML ===
${lint_yaml_output}"
    fi
  fi

  if [ -n "${combined_output}" ]; then
    block_with_reason "Linters reported issues:${combined_output}"
  fi
}

main "$@"
