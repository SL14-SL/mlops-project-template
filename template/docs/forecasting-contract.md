# Domain-independent forecasting contract

The forecasting template serves any numeric target: temperature, energy,
traffic, inventory or other time series. It does not prescribe a domain,
entity identifier, timestamp column, data frequency or non-negative target.

## Request and model responsibilities

`inputs` is a non-empty batch of model-specific feature records. The model
adapter defines what each record represents. For example, one record can
contain the recent history of one sensor; a batch can contain several sensors.
An identifier such as `sensor_id` or `series_id` is optional unless the model
requires it. The template does not infer grouping from rows or column names.

`horizon` is a positive integer counting model steps, not necessarily days.
The model's `predict(frame, params={"horizon": horizon})` adapter must return
one finite numeric value per input record per step, flattened in row-major
order. For two input records and a horizon of three, the order is row 0 steps
1–3, then row 1 steps 1–3. The API returns `row_index` and `horizon_step` so
clients can associate each value with their input record.

An MLflow pyfunc wrapper must declare the `horizon` inference parameter in
its model signature. Training, lag creation, recursive forecasting, inverse
transformations, history handling and future covariates belong to the model
wrapper or the project's adapter. Predictions must already be in target units;
the generic service neither exponentiates nor clips values. Models and clients
should enforce use-case-specific horizon and batch limits.

## Optional release artifacts

A self-contained model needs no extra serving artifacts: `artifacts: {}` and
empty metadata are valid for forecasting. Package model-owned preprocessing
and state with the MLflow model where possible.

Projects may attach arbitrary immutable files to a release. Their names and
formats are not predefined. The loader validates checksums and exposes paths
as `bundle.artifact_uris`. For example, a sensor application may attach
`sensor_calibration` referencing `calibration.json`. If required by the project,
list that name under `metadata.required_artifacts`.

```yaml
metadata:
  required_artifacts:
    - sensor_calibration
```

Declared names must be unique non-empty strings and exist in the manifest's
artifact mapping. No calendar, entity metadata, history file or transformation
label is mandatory by default. The standard prediction service does not
silently pass these extra files to the model; a project adapter explicitly
consumes them. This avoids assuming a universal feature engineering procedure.

## Migration from template v0.5.0

The previous forecasting bundle required retail-oriented fields and eagerly
loaded dataframes and JSON state. The generic bundle removes these typed
fields. Custom code that accessed them must read the appropriate
`artifact_uris` entry or package the data inside the model instead.

Existing manifest artifact names remain legal arbitrary keys and retain
checksum verification. A `target_transformation` metadata label can remain as
descriptive project metadata; the template does not apply a transformation.
Keep existing artifacts during migration when your model still needs them.
Review Copier update conflicts and migrate custom adapter code before deploying.
Classification's feature schema and decision threshold requirements are unchanged.
