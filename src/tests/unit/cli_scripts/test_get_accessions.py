import argparse

from pn_ncbi_pkg.cli import get_accessions
from pn_ncbi_pkg.report import Report
from tests.helpers import load_json


def retryable_report():
    report = Report(errors=["sample processing."], status="Processing")
    report.vote_retry()
    return report


def test_retryable_report_exits_2_after_writing_ppo(tmp_path, monkeypatch):
    output_path = tmp_path / "PipelineProcessOutputs.json"
    args = argparse.Namespace(
        sample_name="sample_1",
        submission_type="Test",
        out_ppo=str(output_path),
        protocol="sftp",
        config_path="submission_config.yml",
        zero_exit=False,
    )
    monkeypatch.setattr(get_accessions, "get_connection", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(get_accessions.Report, "from_server", lambda *_args, **_kwargs: retryable_report())

    result = get_accessions.run(args)

    assert result == 2
    output = load_json(output_path)
    assert output["qc"]["result"] == "FAIL"
    assert output["status"] == "Processing"


def test_zero_exit_suppresses_retry_exit_code_after_writing_ppo(tmp_path, monkeypatch):
    output_path = tmp_path / "PipelineProcessOutputs.json"
    args = argparse.Namespace(
        sample_name="sample_1",
        submission_type="Test",
        out_ppo=str(output_path),
        protocol="sftp",
        config_path="submission_config.yml",
        zero_exit=True,
    )
    monkeypatch.setattr(get_accessions, "get_connection", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(get_accessions.Report, "from_server", lambda *_args, **_kwargs: retryable_report())

    result = get_accessions.run(args)

    assert result == 0
    output = load_json(output_path)
    assert output["qc"]["result"] == "FAIL"
    assert output["status"] == "Processing"
