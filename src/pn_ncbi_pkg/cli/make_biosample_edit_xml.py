from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from pn_ncbi_pkg.metadata import (
    BioSamplePackage,
    metadata_from_csv,
    metadata_to_xml,
    prepare_metadata_for_edit,
)
from pn_ncbi_pkg.metadata.biosample_record.conversion import (
    to_metadata as bs_to_metadata,
)
from pn_ncbi_pkg.metadata.biosample_record.io import (
    XMLParseError,
    load_biosample_xml,
    load_submission_xml,
)
from pn_ncbi_pkg.report.ppo import write_ppo
from pn_ncbi_pkg.result import Err, Ok
from pn_ncbi_pkg.submission import SubmissionDB

from .common import format_errors

if TYPE_CHECKING:
    from pn_ncbi_pkg.metadata import Metadata


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "make-bs-edit-xml",
        help="Create submission.xml for BioSample metadata edit",
    )
    add_arguments(parser)
    parser.set_defaults(func=run)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--existing-biosample-xml",
        metavar="",
        help="The sample xml retrieved using entrez utils"
    )
    source.add_argument(
        "--original-submission-xml",
        metavar="",
        help="The submission.xml used when this sample was originally submitted to BioSample"
    )

    parser.add_argument(
        "--update-csv",
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


def write_failure(args: argparse.Namespace, errors: list[str]) -> None:
    with open(args.out_xml, 'w') as _:
        pass
    write_ppo(file_path=args.out_ppo, issues=errors)

def run(args: argparse.Namespace) -> int:
    meta_package = (
        BioSamplePackage(args.metadata_package)
        if args.metadata_package
        else None
    )

    update_metadata: Metadata = metadata_from_csv(args.update_csv, meta_package)

    try:
        if args.original_submission_xml:
            biosample = update_metadata.get("biosample")
            if biosample is None:
                errors = ["biosample is required for an edit using the original submission xml"]
                write_failure(args, errors)
                return 0
            record = load_submission_xml(args.original_submission_xml, biosample)

        else:
            record = load_biosample_xml(args.existing_biosample_xml)

        existing_metadata = bs_to_metadata(record)
    except XMLParseError as e:
        errors = [f"Unable to parse biosample xml: {e!s}"]
        write_failure(args, errors)
        return 0

    match prepare_metadata_for_edit(existing_metadata, update_metadata):
        case Ok(fixed_metadata):
            metadata = fixed_metadata

            metadata_to_xml(
                metadata=metadata,
                file_name=args.out_xml,
                submission_yaml=args.submission_yaml,
                submission_type=SubmissionDB.BIOSAMPLE,
                biosample_edit=True
            )
            write_ppo(file_path=args.out_ppo, issues=[])
            return 0

        case Err(metadata_errors):
            errors = format_errors(metadata_errors)
            write_failure(args, errors)
            return 0
