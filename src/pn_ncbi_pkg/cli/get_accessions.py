from __future__ import annotations

import argparse

from pn_ncbi_pkg.connection import (
    ConnectionConfigError,
    NCBIConnectionError,
    get_connection,
)
from pn_ncbi_pkg.report import Report


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "get-accessions",
        help="Retrieve report.xml from NCBI FTP and try to extract accessions",
    )
    add_arguments(parser)
    parser.set_defaults(func=run)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--sample-name",
        help="name of sample submitted to NCBI",
        metavar="",
        required=True
    )
    parser.add_argument(
        "--submission-type",
        help="Test or Production",
        metavar="",
        required=True
    )
    parser.add_argument(
        "--out-ppo",
        metavar="",
        default="PipelineProcessOutputs.json",
        help="path to write output json"
    )
    parser.add_argument(
        "--protocol",
        help="use ftp or sftp?",
        choices=["ftp", "sftp"],
        default="sftp"
    )
    parser.add_argument(
        "--config-path",
        help="submission config with username and password info",
        metavar="",
        default="/tostadas/conf/submission_config.yml"
    )
    parser.add_argument(
        "--sra-only",
        help="don't retrieve biosample submission report",
        action="store_true"
    )
    parser.add_argument(
        "--zero-exit",
        help="suppress non-error uses of non-zero exit codes",
        action="store_true",
        required=False
    )


def run(args: argparse.Namespace) -> int:
    submission_dir = f"/submit/{args.submission_type}/{args.sample_name}"
    try:
        connection =  get_connection(args.protocol, args.config_path)
        report = Report.from_server(connection, submission_dir)
    except ConnectionConfigError as error:
        report = Report(errors=[str(error)], submission_dir=submission_dir)
        report.vote_stop()
    except NCBIConnectionError as error:
        report = Report(errors=[str(error)], submission_dir=submission_dir, status="Processing")
        report.vote_retry()

    report.to_file(args.out_ppo)
    if report.stop or args.zero_exit:
        return 0
    return 2
