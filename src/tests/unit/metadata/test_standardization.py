from pn_ncbi_pkg.metadata import prepare_metadata_for_submission
from pn_ncbi_pkg.result import Ok
from pn_ncbi_pkg.submission import SubmissionDB
from tests.helpers import _DELETE, valid_ohe_metadata


def test_different_case_aliases_standardize_to_canonical_fields():
    metadata = valid_ohe_metadata(
        **{
            "ncbi-spuid": _DELETE,
            "ncbi-spuid_namespace": _DELETE,
            "ncbi-bioproject": _DELETE,
            "geo_loc_name": _DELETE,
            "NCBI-SPUID": "spuid",
            "NCBI-SPUID_NAMESPACE": "some_namespace",
            "NCBI-BIOPROJECT": "PRJNA000000",
            "Country": "USA",
            "State": "TX",
        }
    )

    result = prepare_metadata_for_submission(metadata, SubmissionDB.BIOSAMPLE)

    assert isinstance(result, Ok), "Data should be valid - not test target"

    new_metadata = result.unwrap()

    assert new_metadata["spuid"] == "spuid", "spuid was not standardized"
    assert new_metadata["spuid_namespace"] == "some_namespace", (
        "spuid_namespace was not standardized"
    )
    assert new_metadata["bioproject"] == "PRJNA000000", "bioproject was not standardized"
    assert new_metadata["geo_loc_name"] == "USA:TX", "geo_loc_name was not standardized"

    for raw_alias in ["NCBI-SPUID", "NCBI-SPUID_NAMESPACE", "NCBI-BIOPROJECT", "Country", "State"]:
        assert raw_alias not in new_metadata, (
            f"{raw_alias} is not a valid metadata field and should "
            "have been removed during standardization"
        )
