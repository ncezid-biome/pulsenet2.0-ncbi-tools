import csv

from ...submission import SubmissionDB
from ..packages import BioSamplePackage
from .model import Metadata


def metadata_from_csv(file: str, package: BioSamplePackage | None = None) -> Metadata:
    with open(file) as fin:
        contents = csv.reader(fin)
        metadata_cols, sample = [row for row in contents][:2]
    data = {k: v for k, v in zip(metadata_cols, sample, strict=True)}
    return Metadata(data, package=package)


def metadata_to_xml(
        metadata: Metadata,
        file_name: str,
        submission_yaml: str,
        submission_type: SubmissionDB,
        biosample_edit: bool = False
    ) -> None:
    from ...submission import BiosampleSubmission, CombinedSubmission, SRASubmission
    match submission_type:
        case SubmissionDB.SRA:
            xml = SRASubmission.from_yaml(
                submission_yaml,
                **metadata
            )
        case SubmissionDB.BIOSAMPLE:
            if metadata.package is None:
                raise ValueError("metadata package is required for BioSample submissions")
            xml = BiosampleSubmission.from_yaml(
                submission_yaml,
                **metadata,
                package=metadata.package,
                edit=biosample_edit
            )
        case SubmissionDB.BOTH:
            if metadata.package is None:
                raise ValueError("metadata package is required for BioSample submissions")
            xml = CombinedSubmission.from_yaml(
                submission_yaml,
                **metadata,
                package=metadata.package
            )
    xml.to_file(file_name)
