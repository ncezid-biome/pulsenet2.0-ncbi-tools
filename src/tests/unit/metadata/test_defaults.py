import pytest

from pn_ncbi_pkg.metadata import prepare_metadata_for_submission
from pn_ncbi_pkg.result import Ok
from pn_ncbi_pkg.submission import SubmissionDB
from tests.helpers import valid_ohe_metadata


@pytest.mark.parametrize(
    ("field", "default"),
    [
        ("author", "CDC"),
        ("spuid_namespace", "EDLB-CDC"),
        ("strain", "missing"),
        ("collected_by", "missing"),
        ("isolation_source", "missing"),
        ("purpose_of_sampling", "missing"),
    ],
)
def test_blank_defaultable_mandatory_fields_use_defaults(field, default):
    metadata = valid_ohe_metadata(**{field: ""})
    del metadata["ncbi-spuid_namespace"]

    result = prepare_metadata_for_submission(metadata, SubmissionDB.BIOSAMPLE)

    assert isinstance(result, Ok), f"default field {field} should tolerate blank input"

    new_metadata = result.unwrap()

    assert new_metadata[field] == default, (
        f"blank input for field {field} should be replaced with {default}"
    )

