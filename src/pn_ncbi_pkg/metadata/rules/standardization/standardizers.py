from __future__ import annotations

from typing import TYPE_CHECKING

from pn_ncbi_pkg.submission import SubmissionDB

from .rules import (
    both_canonicalize,
    bs_geo_loc_name,
    bs_only_canonicalize,
    remove_blanks,
    remove_missing,
    remove_nulls,
    sra_only_canonicalize,
)

if TYPE_CHECKING:
    from ..metadata_rules.standardization_fields import (
        CanonicalizeFieldNames,
        GeoLocNameFromCountryState,
        RemoveBlankStrings,
        RemoveMissingFields,
        RemoveNullValues,
    )


def get_standardization_rules(
    submission_type: SubmissionDB
) -> tuple[CanonicalizeFieldNames | GeoLocNameFromCountryState | RemoveNullValues | RemoveBlankStrings | RemoveMissingFields , ...]:
    match submission_type:
        case SubmissionDB.SRA:
            return (sra_only_canonicalize, remove_nulls, remove_blanks, remove_missing)
        case SubmissionDB.BIOSAMPLE:
            return (bs_only_canonicalize, bs_geo_loc_name, remove_nulls, remove_blanks, remove_missing)
        case SubmissionDB.BOTH:
            return (both_canonicalize, bs_geo_loc_name, remove_nulls, remove_blanks, remove_missing)
