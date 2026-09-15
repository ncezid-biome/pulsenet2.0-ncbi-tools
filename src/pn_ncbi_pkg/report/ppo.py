import json
from dataclasses import dataclass
from typing import Literal, NotRequired, TypedDict

from pn_ncbi_pkg.metadata.result_types import MetadataAnnotation, MetadataFailure


class PPOMetadata(TypedDict):
    SRR_ID: str | None
    NCBI_ACCESSION: str | None
    Submission: str | None
    Submission_dir: str | None

class PPOQC(TypedDict):
    result: Literal["PASS", "FAIL"]
    issues: list[str]

class PPOFieldResult(TypedDict):
    QC: Literal["PASS", "WARN", "FAIL"]
    Issue: str


class PPOSampleData(TypedDict):
    data: dict[str, str]
    field_results: dict[str, PPOFieldResult]


class PPOData(TypedDict):
    metadata: PPOMetadata
    qc: PPOQC
    status: str
    sample_data: NotRequired[PPOSampleData]


@dataclass
class PPO:
    srr: str|None
    samn: str|None
    submission: str|None
    submission_dir: str|None
    issues: list[str]|None
    metadata_annotation: MetadataAnnotation|None
    metadata_failure: MetadataFailure|None
    status: str=""

    def to_file(self, file_path: str):
        ppo_body = self.build_ppo()
        with open(file_path, "w") as fout:
            json.dump(ppo_body, fout, indent=4)

    def build_ppo(self) -> PPOData:
        if self.issues is None:
            issues = []
        else:
            issues = self.issues
        ppo_body: PPOData = {
            "metadata": {
                "SRR_ID": self.srr,
                "NCBI_ACCESSION": self.samn,
                "Submission": self.submission,
                "Submission_dir": self.submission_dir
            },
            "qc": {
                "result": "PASS" if len(issues) == 0 else "FAIL",
                "issues": issues
            },
            "status": self.status
        }
        if self.metadata_annotation is not None:
            ppo_body["sample_data"] = self._build_sample_data_section()
        return ppo_body


    def _build_sample_data_section(self) -> PPOSampleData:
        # should only get here if there is a metadata_annotation
        assert self.metadata_annotation is not None
        field_results: dict[str, PPOFieldResult] = {} # output data
        failed_fields = {}
        if self.metadata_annotation.issues is not None:
            failed_fields = {
                issue.field: issue for issue in self.metadata_annotation.issues.issues
            }

        for field in self.metadata_annotation.metadata:
            if field in failed_fields:
                meta_issue = failed_fields[field]
                qc = "FAIL"
                issue = meta_issue.message
            elif field in self.metadata_annotation.changes:
                qc = "WARN"
                new_val = self.metadata_annotation.changes[field]
                issue = f"Default value automatically applied: {new_val}"
            else:
                qc = "PASS"
                issue = ""

            field_results[field] = {
                "QC": qc,
                "Issue": issue
            }
        res: PPOSampleData = {
                    "data": self.metadata_annotation.metadata,
                    "field_results": field_results
                }
        return res


def write_ppo(
    *,
    file_path: str="PipelineProcessOutputs.json",
    srr: str|None=None,
    samn: str|None=None,
    submission: str|None=None,
    submission_dir: str|None=None,
    issues: list[str]|None=None,
    metadata_annotation: MetadataAnnotation|None=None,
    metadata_failure: MetadataFailure|None=None,
    status: str=""
):
    if issues is None:
        issues = []
    ppo = PPO(
        srr=srr,
        samn=samn,
        submission=submission,
        submission_dir=submission_dir,
        issues=issues,
        metadata_annotation=metadata_annotation,
        metadata_failure=metadata_failure,
        status=status
    )
    ppo.to_file(file_path)


def format_ppo_data(
    *,
    srr: str|None=None,
    samn: str|None=None,
    submission: str|None=None,
    submission_dir: str|None=None,
    issues: list[str]|None=None,
    metadata_annotation: MetadataAnnotation|None=None,
    metadata_failure: MetadataFailure|None=None,
    status: str=""
) -> PPOData:
    if issues is None:
        issues = []
    ppo = PPO(
        srr=srr,
        samn=samn,
        submission=submission,
        submission_dir=submission_dir,
        issues=issues,
        metadata_annotation=metadata_annotation,
        metadata_failure=metadata_failure,
        status=status
    )

    return ppo.build_ppo()



