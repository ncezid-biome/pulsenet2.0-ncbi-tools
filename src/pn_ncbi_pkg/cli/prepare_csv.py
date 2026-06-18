from __future__ import annotations

import argparse
import csv
import gzip
import shutil
from pathlib import Path

READ_SUFFIXES = (
    ".fastq.gz",
    ".fq.gz",
    ".fastq",
    ".fq",
)


def add_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "prepare-csv",
        help=(
            "extract sample row from csv, "
            "copy reads out of input dir, "
            "change to .fastq.gz if needed"
        )
    )
    add_arguments(parser)
    parser.set_defaults(func=run)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--sample",
        metavar="",
        required=True,
        help="sample name"
    )
    parser.add_argument(
        "--csv",
        metavar="",
        required=True,
        help="CSV file containing sample mapping fields"
    )
    parser.add_argument(
        "--drop-column",
        metavar="",
        nargs="*",
        help="Columns to remove from the csv if present"
    )
    parser.add_argument(
        "--out-csv",
        metavar="",
        required=True,
        help="path to write output CSV"
    )
    parser.add_argument(
        "--read-dir",
        metavar="",
        required=False,
        help="path to directory with read files"
    )

def read_metadata_row(csv_path: str, sample: str) -> dict[str, str]:
    with open(csv_path, newline="") as fin:
        rows = [row for row in csv.DictReader(fin) if row.get("sample") == sample]

    if len(rows) != 1:
        raise ValueError(f"Expected exactly one row for sample {sample!r}; found {len(rows)}")

    return dict(rows[0])


def resolve_reads(read_dir: str) -> list[Path]:
    directory = Path(read_dir)
    reads = sorted(
        path for path in directory.iterdir()
        if path.is_file() and path.name.endswith(READ_SUFFIXES)
    )

    return reads


def copy_reads(read_paths: list[Path]) -> list[Path]:
    """copy files out of read dir, standardize extensions, and gzip if needed"""
    new_paths: list[Path] = []
    for read in read_paths:
        if read.name.endswith(".gz"):
            # basic copy, maybe rename
            destination = Path(read.with_suffix('').stem + ".fastq.gz")
            new_paths.append(destination)
            shutil.copy(read, destination)

        else:
            # copy and gzip
            destination = Path(read.stem + ".fastq.gz")
            new_paths.append(destination)
            with open(read, 'rb') as fin:
                with gzip.open(destination, 'wb') as fout:
                    shutil.copyfileobj(fin, fout)

    return new_paths


def write_one_row_csv(row: dict[str, str], out_csv: str) -> None:
    with open(out_csv, "w", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)


def run(args: argparse.Namespace) -> int:
    row = read_metadata_row(args.csv, args.sample)

    if args.read_dir:
        reads = resolve_reads(args.read_dir)
        if len(reads) > 2:
            raise ValueError(f"At most two reads files are allowed. {len(reads)} found")
        prepped_reads = copy_reads(reads)

        row.pop("file_path", None)
        for n, read in enumerate(prepped_reads, start=1):
            row[f"file{n}"] = read.name

    for column in args.drop_column:
        row.pop(column, None)

    write_one_row_csv(row, args.out_csv)
    return 0
