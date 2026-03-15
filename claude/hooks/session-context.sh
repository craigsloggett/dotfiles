#!/bin/sh
# SessionEnd hook: extract session transcript to .claude/context/session-<timestamp>-<session_id>.md.

set -u

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

input="$(cat)"
transcript_path="$(printf '%s\n' "${input}" | jq -r '.transcript_path // empty')"
cwd="$(printf '%s\n' "${input}" | jq -r '.cwd // empty')"
session_id="$(printf '%s\n' "${input}" | jq -r '.session_id // empty')"

if [ -z "${transcript_path}" ] || [ ! -f "${transcript_path}" ]; then
  exit 0
fi

if [ -z "${cwd}" ] || [ ! -d "${cwd}" ]; then
  exit 0
fi

if [ -z "${session_id}" ]; then
  exit 0
fi

timestamp="$(date -u +%Y-%m-%dT%H-%M-%S)"
output_dir="${cwd}/.claude/context"
mkdir -p "${output_dir}"
output="${output_dir}/session-${timestamp}-${session_id}.md"

jq -r '
  if .type == "user" and (.message.content | type) == "string" and (.message.content | length) > 0 then
    "## User\n\n" + .message.content + "\n"
  elif .type == "assistant" and .message.content then
    [.message.content[] |
      if .type == "text" then
        "## Assistant\n\n" + .text + "\n"
      elif .type == "tool_use" then
        "> **Tool:** `" + .name + "`\n"
      else empty
      end
    ] | join("\n")
  else empty
  end
' "${transcript_path}" >"${output}"

# Clean up the turns state file for this session.
rm -f "${XDG_STATE_HOME:-${HOME}/.local/state}/claude/${session_id}.lines" 2>/dev/null
