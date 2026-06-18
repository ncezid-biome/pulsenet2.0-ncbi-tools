import argparse
import sys
from time import sleep

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
        "submit",
        help="Submit files for SRA/BioSample submissions",
    )
    add_arguments(parser)
    parser.set_defaults(func=run)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--submission-dir",
        help="name of directory to create and populate with submission files",
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
        "--files",
        help="files to be submitted (e.g., submission.xml, reads)",
        metavar="",
        nargs="+"
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
        metavar="",
        default="PipelineProcessOutputs.json",
        help="path to write output json"
    )


def run(args: argparse.Namespace) -> int:
    submission_dir = f"/submit/{args.submission_type}/{args.submission_dir}"
    try:
        connection = get_connection(args.protocol, args.submission_yaml)
        submission_dir = f"/submit/{args.submission_type}/{args.submission_dir}"
    except (ConnectionConfigError, NCBIConnectionError, ) as error:
        write_ppo(file_path=args.out_ppo, issues=[str(error)], submission_dir=submission_dir)
        return 0

    try:
        # Create and cd to submission dir
        if connection.file_exists(submission_dir):
            print(f"A Submission already exists at {args.submission_dir}\n", file=sys.stderr)
            return 1
        else:
            connection.make_directory(submission_dir)
        connection.change_directory(submission_dir)

        # upload files
        for file in args.files:
            fname = file.split("/")[-1]
            connection.upload_file(file, fname)

        # upload submit.ready file after a short delay to make sure everything else is up
        sleep(5)
        with open("submit.ready", 'w') as _:
            pass

        connection.upload_file("submit.ready", "submit.ready")
        write_ppo(file_path=args.out_ppo, submission_dir=args.submission_dir)
        return 0

    except Exception as e:
        print(f"caught exception: {e}")
        error = f"Issue submitting sample: {e}"
        write_ppo(file_path=args.out_ppo, issues=[error], submission_dir=args.submission_dir)
        return 0
