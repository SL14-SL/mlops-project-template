# Changelog

All notable changes to this project template are documented in this file.

The template follows Semantic Versioning.

## [Unreleased]

### Added

- reusable contracts for ingestion, feature engineering and dataset splitting
- reusable model training and evaluation contracts
- framework-independent training pipeline runner
- immutable lifecycle status model for training-pipeline runs
- lifecycle tracking for framework-independent training runs
- versioned JSON serialization for pipeline lifecycle records
- local and GCS-compatible persistence for pipeline lifecycle records
- configuration-based repository for pipeline lifecycle records
- configured training pipeline service with automatic lifecycle persistence
- thin Prefect adapter for configured training pipelines
- explicit project-specific training pipeline extension point
- executable project-specific Prefect training flow entrypoint
- optional local Prefect server through a Docker Compose profile
- version-controlled local Prefect training deployment
- optional persistent local MLflow tracking server
- shared MLflow training run and result logging adapter
- approval-gated MLflow model registration
- explicit challenger assignment and champion promotion for MLflow models
- direction-aware metric gate for champion promotion
- MLflow-backed candidate-to-champion evaluation and conditional promotion
- unified model candidate lifecycle for registration, challenger assignment and champion promotion
- environment-specific promotion policies for classification and forecasting
- configuration-driven model lifecycle entrypoint
- MLflow logging for model evaluation metrics and approval decisions
- Prefect adapter for the complete MLflow model lifecycle
- executable Prefect training flow for the complete model lifecycle
- public MLflow run-context helper for project-specific model trainers
- project-specific MLflow model artifact logging contract
- model artifact logger dependency for configured training pipelines
- model artifact logging inside the active MLflow training run
- immutable serving-release manifest builder for promoted champion models
- local and GCS-compatible serving artifact publisher with checksums and cleanup
- validated serving-release publication with atomic active-pointer activation
- project-specific serving-release input provider contract

### Changed

### Fixed

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