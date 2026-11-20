# Stability and compatibility policy

This policy applies to template releases starting with version 1.0.0.

## Supported project variants

The template supports classification and forecasting projects, each with
the api, deployment, and end_to_end tiers.

The tier defines the generated scope. It does not implement project-specific
data ingestion, feature engineering, training, or business rules.

## Stable interfaces

Within version 1.x, compatibility is maintained for:

- Existing documented Copier answer names and values, including task_type,
  project_tier, project_name, project_slug, and package_name.
- The documented prediction request and response contracts for classification
  and forecasting.
- API-key authentication through the X-API-Key header.
- The documented liveness and readiness endpoints.
- Serving-release manifest schema version 1 and active-pointer schema version 1.
- Relative, checksum-validated artifact references within serving releases.
- Documented configuration keys and environment-variable meanings.
- The ModelTrainer and ModelEvaluator protocols and their TrainingResult
  and EvaluationResult contracts in the end_to_end tier.
- The forecasting model-adapter contract documented in generated projects.

Optional fields, configuration options, and new capabilities may be added
in compatible minor releases. Existing supported inputs must retain their
documented meaning.

Private helpers, undocumented internal functions, dependency versions,
log messages, generated resource IDs, and exact error-message wording
are not stable interfaces.

## Versioning

- PATCH releases contain compatible fixes.
- MINOR releases add compatible functionality or deprecations.
- MAJOR releases may change stable interfaces incompatibly.

An incompatible change to a stable interface requires a new major release
and migration documentation.

Deprecation notices identify the affected interface and its replacement.
Deprecated stable interfaces remain available for the rest of the current
major version unless a documented security issue requires otherwise.

## Generated projects and updates

A generated project is owned by its user. Applying a Copier update is an
explicit source-code migration, not an automatic application upgrade.

Before updating:

1. Commit the current project.
2. Create a dedicated update branch.
3. Apply the target template release.
4. Review generated changes and resolve conflicts.
5. Regenerate the dependency lock when required.
6. Run project-specific tests and container smoke tests.

Compatibility does not mean arbitrary edits to template-owned files can
always be merged automatically. Such edits may require manual conflict
resolution.

Project-specific implementations using documented stable contracts should
continue to work across compatible template updates. Changing a project's
tier or task type is a separate migration and may remove generated files.

The stability guarantee starts at 1.0.0. Earlier 0.x projects may require
migration work when upgrading to 1.0.0.

## Experimental AWS infrastructure

The AWS Terraform deployment remains experimental in version 1.0.0.

S3 helpers and AWS-enabled API containers are covered by automated tests.
The generated AWS infrastructure is initialized and validated with Terraform,
but has not been verified end to end on AWS.

The experimental designation covers AWS Terraform resource layout, deployment
procedures, and infrastructure defaults. These may change within version 1.x,
with changes and migration requirements documented in the changelog.

This exception does not remove the compatibility guarantees for the stable
configuration and serving-release contracts listed above.

## What version 1.0.0 does not promise

Version 1.0.0 does not certify a generated application for production.

Model quality, data protection, application security, operational readiness,
cloud costs, and project-specific behavior require validation for each use case.

Cloud deployment and infrastructure changes remain explicit operator actions.
Template generation and Copier updates do not deploy infrastructure.