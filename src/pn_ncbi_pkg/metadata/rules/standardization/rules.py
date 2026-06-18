from ..metadata_rules.standardization_fields import (
    CanonicalizeFieldNames,
    GeoLocNameFromCountryState,
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

bs_only_canonicalize = CanonicalizeFieldNames(ALL_ALIASES)

sra_only_canonicalize = CanonicalizeFieldNames(ALL_ALIASES | SRA_ALIASES)

both_canonicalize = CanonicalizeFieldNames(ALL_ALIASES | SRA_ALIASES)

bs_geo_loc_name = GeoLocNameFromCountryState()
