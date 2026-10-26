#!/bin/sh

input=$(cat)
file_path=$(printf '%s' "${input}" | jq -r '.tool_input.file_path // empty')
cwd=$(printf '%s' "${input}" | jq -r '.cwd // empty')

[ -n "${file_path}" ] || {
  echo 1
  exit 0
}

case ${file_path} in
  /*)
    ;;
  *)
    file_path="${cwd}/${file_path}"
    ;;
esac

file_dirname=$(dirname "${file_path}")

if git -C "${file_dirname}" ls-files --error-unmatch -- "${file_path}" >/dev/null 2>&1; then
  echo 0
else
  echo 1
fi
