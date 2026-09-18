# Changelog

All notable changes to this project template are documented in this file.

The template follows Semantic Versioning.

## [Unreleased]

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