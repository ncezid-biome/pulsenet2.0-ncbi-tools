from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from pn_ncbi_pkg.metadata import (
    BioSamplePackage,
    validate_existing_biosample_xml,
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

if TYPE_CHECKING:
    pass


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "validate-bs-xml",
        help="Validate submission.xml for downstream BioSample metadata edit",
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

    try:
        if args.original_submission_xml:
            record = load_submission_xml(args.original_submission_xml)

        else:
            record = load_biosample_xml(args.existing_biosample_xml)

        existing_metadata = bs_to_metadata(record)
        existing_metadata.package = meta_package
    except XMLParseError as e:
        errors = [f"Unable to parse biosample xml: {e!s}"]
        write_ppo(file_path=args.out_ppo, issues=errors)
        return 0

    annotation = validate_existing_biosample_xml(existing_metadata)
    write_ppo(file_path=args.out_ppo, issues=[], metadata_annotation=annotation)
    return 0

