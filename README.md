# MLOps Project Template

Reusable project template for production-oriented machine-learning systems.

## Supported project types

- Classification
- Time-series forecasting

## Design principles

- Generated projects are fully standalone.
- Shared infrastructure is kept separate from domain-specific ML logic.
- Classification and forecasting use explicit implementations.
- Generated projects do not depend on this template at runtime.
- Infrastructure components are optional where practical.
- Every generated project includes tests and operational documentation.

## Planned platform components

- FastAPI model serving
- MLflow experiment tracking and model registry
- Prefect workflow orchestration
- Docker and Docker Compose
- Prometheus and Grafana monitoring
- Terraform deployment for Google Cloud
- GitHub Actions CI/CD
- Controlled model promotion and rollback

## Status

The template is currently under development.