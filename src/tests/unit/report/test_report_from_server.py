from pn_ncbi_pkg.report import Report
from tests.helpers import FakeReportConnection


def test_malformed_report_xml_is_retryable():
    connection = FakeReportConnection(report_xml="<SubmissionStatus><Action")

    report = Report.from_server(connection, "SUBMISSION_DIR")

    assert report.stop is False
    assert report.errors
    assert "report.xml" in "\n".join(str(error) for error in report.errors).lower()


def test_missing_report_xml_is_retryable():
    connection = FakeReportConnection(read_exc=FileNotFoundError("report.xml does not exist"))

    report = Report.from_server(connection, "SUBMISSION_DIR")

    assert report.stop is False
    assert report.errors
    assert "report.xml" in "\n".join(str(error) for error in report.errors)


def test_directory_connection_interruption_is_retryable_and_closes_connection():
    connection = FakeReportConnection(change_directory_exc=ConnectionError("socket closed"))

    report = Report.from_server(connection, "SUBMISSION_DIR")

    assert report.stop is False
    assert report.errors
    assert connection.closed is True
