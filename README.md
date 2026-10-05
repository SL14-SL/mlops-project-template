# Reusable MLOps Project Template

Reusable Copier template for production-oriented classification and
time-series forecasting projects.

The template provides a shared MLOps foundation while keeping data,
feature engineering, training and business logic project-specific.

## Quick start

Generate a new project directly from the latest reviewed template release:

```bash
uvx copier copy \
  --trust \
  --vcs-ref v0.4.2 \
  https://github.com/SL14-SL/mlops-project-template.git \
  my-mlops-project
```

Copier will prompt for the project name, repository slug, task type,
Python version and author information.

Use a tagged release for real projects. The `main` branch may contain
changes intended for the next template release.

## Supported project types

The template currently supports:

- classification
- forecasting

Both variants share the same operational structure but generate
task-specific request schemas, serving bundles, validation policies and
prediction services.

## Included components

Generated projects include:

- Python package using a `src` layout
- uv dependency management
- environment-specific YAML configuration
- local and Google Cloud Storage support
- immutable serving-release manifests
- active-release pointers and rollback support
- MLflow model loading
- thread-safe model management
- task-specific serving bundles
- FastAPI inference API
- API-key authentication
- health and readiness endpoints
- request IDs and safe API errors
- Prometheus metrics
- privacy-safe prediction event logging
- Docker and Docker Compose
- common Makefile commands
- GitHub Actions CI
- unit and integration tests

## Template boundaries

The template intentionally separates reusable infrastructure from
project-specific machine-learning logic.

| Shared template component | Project-specific implementation |
|---|---|
| Configuration loading | Dataset locations and source credentials |
| Storage abstraction | Dataset-specific storage layout |
| Release manifests | Required model artifacts |
| Model loading | Model framework and serialization format |
| Serving lifecycle | Feature preparation |
| Model manager | Training algorithm |
| FastAPI application | Prediction request fields |
| Authentication | Prediction response fields |
| Metrics middleware | Business metrics |
| Docker and CI | Cloud project and deployment settings |

The following components must normally be implemented or adapted after
generating a project:

- raw-data ingestion
- dataset validation rules
- feature engineering
- train/validation/test splitting
- model training
- hyperparameter tuning
- model evaluation
- business-specific prediction mapping
- performance and drift thresholds
- retraining rules
- cloud resource identifiers
- project documentation

## Requirements

Using the template requires:

- Python 3.12
- uv
- Copier
- GNU Make
- Docker
- Docker Compose

Local template development uses:

- Python 3.12.9
- uv 0.12.13

Install and synchronize the template development environment:

```bash
uv sync
```

## Generate a classification project

From a local clone of this repository:

```bash
uv run copier copy --defaults \
  --data project_name="Customer Churn Prediction" \
  --data project_slug="customer-churn-prediction" \
  --data task_type="classification" \
  . \
  generated/customer-churn-prediction
```

Initialize and validate the generated project:

```bash
cd generated/customer-churn-prediction

cp .env.example .env

make sync
make check
make api-config
```

## Generate a forecasting project

From a local clone of this repository:

```bash
uv run copier copy --defaults \
  --data project_name="Sales Forecasting" \
  --data project_slug="sales-forecasting" \
  --data task_type="forecasting" \
  . \
  generated/sales-forecasting
```

Initialize and validate the generated project:

```bash
cd generated/sales-forecasting

cp .env.example .env

make sync
make check
make api-config
```

## Run a generated API

Inside a generated project:

```bash
make api-rebuild
```

Check its status:

```bash
make api-ps
```

Test liveness:

```bash
curl \
  --fail \
  --show-error \
  --retry 30 \
  --retry-delay 2 \
  --retry-connrefused \
  http://localhost:8000/livez
```

Stop the stack:

```bash
make api-down
```

If port 8000 is already in use, change `API_PORT` in the generated
project's `.env` file.

## Repository structure

```text
.
├── .github
│   └── workflows
│       └── template-ci.yml
├── template
│   ├── .github
│   │   └── workflows
│   │       └── ci.yml
│   ├── configs
│   ├── src
│   │   └── {{ package_name }}
│   ├── tests
│   ├── Dockerfile.jinja
│   ├── Makefile
│   ├── README.md.jinja
│   ├── compose.yaml.jinja
│   └── pyproject.toml.jinja
├── copier.yml
├── pyproject.toml
└── uv.lock
```

The two CI workflows serve different purposes:

- `.github/workflows/template-ci.yml` tests the Copier template itself.
- `template/.github/workflows/ci.yml` is included in generated projects.

## Reference implementations

Two public reference projects demonstrate how the generated foundation
can be extended with project-specific machine-learning logic:

- [Time Series Forecasting MLOps Blueprint](https://github.com/SL14-SL/mlops-sales-forecasting)
- [Classification & Decisioning MLOps Blueprint](https://github.com/SL14-SL/mlops-churn-prediction)

These projects include domain-specific data pipelines, feature
engineering, training, monitoring, retraining and operational
documentation built on top of the shared template architecture.

## Development workflow

When changing a shared component:

1. Modify the source under `template/`.
2. Add or update the corresponding template tests.
3. Generate a fresh classification project.
4. Run Ruff and pytest.
5. Generate a fresh forecasting project.
6. Run Ruff and pytest.
7. Validate Docker Compose.
8. Start at least one generated API container.
9. Commit only the template source, not generated test projects.

A typical validation sequence is:

```bash
uv run copier copy --defaults \
  --vcs-ref HEAD \
  --data project_name="Classification Template Test" \
  --data project_slug="classification-template-test" \
  --data task_type="classification" \
  . \
  generated/classification-template-test
```

```bash
cd generated/classification-template-test

cp .env.example .env

make sync
make check
make api-config
```

Generated test projects under `generated/` are disposable and can be
deleted after validation.

## Copier updates

Generated projects should retain their Copier answers file so that later
template updates can be reviewed and applied with:

```bash
copier update
```

Before applying a template update to a real project:

1. Commit or stash all project changes.
2. Use a dedicated update branch.
3. Run `copier update`.
4. Review every generated diff.
5. Resolve conflicts without overwriting project-specific logic.
6. Run the complete project test suite.

## License

This project is available under the [MIT License](LICENSE).