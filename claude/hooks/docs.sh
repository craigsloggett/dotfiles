#!/bin/sh
#
# docs.sh - regenerate documentation after Claude edits
#
# Called as a PostToolUse hook. Reads JSON from stdin
# to extract the file path, then runs the appropriate
# documentation generator. Tracks generated files to a
# per-session state file for the lint Stop hook to review.

set -u

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

# Read tool context from stdin.
input="$(cat)"

# Extract the file path and session ID from the hook input.
file_path="$(printf '%s\n' "${input}" | jq -r '.tool_input.file_path // empty')"
session_id="$(printf '%s\n' "${input}" | jq -r '.session_id // empty')"

if [ -z "${file_path}" ]; then
  exit 0
fi

# Determine the file extension.
ext="${file_path##*.}"

case "${ext}" in
  tf)
    if ! command -v terraform-docs >/dev/null 2>&1; then
      exit 0
    fi

    # Find the project root by walking up to .git.
    dir="$(dirname "${file_path}")"
    while [ "${dir}" != "/" ]; do
      if [ -d "${dir}/.git" ]; then
        break
      fi
      dir="$(dirname "${dir}")"
    done

    readme="${dir}/README.md"
    terraform-docs markdown table "${dir}" --output-file README.md 2>/dev/null

    # Only track if the README actually changed.
    if [ -n "${session_id}" ] && [ -f "${readme}" ]; then
      changed=false
      if command -v git >/dev/null 2>&1 && git -C "${dir}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        if git -C "${dir}" diff --quiet -- "${readme}" 2>/dev/null; then
          changed=false
        else
          changed=true
        fi
      fi
      if [ "${changed}" = "true" ]; then
        state_dir="${XDG_STATE_HOME:-${HOME}/.local/state}/claude"
        mkdir -p "${state_dir}"
        printf '%s\n' "${readme}" >>"${state_dir}/edited-docs-${session_id}"
      fi
    fi
    ;;
esac

exit 0
