import argparse
import sys

from pn_ncbi_pkg.connection import (
    ConnectionConfigError,
    NCBIConnectionError,
    get_connection,
)
from pn_ncbi_pkg.report.ppo import write_ppo

SFTP_HOST = "sftp-private.ncbi.nlm.nih.gov"
FTP_HOST = "ftp-private.ncbi.nlm.nih.gov"

def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "get-submission-dirname",
        help="Get the directory name to use for submission to SRA/BioSample",
    )
    add_arguments(parser)
    parser.set_defaults(func=run)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--directory-prefix",
        help="beginning of the directory name to generate",
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
        "--protocol",
        help="use ftp or sftp?",
        choices=["ftp", "sftp"],
        default="sftp"
    )
    parser.add_argument(
        "--submission-yaml",
        help="submission config with username and password info",
        metavar="",
        default="/submission_config.yml"
    )
    parser.add_argument(
        "--out-ppo",
        default="PipelineProcessOutputs.json",
        help="path to write output json"
    )

def run(args: argparse.Namespace) -> int:
    try:
        connection = get_connection(args.protocol, args.submission_yaml)
    except (ConnectionConfigError, NCBIConnectionError, ) as error:
        write_ppo(
            file_path=args.out_ppo,
            issues=[f"Error establishing connection to NCBI: {error}"],
        )
        sys.exit(0)

    base_path = f"/submit/{args.submission_type}/{args.directory_prefix}"
    try:
        # check if a directory exists with just the prefix
        if not connection.file_exists(base_path):
            write_ppo(file_path=args.out_ppo, submission_dir=args.directory_prefix)
            print(args.directory_prefix)
            return 0

        # otherwise check incrementing numbers until an unused directory is found
        n = 1
        new_path = base_path + f"_{n}"
        while connection.file_exists(new_path):
            n += 1
            new_path = base_path + f"_{n}"

        submission_dir = f"{args.directory_prefix}_{n}"

        write_ppo(file_path=args.out_ppo, submission_dir=submission_dir)

        print(submission_dir)
        return 0

    except Exception as e:
        error = f"Issue determining submission directory: {e}"
        write_ppo(file_path=args.out_ppo, issues=[error])
        sys.exit(0)
