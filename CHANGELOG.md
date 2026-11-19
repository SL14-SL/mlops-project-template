# Changelog

All notable changes to this project template are documented in this file.

The template follows Semantic Versioning.

## [Unreleased]

## [1.2.0] - 2026-11-19

### Added

- Explicit AWS/GCP selection across both tasks and all three tiers; 12 CI variants.
- AWS OIDC deployment/image rollback and Fargate lifecycle workflows.
- Optional durable MLflow on Fargate, RDS PostgreSQL and S3 with authenticated gateway.
- Portable model publication and shared evidence-driven retraining gates.
- Offline regression coverage for logical clocks, cooldown, evidence validation and publication.

### Changed

- Generate only the selected cloud provider infrastructure and workflows.
- Quickstart examples reference v1.2.0; GCP remains the default for existing answers.

### Fixed

- Format retraining flow names safely for longer generated project names.

### Verification

- All 34 PR checks passed, covering all twelve variants, Terraform validation,
  container smoke/security checks and template update compatibility.
- Generated cloud stacks still require account- and adapter-specific live verification.

## [1.1.0] - 2026-11-17

### Added

- Isolated training with local MLflow tracking and portable candidate export
  in the end-to-end tier.
- Non-root training images, Fargate S3 transport, SageMaker request generation,
  and scoped training infrastructure.
- Container training smoke tests, image scans and AWS training documentation.
- Verified Fargate training from a generated forecasting project on AWS,
  including S3/KMS access, artifact checksums and model reload.
- Screenshots and verification evidence documenting the successful cloud test
  and completed infrastructure cleanup.

### Changed

- Quickstart examples now reference v1.1.0.

### Fixed

- Preserve unset MLflow registry configuration and tracking environment
  variables after isolated training jobs.

### Limitations

- SageMaker cloud execution and non-root access to its mounted directories
  remain unverified.
- The generated API deployment remains unverified on AWS.
- Training candidates are not automatically registered, promoted or activated.
- AWS Terraform infrastructure remains experimental.


## [1.0.0] - 2026-11-17

### Added

- Explicit stability and compatibility policy for documented public interfaces.
- Compatibility tests verifying that project-owned trainers and evaluators
  remain unchanged and functional after updates from v0.6.2.
- Optional AWS dependencies, S3 storage configuration, and conditional
  serving-release pointer updates.
- AWS-enabled API container builds, prediction smoke tests, and image scans
  across all six project variants.
- Experimental AWS Terraform infrastructure for ECS/Fargate serving through
  an API Gateway HTTPS endpoint in deployment and end-to-end tiers.
- AWS deployment, operational limitations, and full teardown documentation.

### Changed

- Documented public contracts now follow the version 1.x compatibility policy.
- Generated project CI tests both default and AWS-enabled dependencies.
- Template CI validates generated AWS Terraform configuration.
- Quickstart examples now reference v1.0.0.

### Fixed

- Reject absolute cloud URIs and backslashes in release-relative artifact paths.
- Update OpenTelemetry dependencies in the template repository lockfile.

### Migration

- Existing 0.x projects should update on a dedicated branch, review generated
  changes, regenerate their dependency lock, and run project-specific tests.
- The compatibility guarantee starts with v1.0.0; pre-1.0 updates can require
  manual migration and conflict resolution.
- AWS Terraform remains experimental and is excluded from the stable
  infrastructure compatibility guarantee. The generated AWS deployment has
  not been verified end to end on AWS.
- AWS training jobs and SageMaker execution are not included.

## [0.6.2] - 2026-11-04

### Fixed

- Align the project version in `pyproject.toml` and `uv.lock` with the release tag.

## [0.6.1] - 2026-11-04

### Added

- Isolated Docker smoke tests across all six template variants. The tests load
  saved MLflow models through active serving releases and verify readiness,
  expected predictions, API-key authentication and input validation.
- `make smoke-test` for running the same checks locally in generated projects.

## [0.6.0] - 2026-11-03

### Changed

- forecasting bundles no longer require store metadata, store state,
  calendar artifacts or target-transformation metadata
- self-contained forecasting models can serve without extra release artifacts
- optional project artifacts are exposed through checksum-validated artifact URIs
- forecasting horizons count model steps without a fixed 366-step limit

### Added

- generic forecasting contract and migration guide
- sensor forecasting tests covering negative values, multiple series,
  optional artifacts and saved MLflow models

### Migration

- custom forecasting adapters must replace accesses to the former
  store-specific bundle fields with project-specific artifact handling

## [0.5.0] - 2026-11-03

### Added

- selectable API, deployment and end-to-end MLOps project tiers
- independent classification and forecasting selection for every tier
- CI coverage for all six project variants

### Changed

- generated files, dependencies, Compose services, Make targets and documentation
  follow the selected project tier
- cloud release export no longer depends on training promotion modules

### Fixed

- preserve end-to-end scope when updating projects without a project-tier answer
- restrict monitoring-stack exclusions to the project root

## [0.3.1] - 2026-09-24

### Added

- automated Copier upgrade compatibility tests from v0.2.0 to the current template
- project guide for safely applying future Copier template releases
- structured model-lifecycle events with logging and optional HTTP webhook
  delivery for rejected candidates, Challengers, Champions, serving releases
  and technical failures

### Fixed

- expose serving-bundle readiness as a Prometheus gauge and alert when the API
  is running without an active serving bundle

## [0.3.0] - 2026-09-18

### Added

- automated weekly dependency updates for Python, GitHub Actions, Docker and Terraform
- Python dependency auditing with documented vulnerability exceptions
- Trivy scanning for dependencies, secrets and infrastructure configuration
- blocking Trivy vulnerability scans for built API container images

### Changed

- GitHub Actions now use Node.js 24-compatible checkout actions
- CI runners are pinned to Ubuntu 24.04 for reproducible execution
- generated-project documentation explains creation and versioning of `uv.lock`

### Fixed

- outdated Debian runtime packages are upgraded during container builds
- container security scanning accounts for the temporary MLflow cryptography constraint

## [0.2.0] - 2026-09-18

### Added

- reusable contracts for data ingestion, feature engineering, splitting, model training and evaluation
- framework-independent training pipeline with lifecycle tracking, serialization and local or GCS-compatible persistence
- Prefect orchestration for project-specific training and complete model lifecycle execution
- local Prefect and MLflow services through optional Docker Compose profiles
- MLflow experiment logging, model artifact logging and approval-gated model registration
- challenger assignment, champion promotion and environment-specific promotion policies
- MLflow 3 logged-model URI support and end-to-end MLflow lifecycle integration tests
- immutable serving-release manifests, checksummed artifact publication and atomic active-release pointers
- automatic serving-release publication with champion restoration after publication failures
- local Prometheus, Grafana and Alertmanager monitoring stack
- API availability, error-rate, latency and service-level objective monitoring
- operational prediction metrics and task-specific output-distribution dashboards
- delayed ground-truth feedback contracts and classification or forecasting performance metrics
- feature-level drift metrics with project-specific extension points
- Google Cloud Terraform infrastructure for Artifact Registry, GCS, Secret Manager and Cloud Run
- protected GCS remote-state bootstrap and reproducible Terraform provider locks
- keyless GitHub Actions authentication through Workload Identity Federation
- two-phase Artifact Registry and Cloud Run deployment with separate plan and apply execution
- Cloud Run revision rollback workflow
- Google Cloud deployment guide and operations runbook

### Changed

- unified the training, registration, promotion and serving-release lifecycle
- separated infrastructure bootstrapping from Cloud Run deployment
- separated Cloud Run planning from explicit deployment approval
- moved API-key publication outside Terraform to prevent secret values from entering Terraform state
- expanded template CI to validate generated classification and forecasting projects

### Fixed

- restore the previous MLflow champion when serving-release publication fails
- register MLflow 3 logged models directly without run-artifact fallback

## [0.1.0] - 2026-09-15

### Added

- Copier-based project generation
- classification and forecasting project variants
- src-based Python package layout
- uv dependency management
- environment-specific YAML configuration
- local and Google Cloud Storage abstraction
- immutable serving-release manifests
- active-release pointers and rollback support
- MLflow model loading
- thread-safe model management
- task-specific serving bundles
- authenticated FastAPI prediction endpoint
- health, readiness and metrics endpoints
- request middleware and safe error responses
- privacy-safe prediction event logging
- Docker and Docker Compose support
- shared Makefile commands
- CI workflow for generated projects
- matrix CI workflow for the template repository
- unit and integration test suites