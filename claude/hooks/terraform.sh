#!/bin/sh
#
# hooks/terraform.sh
#
# Format, lint, and validate the Terraform files among the given paths.

set -euf

for utility in terraform tflint; do
  command -v "${utility}" >/dev/null 2>&1 || exit 0
done

files=""
for file in "$@"; do
  case ${file} in
    *.tf | *.tfvars) ;;
    *) continue ;;
  esac

  [ -f "${file}" ] || continue

  files="${files}${file}
"
done

[ -n "${files}" ] || exit 0

printf '%s' "${files}" | xargs terraform fmt -no-color -list=false >&2 || exit 2

directories="$(printf '%s' "${files}" | xargs -n1 dirname | sort -u)"

status=0
for directory in ${directories}; do
  tflint --chdir "${directory}" --no-color >&2 || status=2

  [ -d "${directory}/.terraform" ] || continue

  terraform -chdir="${directory}" validate -no-color >&2 || status=2
done
exit "${status}"
