from __future__ import annotations

from typing import TYPE_CHECKING

from pn_ncbi_pkg.submission import SubmissionDB

from ...packages import BioSamplePackage
from . import rules

if TYPE_CHECKING:
    from ..metadata_rules.validation_fields import (
        ControlledLanguageField,
        ControlledLanguageSubField,
        ImmutableField,
        MandatoryField,
        MandatoryGroup,
        RegexField,
    )


def get_validation_rules(
    submission_type: SubmissionDB,
    metadata_package: BioSamplePackage | None=None,
) -> tuple[MandatoryField | MandatoryGroup | ControlledLanguageField | ControlledLanguageSubField | RegexField, ...]:
    match submission_type:
        case SubmissionDB.SRA:
            return validate_sra_only

        case SubmissionDB.BIOSAMPLE:
            if metadata_package is None:
                raise ValueError("metadata_package is required for BioSample submissions")
            match metadata_package:
                case BioSamplePackage.OHE:
                    return validate_biosample_onehealthenteric_1_0
                case BioSamplePackage.PATH:
                    return validate_biosample_pathogen_cl_1_0

        case SubmissionDB.BOTH:
            if metadata_package is None:
                raise ValueError("metadata_package is required for BioSample submissions")
            match metadata_package:
                case BioSamplePackage.OHE:
                    return validate_sra_addon + validate_biosample_onehealthenteric_1_0
                case BioSamplePackage.PATH:
                    return validate_sra_addon + validate_biosample_pathogen_cl_1_0


def get_edit_validation_rules() -> tuple[MandatoryField | RegexField, ...]:
    return (rules.MANDATORY_BIOSAMPLE + rules.CONTROLLED_BIOSAMPLE)


def get_patch_fields_validation_rules() -> tuple[ImmutableField, ...]:
    return rules.BS_IMMUTABLE_EDIT_FIELDS


validate_biosample_pathogen_cl_1_0 = (
    rules.ALL_MANDATORY
    + rules.BS_ALL_MANDATORY
    + rules.BS_PATH_MANDATORY
    + rules.BS_ALL_CONTROLLED
)


validate_biosample_onehealthenteric_1_0 = (
    rules.ALL_MANDATORY
    + rules.BS_ALL_MANDATORY
    + rules.BS_OHE_MANDATORY
    + rules.BS_ALL_CONTROLLED
    + rules.BS_OHE_CONTROLLED
)

validate_sra_addon = (
    rules.SRA_MANDATORY
    + rules.SRA_CONTROLLED
)

validate_sra_only = (
    rules.ALL_MANDATORY
    + rules.SRA_MANDATORY
    + rules.MANDATORY_BIOSAMPLE
    + rules.SRA_CONTROLLED
    + rules.CONTROLLED_BIOSAMPLE
)

