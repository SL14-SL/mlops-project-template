from dataclasses import dataclass

from .contracts import ServingReleaseManifest
from .pointer import ActiveReleasePointer


@dataclass(frozen=True)
class PublishedServingRelease:
    """Fully persisted and activated serving release."""

    manifest: ServingReleaseManifest
    release_root: str
    active_pointer: ActiveReleasePointer
