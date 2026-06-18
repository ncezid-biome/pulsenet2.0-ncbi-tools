import pytest

from pn_ncbi_pkg.metadata import BioSamplePackage, Metadata, prepare_metadata_for_edit
from pn_ncbi_pkg.result import Err, Ok


@pytest.fixture
def existing_ohe_metadata():
    return Metadata(
        {
            "spuid": "PNUSAS12345",
            "spuid_namespace": "EDLB-CDC",
            "bioproject": "PRJNA56789",
            "sample_name": "PNUSAS12345",
            "organism": "Salmonella enterica",
            "strain": "PNUSAS12345",
            "collected_by": "CDC",
            "collection_date": "2025-01-01",
            "geo_loc_name": "USA:GA",
            "isolation_source": "food",
            "source_type": "food",
        },
        package=BioSamplePackage.OHE,
    )

@pytest.fixture
def meta_patch():
    def _build_meta_patch(fields: dict[str, str], package: BioSamplePackage | None = BioSamplePackage.OHE):
        return Metadata(
            {"biosample": "SAMN12345"} | fields,
            package=package
        )
    return _build_meta_patch

def messages(result):
    return "\n".join(result.error.messages())


def test_edit_mutable_field_succeeds(existing_ohe_metadata, meta_patch):
    update = meta_patch({"collected_by": "State lab"})

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Ok)
    assert result.value["collected_by"] == "State lab"
    assert result.value["strain"] == "PNUSAS12345"


def test_edit_immutable_changed_value_fails(existing_ohe_metadata, meta_patch):
    update = meta_patch({"strain": "DIFFERENT"})

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Err)
    assert "strain cannot be updated automatically" in messages(result)


def test_edit_blank_biosample_fails(existing_ohe_metadata, meta_patch):
    update = meta_patch({"biosample": ""})

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Err)
    assert "biosample is required" in messages(result)


def test_edit_missing_biosample_fails(existing_ohe_metadata, meta_patch):
    update = meta_patch({})
    del update["biosample"]

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Err)
    assert "biosample is required" in messages(result)


def test_edit_immutable_same_value_succeeds(existing_ohe_metadata, meta_patch):
    update = meta_patch({"strain": "PNUSAS12345"})

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Ok)
    assert result.value["strain"] == "PNUSAS12345"


def test_edit_immutable_alias_is_standardized_before_validation(existing_ohe_metadata, meta_patch):
    update = meta_patch({"ncbi-spuid": "DIFFERENT"})

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Err)
    assert "spuid cannot be updated automatically" in messages(result)


def test_edit_without_package_keeps_existing_package(existing_ohe_metadata, meta_patch):
    update = meta_patch({"collected_by": "State lab"}, None)

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Ok)
    assert result.value.package == BioSamplePackage.OHE
    assert result.value["collected_by"] == "State lab"


def test_edit_reports_unfixed_preexisting_validation_failures(existing_ohe_metadata, meta_patch):
    del existing_ohe_metadata["collected_by"]
    update = meta_patch({"purpose_of_sampling": "surveillance"})

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Err)
    assert "issue with existing sample metadata must be fixed" in messages(result)
    assert "collected_by is required" in messages(result)


def test_edit_can_fix_preexisting_validation_failure(existing_ohe_metadata, meta_patch):
    del existing_ohe_metadata["collected_by"]
    update = meta_patch({"collected_by": "State lab"})

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Ok)
    assert result.value["collected_by"] == "State lab"


def test_edit_standardization_failure_stops_processing(existing_ohe_metadata, meta_patch):
    update = meta_patch(
        {
            "spuid": "PNUSAS12345",
            "ncbi-spuid": "DIFFERENT",
        }
    )

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Err)
    assert "Multiple input fields map to spuid" in messages(result)
    assert "cannot be updated automatically" not in messages(result)


def test_edit_invalid_mutable_value_fails_normal_validation(existing_ohe_metadata, meta_patch):
    update = meta_patch({"source_type": "not-a-source-type"})

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Err)
    assert "source_type is a controlled language field" in messages(result)


def test_edit_multiple_immutable_changes_report_multiple_issues(existing_ohe_metadata, meta_patch):
    update = meta_patch(
        {
            "bioproject": "PRJNA99999",
            "organism": "Escherichia coli",
            "strain": "DIFFERENT",
        }
    )

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Err)
    assert "bioproject cannot be updated automatically" in messages(result)
    assert "organism cannot be updated automatically" in messages(result)
    assert "strain cannot be updated automatically" in messages(result)


def test_edit_blank_immutable_value_is_rejected_as_immutable_change(existing_ohe_metadata, meta_patch):
    update = meta_patch({"strain": ""})

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Err)
    assert "strain cannot be updated automatically" in messages(result)
    assert "strain is required" not in messages(result)


def test_edit_immutable_alias_with_same_value_succeeds(existing_ohe_metadata, meta_patch):
    update = meta_patch({"ncbi-spuid": "PNUSAS12345"})

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Ok)
    assert result.value["spuid"] == "PNUSAS12345"


def test_edit_reports_preexisting_and_new_validation_failures(existing_ohe_metadata, meta_patch):
    del existing_ohe_metadata["collected_by"]
    update = meta_patch({"source_type": "not-a-source-type"})

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Err)
    assert "issue with existing sample metadata must be fixed" in messages(result)
    assert "collected_by is required" in messages(result)
    assert "source_type is a controlled language field" in messages(result)


def test_edit_reports_new_validation_failures_after_fixing_preexisting_issue(existing_ohe_metadata, meta_patch):
    del existing_ohe_metadata["collected_by"]
    update = meta_patch(
        {
            "collected_by": "State lab",
            "source_type": "not-a-source-type",
        }
    )

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Err)
    assert "source_type is a controlled language field" in messages(result)
    assert "issue with existing sample metadata must be fixed" not in messages(result)
    assert "collected_by is required" not in messages(result)


def test_edit_package_update_uses_new_package_validation(existing_ohe_metadata, meta_patch):
    update = meta_patch({}, package=BioSamplePackage.PATH)

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Err)
    assert "host is required" in messages(result)
    assert "host_disease is required" in messages(result)
    assert "lat_lon is required" in messages(result)


def test_edit_package_update_succeeds_with_new_package_required_fields(existing_ohe_metadata, meta_patch):
    update = meta_patch(
        {
            "host": "Homo sapiens",
            "host_disease": "Salmonellosis",
            "lat_lon": "38.98 N 77.11 W",
        },
        package=BioSamplePackage.PATH,
    )

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Ok)
    assert result.value.package == BioSamplePackage.PATH
    assert result.value["host"] == "Homo sapiens"


def test_edit_immutable_comparison_is_strict(existing_ohe_metadata, meta_patch):
    update = meta_patch({"strain": "PNUSAS12345 "})

    result = prepare_metadata_for_edit(existing_ohe_metadata, update)

    assert isinstance(result, Err)
    assert "strain cannot be updated automatically" in messages(result)
