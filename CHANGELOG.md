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