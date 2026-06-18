from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from pn_ncbi_pkg.metadata import (
    BioSamplePackage,
    metadata_from_csv,
    metadata_to_xml,
    prepare_metadata_for_submission,
)
from pn_ncbi_pkg.report.ppo import write_ppo
from pn_ncbi_pkg.result import Err, Ok
from pn_ncbi_pkg.submission import SubmissionDB

from .common import format_errors

if TYPE_CHECKING:
    from pn_ncbi_pkg.metadata import Metadata


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "make-submission-xml",
        help="Create submission.xml for new SRA/BioSample submissions",
    )
    add_arguments(parser)
    parser.set_defaults(func=run)

def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--csv",
        metavar="",
        required=True,
        help="csv file containing sample mapping fields. Only one sample should be in the file"
    )
    parser.add_argument(
        "--metadata-package",
        choices=["OneHealthEnteric.1.0", "Pathogen.cl.1.0"],
        default="OneHealthEnteric.1.0",
        help="desired metadata package"
    )
    parser.add_argument(
        "--submission-db",
        choices=["sra", "biosample", "both"],
        required=True,
        help="desired submission target database(s)"
    )
    parser.add_argument(
        "--submission-yaml",
        metavar="",
        required=True,
        help="yaml file with submitter metadata"
    )
    parser.add_argument(
        "--out-xml",
        metavar="",
        default="submission.xml",
        help="path to write new submission.xml file"
    )
    parser.add_argument(
        "--out-ppo",
        metavar="",
        default="PipelineProcessOutputs.json",
        help="path to write output json"
    )

def run(args: argparse.Namespace) -> int:
    meta_package = (
        BioSamplePackage(args.metadata_package)
        if args.metadata_package
        else None
    )
    submission_db = SubmissionDB(args.submission_db)

    metadata: Metadata = metadata_from_csv(args.csv, meta_package)
    errors = []
    match prepare_metadata_for_submission(metadata, submission_db):
        case Ok(fixed_metadata):
            status = "PASS"
            metadata = fixed_metadata
        case Err(metadata_errors):
            status = "FAIL"
            errors = format_errors(metadata_errors)

    write_ppo(file_path=args.out_ppo, issues=errors)

    if status == "FAIL":
        with open(args.out_xml, 'w') as _:
            pass
        # Having written expected output files, just exit.
        # Let nextflow handle publishing ppo and removing this sample so exit code 0
        return 0


    metadata_to_xml(
        metadata,
        args.out_xml,
        args.submission_yaml,
        submission_db
    )
    return 0
