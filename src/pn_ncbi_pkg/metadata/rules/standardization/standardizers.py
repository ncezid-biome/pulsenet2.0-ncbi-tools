from __future__ import annotations

from typing import TYPE_CHECKING

from pn_ncbi_pkg.submission import SubmissionDB

from .rules import (
    both_canonicalize,
    bs_geo_loc_name,
    bs_only_canonicalize,
    sra_only_canonicalize,
)

if TYPE_CHECKING:
    from ..metadata_rules.standardization_fields import (
        CanonicalizeFieldNames,
        GeoLocNameFromCountryState,
    )


def get_standardization_rules(
    submission_type: SubmissionDB
) -> tuple[CanonicalizeFieldNames | GeoLocNameFromCountryState, ...]:
    match submission_type:
        case SubmissionDB.SRA:
            return (sra_only_canonicalize,)
        case SubmissionDB.BIOSAMPLE:
            return (bs_only_canonicalize, bs_geo_loc_name)
        case SubmissionDB.BOTH:
            return (both_canonicalize, bs_geo_loc_name)
