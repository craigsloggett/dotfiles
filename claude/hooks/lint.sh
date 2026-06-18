#!/bin/sh
#
# hooks/lint.sh
#
# Lint the files worked on after Claude finishes responding

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
  for utility in actionlint golangci-lint jq shellcheck swiftlint tflint yamllint; do
    command -v "${utility}" >/dev/null 2>&1 || return 1
  done
}

block_with_reason() (
  reason="$1"
  jq -n --arg reason "${reason}" '{decision: "block", reason: $reason}'
)

# filter_worked_files reads paths on stdin and prints those that live under
# project_dir and still exist, one per line.
filter_worked_files() (
  project_dir="$1"
  while IFS= read -r file_path; do
    case "${file_path}" in
      "${project_dir}"/*)
        [ -f "${file_path}" ] || continue
        printf '%s\n' "${file_path}"
        ;;
    esac
  done
)

# files_matching prints the worked files whose path matches regex, one per line.
files_matching() (
  files="$1"
  regex="$2"
  printf '%s\n' "${files}" | grep -E "${regex}" || true
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

# lint_shell runs shellcheck on the given newline-separated shell files.
lint_shell() (
  files="$1"
  IFS='
'
  # Split on newline IFS into positional parameters; set -f disables globbing.
  # shellcheck disable=SC2086
  set -- ${files}
  shellcheck -x "$@" 2>&1
)

# lint_swift runs swiftlint on the given newline-separated Swift files.
lint_swift() (
  files="$1"
  IFS='
'
  # Split on newline IFS into positional parameters; set -f disables globbing.
  # shellcheck disable=SC2086
  set -- ${files}
  swiftlint lint --quiet "$@" 2>&1
)

lint_terraform() (
  tflint_plugin_dir="${TFLINT_PLUGIN_DIR:-.tflint.d}"

  [ -d "${tflint_plugin_dir}" ] || tflint --init >/dev/null 2>&1 || true

  tflint --recursive --format=compact 2>&1
)

# lint_yaml runs yamllint on the given newline-separated YAML files.
lint_yaml() (
  files="$1"
  IFS='
'
  # Split on newline IFS into positional parameters; set -f disables globbing.
  # shellcheck disable=SC2086
  set -- ${files}
  yamllint "$@" 2>&1
)

main() {
  check_stop_hook_active_field || return 0
  check_prerequisites || return 0

  [ -n "${CLAUDE_PROJECT_DIR:-}" ] || return 0
  cd "${CLAUDE_PROJECT_DIR}" || return 0

  session_id="$(printf '%s' "${HOOK_INPUT}" | jq -r '.session_id // empty')"
  [ -n "${session_id}" ] || return 0

  state_file="${XDG_STATE_HOME:-${HOME}/.local/state}/claude/worked-files/${session_id}"
  [ -f "${state_file}" ] || return 0

  # Consume the list: dedupe and keep only existing project files, then drop the
  # state file so the next turn lints only its own edits.
  worked_files="$(sort -u "${state_file}" | filter_worked_files "${CLAUDE_PROJECT_DIR}")"
  rm -f "${state_file}"

  [ -n "${worked_files}" ] || return 0

  workflow_path_regex='/\.github/workflows/[^/]+\.ya?ml$'

  shell_files="$(files_matching "${worked_files}" '\.sh$')"
  swift_files="$(files_matching "${worked_files}" '\.swift$')"
  yaml_files="$(files_matching "${worked_files}" '\.ya?ml$')"
  go_files="$(files_matching "${worked_files}" '\.go$')"
  tf_files="$(files_matching "${worked_files}" '\.tf$')"
  workflow_files="$(files_matching "${worked_files}" "${workflow_path_regex}")"

  combined_output=""

  # GitHub Actions (actionlint scans .github/workflows; run it if one changed)
  if [ -n "${workflow_files}" ]; then
    if ! lint_github_actions_output="$(lint_github_actions)"; then
      combined_output="${combined_output}
=== GitHub Actions ===
${lint_github_actions_output}"
    fi
  fi

  # Go (golangci-lint resolves packages, so run project-scope when any .go changed)
  if [ -n "${go_files}" ]; then
    if ! lint_go_output="$(lint_go)"; then
      combined_output="${combined_output}
=== Go ===
${lint_go_output}"
    fi
  fi

  # Shell
  if [ -n "${shell_files}" ]; then
    if ! lint_shell_output="$(lint_shell "${shell_files}")"; then
      combined_output="${combined_output}
=== Shell ===
${lint_shell_output}"
    fi
  fi

  # Swift
  if [ -n "${swift_files}" ]; then
    if ! lint_swift_output="$(lint_swift "${swift_files}")"; then
      combined_output="${combined_output}
=== Swift ===
${lint_swift_output}"
    fi
  fi

  # Terraform (tflint runs recursively; gate on a changed .tf and a config)
  if [ -f .tflint.hcl ] && [ -n "${tf_files}" ]; then
    if ! lint_terraform_output="$(lint_terraform)"; then
      combined_output="${combined_output}
=== Terraform ===
${lint_terraform_output}"
    fi
  fi

  # YAML
  if [ -n "${yaml_files}" ]; then
    if ! lint_yaml_output="$(lint_yaml "${yaml_files}")"; then
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
