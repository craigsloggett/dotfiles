---
paths:
  - '**/*.tf'
  - '**/*.tfvars'
---

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
- Compose modules at the root, keeping the tree flat (one level of child modules); wire them together with expressions like `module.network.vpc_id` rather than nesting modules inside modules.
- Pass a module's dependencies in as input variables instead of creating them inside the module, so the root can rewire modules or swap inputs for data sources without changing the module.
- Don't write a module that detects whether an object exists and creates it conditionally; accept it as an input variable and let the caller pass either a managed `resource` or a `data` source.
- Type such a dependency variable as an `object({...})` listing only the attributes the module uses, so either a resource or a data source satisfies it.
- Declare provider configurations only in the root module; reusable modules must not contain `provider` blocks, which would break `count`, `for_each`, and `depends_on` on the module block.
- Pass providers to child modules implicitly by inheritance, or explicitly with the `providers` argument when a module needs a non-default or aliased configuration.
- Have every module declare its own provider requirements in a `required_providers` block (source and version), even though the configuration itself is shared from the root.
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
- Root modules: pin provider versions to an exact version: `5.0.0`. Always use the latest version available.
- Shared modules: constrain only the minimum provider version with `>=`, so callers can select a newer version other parts of their configuration need.
- Use `aws_iam_policy_document` data sources for IAM policies. They are type-safe, easier to read, and composable. Avoid inline `jsonencode` blocks for policy JSON.
- Encode assumptions (conditions that must hold for a resource to be usable) as `precondition` blocks and guarantees (behavior consumers rely on) as `postcondition` blocks, so violations fail early and in context with a clear `error_message`.
