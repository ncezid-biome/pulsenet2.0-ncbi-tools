import pytest

from pn_ncbi_pkg.metadata import (
    prepare_metadata_for_submission,
    validate_existing_biosample_xml,
)
from pn_ncbi_pkg.metadata.result_types import MetadataAnnotation, MetadataFailure
from pn_ncbi_pkg.result import Ok
from pn_ncbi_pkg.submission import SubmissionDB
from tests.helpers import _DELETE, valid_existing_ohe_metadata, valid_ohe_metadata


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

@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("sub-species","MISSING"),
        ("serovar","missing"),
    ],
)
def test_missing_values_removed_from_forbiden(field,value):
    metadata= valid_ohe_metadata(**{field:value})

    result = prepare_metadata_for_submission(metadata, SubmissionDB.BIOSAMPLE)
    assert isinstance(result, Ok), "Data should be valid - not test target"
    new_metadata = result.unwrap()
    assert field not in new_metadata, "field cannot be missing and should have been removed during standardization"

@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("building_setting","MISSING"),
        ("building_setting","missing"),
    ],
)
def test_missing_values_for_permitted(field,value):
    metadata= valid_ohe_metadata(**{field:value})

    result = prepare_metadata_for_submission(metadata, SubmissionDB.BIOSAMPLE)
    assert isinstance(result, Ok), "Data should be valid - not test target"
    new_metadata = result.unwrap()
    assert field in new_metadata, "value can be missing and should be present in the metadata"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("optional_field",""),
    ],
)
def test_blank_values_removed(field,value):
    metadata= valid_ohe_metadata(**{field:value})

    result = prepare_metadata_for_submission(metadata, SubmissionDB.BIOSAMPLE)
    assert isinstance(result, Ok), "Data should be valid - not test target"
    new_metadata = result.unwrap()
    assert field not in new_metadata, "value cannot be blank and should have been removed during standardization"

@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("any_field","?"),
    ],
)
def test_null_values_removed(field,value):
    metadata= valid_ohe_metadata(**{field:value})

    result = prepare_metadata_for_submission(metadata, SubmissionDB.BIOSAMPLE)
    assert isinstance(result, Ok), "Data should be valid - not test target"
    new_metadata = result.unwrap()
    assert field not in new_metadata, "value cannot be null and should have been removed during standardization"

@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("isolation_source",_DELETE),
        ("source_type",_DELETE),
        ("strain",_DELETE),
        ("sample_name",_DELETE),
        ("organism",_DELETE),
        ("collection_date",_DELETE),
        ("geo_loc_name",_DELETE),
    ],
)
def test_bs_submission_xml_validation_fails_missing_required_fields(field, value):

    metadata = valid_existing_ohe_metadata(**{field:value})
    result = validate_existing_biosample_xml(metadata)
    assert isinstance(result, MetadataAnnotation), "Should always return MetadataAnnotation - not test target"
    assert isinstance(result.issues, MetadataFailure), "Data should not be valid"
    assert len(result.issues.issues) == 1, "There should only be one issue - the missing field."
    assert field == result.issues.issues[0].field, f"{field} not logged as an issue - missing required fields should be present"
    for meta_field in metadata:
        assert meta_field in result.metadata, f"{meta_field} not found in metadata annotation - all fields should be present"
    assert field in result.metadata, f"{meta_field} not found in metadata annotation - all fields should be present"

@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("author",_DELETE),
        ("spuid_namespace",_DELETE),
        ("purpose_of_sampling",_DELETE),
        ("collected_by",_DELETE),
    ],
)
def test_bs_submission_xml_validation_tolerates_missing_default_fields(field, value):

    metadata = valid_existing_ohe_metadata(**{field:value})
    result = validate_existing_biosample_xml(metadata)
    assert isinstance(result, MetadataAnnotation), "Should always return MetadataAnnotation - not test target"
    assert result.issues is None, "Data should be valid"
    for meta_field in metadata:
        assert meta_field in result.metadata, f"{meta_field} not found in metadata annotation - all fields should be present"
    assert field in result.metadata, f"{field} not found in metadata annotation - missing default fields should be present"
    assert field in result.changes, f"{field} not found in metadata changes - missing default fields should be tracked as changes"
