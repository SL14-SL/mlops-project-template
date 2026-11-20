"""Cloud-neutral retraining gates driven by project-produced monitoring evidence."""

import hashlib
import json
import math
from datetime import UTC, datetime

from ..configs.paths import join_uri
from ..pipeline.project_factory import build_project_training_pipeline
from ..storage.filesystem import file_exists, read_text, write_text
from .lifecycle_adapter import run_prefect_model_lifecycle


def _time(value=None):
    if value is None:
        return datetime.now(UTC)
    timestamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        raise ValueError("Retraining timestamps must include a timezone.")
    return timestamp.astimezone(UTC)


def _number(settings, name, default):
    value = settings.get(name, default)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite non-negative number.")
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be a finite non-negative number.")
    return value


def _paths(config):
    root = join_uri(config["paths"]["artifacts"], "lifecycle")
    settings = config.get("monitoring", {}).get("retraining", {})
    return settings.get("signals_path", join_uri(root, "retraining_signals.json")), join_uri(
        root, "retraining_state.json"
    )


def record_training_completion(*, config, evaluated_at=None, decision_id=None):
    """Record completion only after publication and any serving refresh succeed."""
    _, path = _paths(config)
    payload = {"last_training_at": _time(evaluated_at).isoformat(), "decision_id": decision_id}
    write_text(path, json.dumps(payload, sort_keys=True))


def run_auto_retraining(*, config, evaluated_at=None, after_lifecycle=None):
    """Validate evidence, enforce freshness/cooldown/idempotency, then run one lifecycle.

    Calls must be serialized by the scheduler; the marker is not a distributed lock.
    The project adapter owns signal calculation and training-data ingestion.
    """
    now = _time(evaluated_at)
    settings = config.get("monitoring", {}).get("retraining", {})
    signal_path, state_path = _paths(config)
    if not file_exists(signal_path):
        return {"status": "skipped", "reasons": ["No monitoring evidence available."]}
    signals = json.loads(read_text(signal_path))
    if not isinstance(signals, dict):
        raise ValueError("Retraining evidence must be a JSON object.")
    observed = _time(signals["observed_at"])
    age = (now - observed).total_seconds() / 3600
    maximum_age = _number(settings, "maximum_signal_age_hours", 48)
    if age < 0 or age > maximum_age:
        return {"status": "skipped", "reasons": ["Monitoring evidence is future-dated or stale."]}
    rows = signals.get("new_training_rows")
    if isinstance(rows, bool) or not isinstance(rows, int) or rows < 0:
        raise ValueError("new_training_rows must be a non-negative integer.")
    for name in ("performance_degraded", "feature_drift"):
        if not isinstance(signals.get(name), bool):
            raise ValueError(f"{name} must be a JSON boolean.")
    # A stable observation cannot be retrained repeatedly after cooldown expires.
    decision = hashlib.sha256(json.dumps(signals, sort_keys=True).encode()).hexdigest()
    state = json.loads(read_text(state_path)) if file_exists(state_path) else {}
    if state.get("decision_id") == decision:
        return {"status": "skipped", "reasons": ["This observation was already processed."]}
    elapsed = None
    if state.get("last_training_at"):
        elapsed = (now - _time(state["last_training_at"])).total_seconds() / 3600
        if elapsed < _number(settings, "cooldown_hours", 168):
            return {"status": "skipped", "reasons": ["Retraining cooldown is active."]}
    if rows < _number(settings, "minimum_new_training_rows", 500):
        return {"status": "skipped", "reasons": ["Insufficient new training rows."]}
    scheduled = elapsed is not None and elapsed >= _number(
        settings, "scheduled_interval_hours", 720
    )
    if not (signals["performance_degraded"] or signals["feature_drift"] or scheduled):
        return {"status": "skipped", "reasons": ["No retraining trigger is active."]}
    result = run_prefect_model_lifecycle(pipeline=build_project_training_pipeline(config))
    if after_lifecycle is not None:
        after_lifecycle(result)
    record_training_completion(config=config, evaluated_at=now, decision_id=decision)
    return {
        "status": "retrained",
        "decision_id": decision,
        "candidate_run_id": result.pipeline.pipeline.training.run_id,
        "champion_promoted": result.serving_release is not None,
    }
