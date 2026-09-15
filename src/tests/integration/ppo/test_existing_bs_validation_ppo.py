import pytest

from pn_ncbi_pkg.metadata import validate_existing_biosample_xml
from pn_ncbi_pkg.report.ppo import format_ppo_data
from tests.helpers import _DELETE, valid_existing_ohe_metadata


def test_ppo_contains_all_metadata_fields():
    metadata = valid_existing_ohe_metadata()
    result = validate_existing_biosample_xml(metadata)
    ppo_data = format_ppo_data(metadata_annotation=result)
    sample_data_block = ppo_data["sample_data"]
    data_block = sample_data_block["data"]
    field_results_block = sample_data_block["field_results"]
    for meta_field in metadata:
        assert meta_field in data_block, f"All fields should be in ppo json, but {meta_field} is missing"
        assert meta_field in field_results_block, f"All fields should be in ppo json, but {meta_field} is missing"
        qc = field_results_block[meta_field]["QC"]
        assert qc == "PASS", f"All fields should PASS, but {meta_field} is {qc}"


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
def test_ppo_contains_fail_on_missing_mandatory(field, value):
    metadata = valid_existing_ohe_metadata(**{field:value})
    result = validate_existing_biosample_xml(metadata)
    ppo_data = format_ppo_data(metadata_annotation=result)
    sample_data_block = ppo_data["sample_data"]
    data_block = sample_data_block["data"]
    field_results_block = sample_data_block["field_results"]
    for meta_field in metadata:
        assert meta_field in data_block, f"All fields should be in ppo json, but {meta_field} is missing"
        assert meta_field in field_results_block, f"All fields should be in ppo json, but {meta_field} is missing"
        qc = field_results_block[meta_field]["QC"]
        assert qc == "PASS", f"All fields should PASS, but {meta_field} is {qc}"
    assert field in data_block, "Missing fields should be added to metadata"
    assert field in field_results_block, "Missing fields should be added to field_results"
    qc = field_results_block[field]["QC"]
    assert qc == "FAIL", f"Missing mandatory fields should FAIL, but {field} is {qc}"


@pytest.mark.parametrize(
    ("field", "value"),
    [
            ("author",_DELETE),
            ("spuid_namespace",_DELETE),
            ("purpose_of_sampling",_DELETE),
            ("collected_by",_DELETE),
    ],
)
def test_ppo_contains_warn_on_missing_default(field, value):
    metadata = valid_existing_ohe_metadata(**{field:value})
    result = validate_existing_biosample_xml(metadata)
    print(result)
    ppo_data = format_ppo_data(metadata_annotation=result)
    sample_data_block = ppo_data["sample_data"]
    data_block = sample_data_block["data"]
    field_results_block = sample_data_block["field_results"]
    for meta_field in metadata:
        assert meta_field in data_block, f"All fields should be in ppo json, but {meta_field} is missing"
        assert meta_field in field_results_block, f"All fields should be in ppo json, but {meta_field} is missing"
        qc  = field_results_block[meta_field]["QC"]
        assert qc  == "PASS", f"All fields should PASS, but {meta_field} is {qc}"
    assert field in data_block, "Missing fields should be added to metadata"
    assert field in field_results_block, "Missing fields should be added to field_results"
    qc  = field_results_block[field]["QC"]
    assert qc  == "WARN", f"Missing default fields should WARN, but {field} is {qc}"
