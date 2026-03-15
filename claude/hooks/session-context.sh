#!/bin/sh
# SessionEnd hook: extract session transcript to CONTEXT.md in the working directory.

set -u

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

input=$(cat)
transcript_path=$(printf '%s\n' "${input}" | jq -r '.transcript_path // empty')
cwd=$(printf '%s\n' "${input}" | jq -r '.cwd // empty')

if [ -z "${transcript_path}" ] || [ ! -f "${transcript_path}" ]; then
  exit 0
fi

if [ -z "${cwd}" ] || [ ! -d "${cwd}" ]; then
  exit 0
fi

output="${cwd}/CONTEXT.md"

jq -r '
  if .type == "user" and .message.content then
    "## User\n\n" + (.message.content | tostring) + "\n"
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
' "${transcript_path}" > "${output}"
