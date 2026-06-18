import xml.etree.ElementTree as ET
from unittest.mock import Mock, mock_open

import pytest

from pn_ncbi_pkg.metadata import (
    BioSamplePackage,
    metadata_from_csv,
    metadata_to_xml,
    prepare_metadata_for_submission,
)
from pn_ncbi_pkg.result import Err, Ok
from pn_ncbi_pkg.submission import SubmissionDB
from tests.helpers import _DELETE, error_text, valid_ohe_metadata

from . import data as test_data


@pytest.fixture
def opened_metadata_files(monkeypatch):
    mock_meta_read = mock_open(read_data=test_data.METADATA).return_value
    mock_config_read = mock_open(read_data=test_data.META_YAML).return_value
    mock_file_write = mock_open().return_value

    def mock_open_files(filename: str, *args, **kwargs) -> Mock:
        match filename:
            case "SampleFileMapping.csv":
                return mock_meta_read
            case "submission_config.yml":
                return mock_config_read
            case _:
                return mock_file_write

    monkeypatch.setattr("builtins.open", Mock(side_effect=mock_open_files))
    return mock_file_write

def test_combined_ohe_preserves_input_spuid_namespace(opened_metadata_files):
    meta_package = BioSamplePackage("OneHealthEnteric.1.0")
    submission_type = SubmissionDB("both")
    data = metadata_from_csv("SampleFileMapping.csv", meta_package)

    result = prepare_metadata_for_submission(data,submission_type)

    assert isinstance(result, Ok), "Data should be valid - not test target"

    new_data = result.unwrap()

    assert new_data["spuid_namespace"] == "some_namespace", "spuid_namespace was not standardized"

    metadata_to_xml(
        metadata=new_data,
        file_name="combined.xml",
        submission_yaml="submission_config.yml",
        submission_type=submission_type,
    )

    xml_text = opened_metadata_files.write.call_args.args[0]
    assert 'spuid_namespace="some_namespace"' in xml_text, (
        "input metadata not in output XML"
    )
    assert 'spuid_namespace="EDLB-CDC"' not in xml_text, (
        "default value overwriting input metadata"
    )

@pytest.mark.parametrize(
    ("submission_type", "file_name", "expected_xml"),
    [
        (SubmissionDB("sra"), "sra.xml", test_data.SRA_XML),
        (SubmissionDB("biosample"), "biosample.xml", test_data.BIO_XML),
        (SubmissionDB("both"), "combined.xml", test_data.COMBINED_XML),
    ],
)
def test_ohe_metadata_to_xml(opened_metadata_files, submission_type, file_name, expected_xml):
    meta_package = BioSamplePackage("OneHealthEnteric.1.0")
    data = metadata_from_csv("SampleFileMapping.csv", meta_package)
    data = prepare_metadata_for_submission(data, submission_type).unwrap()

    metadata_to_xml(
        metadata=data,
        file_name=file_name,
        submission_yaml="submission_config.yml",
        submission_type=submission_type,
    )

    opened_metadata_files.write.assert_called_once_with(expected_xml)


def test_combined_ohe_xml_semantic_fields(opened_metadata_files):
    data = metadata_from_csv("SampleFileMapping.csv", BioSamplePackage("OneHealthEnteric.1.0"))
    data = prepare_metadata_for_submission(data, SubmissionDB("both")).unwrap()
    metadata_to_xml(data, "combined.xml", "submission_config.yml", SubmissionDB("both"))

    xml_text = opened_metadata_files.write.call_args.args[0]
    root = ET.fromstring(xml_text)

    add_files = root.find(".//AddFiles")

    assert root is not None
    assert add_files is not None
    assert add_files.get("target_db") == "SRA"
    assert [node.get("file_path") for node in root.findall(".//AddFiles/File")] == ["r1.fq", "r2.fq"]
    primary_id = root.find(".//AttributeRefId[@name='BioProject']/RefId/PrimaryId")
    assert primary_id is not None
    assert primary_id.text == "PRJNA56789"
    spuid = root.find(".//BioSample/SampleId/SPUID")
    assert spuid is not None
    assert spuid.get("spuid_namespace") == "some_namespace"

    biosample_attributes = {
        node.get("attribute_name"): node.text
        for node in root.findall(".//BioSample/Attributes/Attribute")
    }
    assert biosample_attributes["geo_loc_name"] == "USA:TX"
    assert biosample_attributes["source_type"] == "Food"


def test_invalid_metadata_returns_multiple_validation_issues():
    metadata = valid_ohe_metadata(
        file1=_DELETE,
        source_type="not-a-source-type",
        illumina_library_layout="triple",
        country="NotACountry",
        geo_loc_name=_DELETE,
    )

    result = prepare_metadata_for_submission(metadata, SubmissionDB.BOTH)

    assert isinstance(result, Err)
    issues = error_text(result).lower()
    assert "file1" in issues
    assert "source_type" in issues
    assert "library_layout" in issues
    assert "country" in issues
