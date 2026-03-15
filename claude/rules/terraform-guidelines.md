---
paths:
  - "**/*.tf"
  - "**/*.tfvars"
---

# Terraform Guidelines

## HCL Conventions

- Use `snake_case` for all resource names, variable names, and output names.
- Use descriptive names: `aws_s3_bucket.application_logs`, not `aws_s3_bucket.bucket1`.
- Group related arguments logically. Separate groups with blank lines.
- Use `#` comments sparingly. The code should be self-documenting.

## File Structure

- `main.tf` — Primary resources and data sources.
- `variables.tf` — Input variable declarations.
- `outputs.tf` — Output declarations.
- `versions.tf` — Required providers and Terraform version constraints.
- `locals.tf` — Local values (only when needed).
- `data.tf` — Data sources (if there are many, otherwise keep in `main.tf`).

## Module Structure

- Modules go in `modules/<name>/`.
- Every module has `variables.tf`, `outputs.tf`, `main.tf`, and `versions.tf`.
- Keep modules focused on a single concern.
- Document required vs optional variables with `description` and `default`.
- Use `validation` blocks for input constraints.

## Variables

- Always include a `description` for every variable.
- Use `type` constraints. Prefer specific types over `any`.
- Set sensible `default` values where appropriate. Required variables have no default.
- Use `sensitive = true` for secrets.

## State Management

- Never edit state files manually. Use `terraform state` commands.
- Use remote state backends for shared infrastructure.
- Use `terraform state list` and `terraform state show` for inspection.
- Be cautious with `terraform state rm` and `terraform import`. Confirm before running.

## Formatting and Validation

- Run `terraform fmt` before committing. Code must be formatted.
- Run `terraform validate` to catch syntax and configuration errors.
- Use `tflint` for additional linting rules.
- Review `terraform plan` output carefully before applying.

## Patterns

- Use `count` for simple conditional resources. Use `for_each` for collections.
- Avoid `depends_on` unless absolutely necessary. Implicit dependencies are preferred.
- Use `moved` blocks for resource renames to avoid destroy/recreate.
- Pin provider versions to minor version ranges: `~> 5.0`.
- Use `aws_iam_policy_document` data sources for IAM policies. They are type-safe, easier to read, and composable. Avoid inline `jsonencode` blocks for policy JSON.
