from __future__ import annotations

from typing import TYPE_CHECKING

from pn_ncbi_pkg.result import Err, Ok

from ...result_types import (
    MetadataFailure,
    MetadataIssue,
    MetadataPatch,
    MetadataPhase,
)
from .base_rules import StandardizationRule

if TYPE_CHECKING:
    from ...metadata_obj import Metadata
    from ...result_types import TransformResult


class CanonicalizeFieldNames(StandardizationRule):
    """Change field names so they match expectations of subsequent rules

    1. Replace known aliases with a single canonical name
    2. Convert casing to lower

    Catches cases where a single key is present in two forms
    """
    def __init__(self, aliases: dict[str, str]):
        self.aliases = {key.lower(): value for key, value in aliases.items()}

    def __call__(self, metadata: Metadata) -> TransformResult:
        updates: dict[str, str] = {}
        removals: list[str] = []
        issues: list[MetadataIssue] = []

        for raw_key, value in metadata.items():
            lookup_key = raw_key.lower().strip()
            canonical_key = self.aliases.get(lookup_key, lookup_key)

            if canonical_key in updates and updates[canonical_key] != value:
                issues.append(MetadataIssue(
                    phase=MetadataPhase.STANDARDIZATION,
                    field=canonical_key,
                    rule=type(self).__name__,
                    message=(
                        f"Multiple input fields map to {canonical_key} "
                        f"with different values."
                    ),
                    value=",".join([updates[canonical_key], value])
                ))
                continue

            if raw_key != canonical_key:
                removals.append(raw_key)

            updates[canonical_key] = value

        if issues:
            return Err(MetadataFailure(tuple(issues)))

        return Ok(MetadataPatch(updates, tuple(removals)))


class GeoLocNameFromCountryState(StandardizationRule):
    def __call__(self, metadata: Metadata) -> TransformResult:
        country = metadata.get("country")
        state = metadata.get("state")
        existing = metadata.get("geo_loc_name")

        if not country:
            return Ok(MetadataPatch({}))

        standardized = f"{country}:{state or ''}"

        if existing:
            return Err(MetadataFailure.issue(
                phase=MetadataPhase.STANDARDIZATION,
                field="geo_loc_name",
                rule=type(self).__name__,
                message="Provide either geo_loc_name or country/state, not both.",
                value=f"Found geo_loc_name={existing} and country/state={standardized}."
            ))

        return Ok(MetadataPatch(
            set_values={"geo_loc_name": standardized},
            remove_fields=("country", "state") if state is not None else ("country",),
        ))

