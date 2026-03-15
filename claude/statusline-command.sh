#!/bin/sh

set -u

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

input="$(cat)"

model="$(printf '%s\n' "${input}" | jq -r '.model.display_name // empty')"
remaining="$(printf '%s\n' "${input}" | jq -r '.context_window.remaining_percentage // empty')"
cwd="$(printf '%s\n' "${input}" | jq -r '.workspace.current_dir // empty')"

# Read effort level from global settings.
effort=""
settings="${HOME}/.claude/settings.json"
if [ -f "${settings}" ]; then
  effort="$(jq -r '.effortLevel // empty' "${settings}" 2>/dev/null)"
fi

# Shorten home directory to ~.
short_cwd="$(printf '%s\n' "${cwd}" | sed "s|^${HOME}|~|")"

# Build status line: model effort · remaining% left · path
status=""
if [ -n "${model}" ]; then
  status="${model}"
  if [ -n "${effort}" ]; then
    status="${status} ${effort}"
  fi
fi

if [ -n "${remaining}" ]; then
  if [ -n "${status}" ]; then
    status="${status} · ${remaining}% left"
  else
    status="${remaining}% left"
  fi
fi

if [ -n "${short_cwd}" ]; then
  if [ -n "${status}" ]; then
    status="${status} · ${short_cwd}"
  else
    status="${short_cwd}"
  fi
fi

printf '%s' "${status}"
