import pytest

from pn_ncbi_pkg.metadata import prepare_metadata_for_submission
from pn_ncbi_pkg.result import Err
from pn_ncbi_pkg.submission import SubmissionDB
from tests.helpers import (
    _DELETE,
    error_text,
    valid_ill_sra_metadata,
    valid_ohe_metadata,
)


@pytest.mark.parametrize(
    ("raw_field", "expected_message_fragment"),
    [
        ("file1", "file1"),
        ("file2", "file2"),
        ("ncbi-spuid", "spuid"),
        ("ncbi-spuid_namespace", "spuid_namespace"),
        ("ncbi-bioproject", "bioproject"),
        ("illumina_sequencing_instrument", "instrument"),
        ("illumina_library_source", "library_source"),
        ("illumina_library_selection", "library_selection"),
        ("illumina_library_layout", "library_layout"),
        ("illumina_library_strategy", "library_strategy"),
    ],
)
def test_missing_sra_required_fields_return_validation_errors(
    raw_field,
    expected_message_fragment,
):
    metadata = valid_ill_sra_metadata(**{raw_field: _DELETE})
    result = prepare_metadata_for_submission(metadata, SubmissionDB.SRA)

    assert isinstance(result, Err), f"missing mandatory field {raw_field} should return Err"
    assert expected_message_fragment in error_text(result).lower(), (
        f"When {raw_field} is missing, the error should mention {expected_message_fragment}"
    )


@pytest.mark.parametrize(
    ("raw_field", "expected_message_fragment"),
    [
        ("organism", "organism"),
        ("ncbi-spuid", "spuid"),
        ("ncbi-bioproject", "bioproject"),
        ("collection_date", "collection_date"),
        ("geo_loc_name", "geo_loc_name"),
        ("source_type", "source_type"),
    ],
)
def test_missing_biosample_constructor_fields_return_validation_errors(
    raw_field,
    expected_message_fragment,
):
    metadata = valid_ohe_metadata(**{raw_field: _DELETE})
    print(metadata)
    result = prepare_metadata_for_submission(metadata, SubmissionDB.BIOSAMPLE)

    assert isinstance(result, Err), f"missing mandatory field {raw_field} should return Err"
    assert expected_message_fragment in error_text(result).lower(), (
        f"When {raw_field} is missing, the error should mention {expected_message_fragment}"
    )

