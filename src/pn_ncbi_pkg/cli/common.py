from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pn_ncbi_pkg.metadata.result_types import MetadataFailure

FIELD_ALIASES = {
    "sample_name": "Strain name",
    "spuid": "Submitter Provided Unique ID",
    "spuid_namespace": "SPUID namespace",
    "bioproject": "BioProject accession",
    "author": "Author",
    "serovar": "Serovar",
    "source_type": "Source Type",
    "isolate": "Isolate Name Alias",
    "isolation_source": "Isolation source",
    "geo_loc_name": "Geographical origin",
    "organism": "Organism name",
    "collection_date": "Collection / Isolation date",
    "collected_by": "Collected by",
    "instrument_model": "Instrument model",
    "library_strategy": "Library strategy",
    "library_source": "Library source",
    "library_selection": "Library selection",
    "library_layout": "Library layout",
    "library_construction_protocol": "Library name",
    "project_name": "Project Name",
    "sequenced_by": "Sequenced By"
}


def format_errors(metadata_errors: MetadataFailure) -> list[str]:
    error_msgs: list[str] = []
    for issue in metadata_errors.issues:
        field = issue.field
        web_app_field = FIELD_ALIASES.get(field, field)
        provided = issue.value
        msg = issue.message
        rename = re.sub(pattern=rf'\b{field}\b', repl=web_app_field, string=msg)
        error_msgs.append(
            f"Problem field: {web_app_field}. "
            "Status: Metadata Validation Failure. "
            f"Provided data: {provided}. "
            f"Error message: {rename}"
        )
    return error_msgs
