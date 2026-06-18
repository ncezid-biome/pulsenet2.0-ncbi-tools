from pn_ncbi_pkg.submission import SubmissionDB

from ...packages import BioSamplePackage
from ..metadata_rules.default_fields import DefaultRule
from .rules import BS_DEFAULT_ALL, BS_DEFAULT_PATH


def get_default_rules(
    submission_type: SubmissionDB,
    package: BioSamplePackage | None=None
) -> tuple[DefaultRule, ...]:
    rules = ()

    match submission_type:
        case SubmissionDB.BIOSAMPLE | SubmissionDB.BOTH:
            rules += BS_DEFAULT_ALL

            match package:
                case BioSamplePackage.PATH:
                    rules += BS_DEFAULT_PATH
                case BioSamplePackage.OHE:
                    pass # No package defaults
                case _:
                    raise NotImplementedError(f"{package} is not a supported BioSample package option")

        case SubmissionDB.SRA:
            pass # No defaults

    return rules
