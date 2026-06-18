import json
import xml.etree.ElementTree as ET

import pytest

from pn_ncbi_pkg.report import Report, ppo

from . import data as test_data


def assert_successful_duplicate_report_state(report):
    assert report.qc == "PASS"
    assert report.stop is True
    assert report.status == "Completed"
    assert report.errors == []


@pytest.mark.parametrize(
    ("report_xml", "expected_sra", "expected_biosample"),
    [
        (test_data.BS_DUP_REPORT, None, "SAMN52211363"),
        (test_data.SRA_DUP_REPORT, "SRR35706443", None),
        (test_data.BS_SRA_DUP_REPORT, "SRR35706443", "SAMN52211363"),
    ],
)
def test_duplicate_reports_get_accessions_without_errors(
    report_xml,
    expected_sra,
    expected_biosample,
    monkeypatch,
):
    monkeypatch.setattr(
        ET,
        "parse",
        lambda _path: ET.ElementTree(ET.fromstring(report_xml)),
    )

    result = Report.from_report_xml("fakepath")

    assert result.sra_accession == expected_sra
    assert result.biosample_accession == expected_biosample
    assert_successful_duplicate_report_state(result)


def test_gets_duplicates_accession_from_report(monkeypatch):
    monkeypatch.setattr(
        ET,
        "parse",
        lambda _path: ET.ElementTree(ET.fromstring(test_data.SRA_DUP_REPORT)),
    )

    monkeypatch.setattr(
        Report,
        "to_file",
        lambda self, _: ppo.format_ppo_data(
            srr=self.sra_accession,
            samn=self.biosample_accession,
            submission=self.submission,
            submission_dir=self.submission_dir,
            issues=self.errors,
            status=self.status
        )


    )

    report = Report.from_report_xml("fakepath")
    assert_successful_duplicate_report_state(report)

    output = report.to_file("fakepath")
    assert json.dumps(output, indent=4) == test_data.EXPECTED_PPO
