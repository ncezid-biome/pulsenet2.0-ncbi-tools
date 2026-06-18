from unittest.mock import Mock, mock_open

import pytest

from pn_ncbi_pkg.metadata.biosample_record.io import (
    load_biosample_xml,
    load_submission_xml,
)
from pn_ncbi_pkg.metadata.packages import BioSamplePackage

from . import data as test_data


@pytest.fixture
def opened_xml(monkeypatch):
    mock_public_xml_read = mock_open(read_data=test_data.PUBLIC_BS_XML).return_value
    mock_bs_sub_xml_read = mock_open(read_data=test_data.BIO_XML).return_value
    mock_combined_sub_xml_read = mock_open(read_data=test_data.COMBINED_XML).return_value
    mock_file_write = mock_open().return_value

    def mock_open_files(filename: str, *args, **kwargs) -> Mock:
        match filename:
            case "existing_bs.xml":
                return mock_public_xml_read
            case "submission_bs.xml":
                return mock_bs_sub_xml_read
            case "submission_comb.xml":
                return mock_combined_sub_xml_read
            case _:
                return mock_file_write

    monkeypatch.setattr("builtins.open", Mock(side_effect=mock_open_files))
    return mock_file_write

def test_bs_record_contains_expected_fields_from_public_xml(opened_xml):
    record = load_biosample_xml("existing_bs.xml")

    assert record.biosample == "SAMN12345"
    assert record.bioproject == "PRJNA56789"
    assert record.spuid == "PNUSAS12345"
    assert record.spuid_namespace == "EDLB-CDC"
    assert record.package == BioSamplePackage.OHE
    assert record.organism == "Salmonella enterica"
    assert record.attrs == {
        "strain": "PNUSAS12345",
        "sample_name": "PNUSAS12345",
        "author": "CDC",
        "serovar": "Typhimurium",
        "source_type": "human",
        "isolate_name_alias": "PNUSAS12345",
        "isolation_source": "missing",
        "geo_loc_name": "USA",
        "collection_date": "2026",
        "collected_by": "CDC",
        "project_name": "missing",
        "sequenced_by": "CDC",
        "purpose_of_sampling": "missing"
    }

@pytest.mark.parametrize(
    ("report_xml", "biosample"),
    [
        ("submission_bs.xml", "SAMN12345"),
        ("submission_comb.xml", "SAMN12345"),
    ],
)
def test_bs_record_contains_expected_fields_from_sub_xmls(opened_xml, report_xml, biosample):
    record = load_submission_xml(report_xml, biosample)
    assert record.biosample == "SAMN12345"
    assert record.spuid == "spuid"
    assert record.spuid_namespace == "some_namespace"
    assert record.package == BioSamplePackage.OHE
    assert record.organism == "Escherichia coli"
    assert record.attrs == {
        "strain": "strain_name",
        "sample_name": "test_sample",
        "author": "author_name",
        "serovar": "serovar_name",
        "source_type": "Food",
        "isolate_name_alias": "test_sample",
        "isolation_source": "source",
        "geo_loc_name": "USA:TX",
        "collection_date": "1/30/2002",
        "collected_by": "collector",
        "project_name": "project",
        "sequenced_by": "sequencer",
        "intended_consumer": "human as food consumer",
        "food_origin": "origin",
        "food_processing_method": "food_proc_method",
        "purpose_of_sampling": "purpose"
    }
