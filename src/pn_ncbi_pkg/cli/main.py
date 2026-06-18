from __future__ import annotations

import argparse
import sys
from importlib.metadata import version

from pn_ncbi_pkg.cli import (
    get_accessions,
    get_submission_dir,
    make_biosample_edit_xml,
    make_submission_xml,
    prepare_csv,
    submit,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pn-ncbi")
    parser.add_argument("--version", action="version", version=version("pn_ncbi_pkg"))

    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_csv.add_parser(subparsers)
    make_submission_xml.add_parser(subparsers)
    make_biosample_edit_xml.add_parser(subparsers)
    submit.add_parser(subparsers)
    get_submission_dir.add_parser(subparsers)
    get_accessions.add_parser(subparsers)

    return parser

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
