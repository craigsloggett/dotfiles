#!/bin/sh
# Stop hook: incrementally append the latest turn to .claude/context/turns-<session_id>.md.

set -u

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

# Read hook input from stdin.
input="$(cat)"

# Skip subagent invocations.
agent_id="$(printf '%s\n' "${input}" | jq -r '.agent_id // empty')"
if [ -n "${agent_id}" ]; then
  exit 0
fi

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

# State directory for tracking processed line counts.
state_dir="${XDG_STATE_HOME:-${HOME}/.local/state}/claude"
mkdir -p "${state_dir}"
state_file="${state_dir}/${session_id}.lines"

# Output file.
output_dir="${cwd}/.claude/context"
mkdir -p "${output_dir}"
output="${output_dir}/turns-${session_id}.md"

# Read last processed line count (0 if first run).
last_line=0
if [ -f "${state_file}" ]; then
  last_line="$(cat "${state_file}")"
fi

# Get current line count.
current_line="$(wc -l <"${transcript_path}" | tr -d ' ')"

# Nothing new to process.
if [ "${current_line}" -le "${last_line}" ]; then
  exit 0
fi

# Extract new lines and format as markdown.
tail -n +"$((last_line + 1))" "${transcript_path}" | jq -r '
  if .type == "user" and (.message.content | type) == "string" and (.message.content | length) > 0 then
    "## User\n\n" + .message.content + "\n"
  elif .type == "assistant" and .message.content then
    [.message.content[] |
      if .type == "text" and (.text | length) > 0 then
        "## Assistant\n\n" + .text + "\n"
      elif .type == "tool_use" then
        "> **Tool:** `" + .name + "`\n"
      else empty
      end
    ] | join("\n")
  else empty
  end
' >>"${output}"

# Update state.
printf '%s\n' "${current_line}" >"${state_file}"

exit 0
