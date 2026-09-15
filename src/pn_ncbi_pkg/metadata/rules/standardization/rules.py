from ..metadata_rules.standardization_fields import (
    CanonicalizeFieldNames,
    GeoLocNameFromCountryState,
    RemoveBlankStrings,
    RemoveMissingFields,
    RemoveNullValues,
)

ALL_ALIASES = {
    "ncbi-spuid": "spuid",
    "ncbi-spuid_namespace": "spuid_namespace",
    "ncbi-bioproject": "bioproject",
}

SRA_ALIASES = {
    "illumina_sequencing_instrument": "instrument_model",
    "illumina_library_source": "library_source",
    "illumina_library_selection": "library_selection",
    "illumina_library_layout": "library_layout",
    "illumina_library_protocol": "library_construction_protocol",
    "illumina_library_strategy": "library_strategy",
    "illumina_library_name": "library_name"
}

CANNOT_BE_MISSING_FIELDS = {
    "subspecies",
    "sub_species",
    "sub species",
    "sub-species",
    "variety",
    "forma",
    "forma_specialis",
    "serovar"
}

NULL_VALUES = {
    "?",
    "n/a",
    "na",
    "none",
    "not available",
    "not determined",
    "not recorded",
    "null",
    "unk",
    "unknown",
    "unspecified",
}

bs_only_canonicalize = CanonicalizeFieldNames(ALL_ALIASES)

sra_only_canonicalize = CanonicalizeFieldNames(ALL_ALIASES | SRA_ALIASES)

both_canonicalize = CanonicalizeFieldNames(ALL_ALIASES | SRA_ALIASES)

bs_geo_loc_name = GeoLocNameFromCountryState()

remove_missing = RemoveMissingFields(CANNOT_BE_MISSING_FIELDS)

remove_blanks = RemoveBlankStrings()

remove_nulls = RemoveNullValues(NULL_VALUES)
