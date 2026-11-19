# Cloud provider verification

Offline verification on 2026-11-19. Baseline: `52f9004` (template v1.1.0).

All 12 variants were rendered with Copier and checked for provider/tier scope,
Python syntax, Ruff, GitHub Actions syntax and their generated pytest suites.
Tests use a shared Python 3.12 environment with the required dependencies; one
AWS classification end-to-end project was additionally synchronized and tested
with its own declared dependencies. No cloud stack was deployed.

| Variant | Passed tests |
|---|---:|
| `classification-api-gcp` | 315 |
| `classification-api-aws` | 315 |
| `classification-deployment-gcp` | 319 |
| `classification-deployment-aws` | 319 |
| `classification-end_to_end-gcp` | 645 |
| `classification-end_to_end-aws` | 707 |
| `forecasting-api-gcp` | 321 |
| `forecasting-api-aws` | 321 |
| `forecasting-deployment-gcp` | 325 |
| `forecasting-deployment-aws` | 325 |
| `forecasting-end_to_end-gcp` | 652 |
| `forecasting-end_to_end-aws` | 714 |

Copier updates from v0.2.0 answers completed without rejected changes for both
task types, defaulting the new cloud choice to GCP. Terraform formatting passed
for every generated cloud module. Trivy's enabled AWS configuration scan found
no HIGH/CRITICAL misconfigurations; API, training and managed MLflow were enabled
for that scan. Internal HTTP listeners retain resource-scoped documented exceptions.

Terraform initialization downloaded the locked providers. `terraform validate`
could not complete here: the runtime disallows the Unix socket needed by Terraform's
provider processes (`listen unix ...: socket: operation not permitted`). Docker is
unavailable in this environment, so image builds, container startup/smoke checks
and image vulnerability scans remain GitHub CI checks. These are not recorded as
passed by this report. Cloud IAM, networking, persistence and live serving still
need verification for each generated project and its model adapters.

## Reproduce

```bash
uv sync --locked
uv run python scripts/verify_cloud_matrix.py --tests
```

The command writes disposable projects below `generated/cloud-matrix`, creates their
lock files and runs each project's checks using its declared dependencies. It does
not run Terraform apply or start paid resources. GitHub's Template CI additionally
validates Terraform, builds images and runs container smoke/security checks.

The AWS forecasting reference implementation has separate live evidence. Its
success does not establish that every generated model adapter is production ready.
