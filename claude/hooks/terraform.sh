#!/bin/sh
#
# hooks/terraform.sh
#
# Format, lint, and validate the Terraform files among the given paths.

set -euf

for utility in terraform tflint; do
  command -v "${utility}" >/dev/null 2>&1 || exit 0
done

for file in "$@"; do
  shift

  case ${file} in
    *.tf | *.tfvars) ;;
    *) continue ;;
  esac

  [ -f "${file}" ] || continue

  set -- "$@" "${file}"
done

[ "$#" -gt 0 ] || exit 0

terraform fmt -no-color -list=false "$@" >&2 || exit 2

directories="$(for file in "$@"; do dirname "${file}"; done | sort -u)"

IFS='
'

status=0
for directory in ${directories}; do
  tflint --chdir "${directory}" --no-color >&2 || status=2

  [ -d "${directory}/.terraform" ] || continue

  terraform -chdir="${directory}" validate -no-color >&2 || status=2
done
exit "${status}"
