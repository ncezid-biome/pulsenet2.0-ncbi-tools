import json


def write_ppo(
    *,
    file_path: str="PipelineProcessOutputs.json",
    srr: str|None=None,
    samn: str|None=None,
    submission: str|None=None,
    submission_dir: str|None=None,
    issues: list[str]|None=None,
    status: str=""
):
    if issues is None:
        issues = []
    output_data = format_ppo_data(
        srr=srr,
        samn=samn,
        submission=submission,
        submission_dir=submission_dir,
        issues=issues,
        status=status
    )
    with open(file_path, "w") as fout:
        json.dump(output_data, fout, indent=4)

def format_ppo_data(
    *,
    srr: str|None=None,
    samn: str|None=None,
    submission: str|None=None,
    submission_dir: str|None=None,
    issues: list[str]|None=None,
    status: str=""
) -> dict[str, str|dict[str, str|None|list[str]]]:
    if issues is None:
        issues = []
    return {
        "metadata": {
            "SRR_ID": srr,
            "NCBI_ACCESSION": samn,
            "Submission": submission,
            "Submission_dir": submission_dir
        },
        "qc": {
            "result": "PASS" if len(issues) == 0 else "FAIL",
            "issues": issues
        },
        "status": status
    }
