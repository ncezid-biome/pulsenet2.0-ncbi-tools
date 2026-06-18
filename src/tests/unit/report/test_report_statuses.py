import pytest

from pn_ncbi_pkg.report import Report


def test_unknown_action_status_is_not_success():
    report_xml = """<?xml version='1.0' encoding='utf-8'?>
    <SubmissionStatus status="processing" submission_id="SUB1">
      <Action target_db="SRA" status="queued"/>
    </SubmissionStatus>
    """

    report = Report.from_xml_string(report_xml)

    assert not (report.qc == "PASS" and report.stop)
    assert report.errors and report.status == "Completed"


@pytest.mark.parametrize(
    "report_xml",
    [
        """<SubmissionStatus submission_id="SUB1">
             <Action status="processed-ok"/>
           </SubmissionStatus>""",
        """<SubmissionStatus submission_id="SUB1">
             <Action target_db="SRA"/>
           </SubmissionStatus>""",
        """<SubmissionStatus submission_id="SUB1">
             <Action target_db="UnexpectedDB" status="processed-ok"/>
           </SubmissionStatus>""",
    ],
)
def test_missing_or_unknown_action_attributes_produce_controlled_errors(report_xml):
    report = Report.from_xml_string(report_xml)

    assert report.errors
    assert report.qc == "FAIL"
