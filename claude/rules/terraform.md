---
paths:
  - '**/*.tf'
  - '**/*.tfvars'
---

## HCL Conventions

- Use `snake_case` for all resource names, variable names, and output names.
- Use descriptive names: `aws_s3_bucket.application_logs`, not `aws_s3_bucket.bucket1`.
- Don't include the resource type in a resource name; the address already carries it (`aws_instance.web_api`, not `aws_instance.web_api_instance`).
- Define resources and data sources after what they reference so the code builds on itself; place a data source before the resource that uses it.
- Order resource parameters: `count`/`for_each` first, then non-block arguments, then nested blocks, then `lifecycle`, then `depends_on`.
- Group related arguments logically.
- Separate argument groups with blank lines.
- Use `#` comments sparingly. The code should be self-documenting.

## File Structure

- `main.tf` — All resource and data source blocks.
- `terraform.tf` — A single `terraform` block defining `required_version` and `required_providers`.
- `backend.tf` — Backend configuration.
- `providers.tf` — All provider blocks and configuration.
- `variables.tf` — Input variable blocks, in alphabetical order.
- `outputs.tf` — Output blocks, in alphabetical order.
- `locals.tf` — Local values (only when needed).
- Split resources and data sources into files by logical group (e.g. `network.tf`, `compute.tf`) as the configuration grows.

## Module Structure

- Modules go in `modules/<name>/`.
- Every module has `variables.tf`, `outputs.tf`, `main.tf`, and `terraform.tf`.
- Keep modules focused on a single concern.
- Compose modules at the root, keeping the tree flat (one level of child modules); wire them together with expressions like `module.network.vpc_id` rather than nesting modules inside modules.
- Pass a module's dependencies in as input variables instead of creating them inside the module, so the root can rewire modules or swap inputs for data sources without changing the module.
- Don't write a module that detects whether an object exists and creates it conditionally; accept it as an input variable and let the caller pass either a managed `resource` or a `data` source.
- Type such a dependency variable as an `object({...})` listing only the attributes the module uses, so either a resource or a data source satisfies it.
- Declare provider configurations only in the root module; reusable modules must not contain `provider` blocks, which would break `count`, `for_each`, and `depends_on` on the module block.
- Pass providers to child modules implicitly by inheritance, or explicitly with the `providers` argument when a module needs a non-default or aliased configuration.
- Have every module declare its own provider requirements in a `required_providers` block (source and version), even though the configuration itself is shared from the root.
- Always include a default provider configuration (a `provider` block with no `alias`), and define the default before any aliased providers.
- Give a non-default provider its `alias` as the block's first argument.
- Document required vs optional variables with `description` and `default`.

## Variables

- Always include a `description` for every variable.
- Use `type` constraints. Prefer specific types over `any`.
- Set sensible `default` values where appropriate.
- Give required variables no `default`.
- Use `sensitive = true` for secrets.
- Order variable parameters: type, description, default, sensitive, validation.

## Outputs

- Include a `type` and `description` for every output.
- Order output parameters: type, description, value, sensitive.

## Local Values

- Use local values sparingly; overuse obscures intent.
- Define a local in `locals.tf` if referenced across files, or at the top of the single file that uses it.

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

- Use `count` for simple conditional resources.
- Use `for_each` for collections.
- Avoid `depends_on` unless absolutely necessary. Implicit dependencies are preferred.
- Use `moved` blocks for resource renames to avoid destroy/recreate.
- Root modules: pin provider versions to an exact version (`5.0.0`).
- Pin to the latest version available.
- Shared modules: constrain only the minimum provider version with `>=`, so callers can select a newer version other parts of their configuration need.
- Use `aws_iam_policy_document` data sources for IAM policies. They are type-safe, easier to read, and composable. Avoid inline `jsonencode` blocks for policy JSON.
- Pin registry module sources with `version`.

## Configuration Validation

- Reserve variable `validation` blocks for uniquely restrictive input requirements beyond type checking; they run at plan time.
- Encode assumptions (conditions that must hold for a resource to be usable) as `precondition` blocks and guarantees (behavior consumers rely on) as `postcondition` blocks, so violations fail early and in context with a clear `error_message`.
- Use `check` blocks to verify resources behave as expected without blocking operations when the assertion fails.
- Choose a validation method by whether it should block operations and which workflow phase it runs in.

## Tests

- Write tests for modules using Terraform tests.
