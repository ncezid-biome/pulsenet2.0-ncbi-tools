import argparse

from pn_ncbi_pkg.cli import submit
from tests.helpers import load_json


class FakeSubmitConnection:
    def file_exists(self, path):
        return False

    def make_directory(self, directory):
        self.made_directory = directory

    def change_directory(self, directory):
        self.changed_directory = directory

    def upload_file(self, local_path, remote_path):
        raise OSError("simulated upload failure")


def test_upload_failure_writes_failed_ppo(tmp_path, monkeypatch):
    output_path = tmp_path / "PipelineProcessOutputs.json"
    args = argparse.Namespace(
        submission_dir="sample_1",
        submission_type="Test",
        out_ppo=str(output_path),
        files=["submission.xml", "reads_1.fastq.gz"],
        protocol="sftp",
        submission_yaml="submission_config.yml",
    )
    monkeypatch.chdir(tmp_path)
    (tmp_path / "submission.xml").write_text("<Submission/>")
    (tmp_path / "reads_1.fastq.gz").write_bytes(b"reads")
    monkeypatch.setattr(submit, "get_connection", lambda *_args, **_kwargs: FakeSubmitConnection())

    result = submit.run(args)

    assert result == 0
    output = load_json(tmp_path / "PipelineProcessOutputs.json")
    assert output["qc"]["result"] == "FAIL"
    assert output["metadata"]["Submission_dir"] == "sample_1"
    assert "simulated upload failure" in "\n".join(output["qc"]["issues"])
