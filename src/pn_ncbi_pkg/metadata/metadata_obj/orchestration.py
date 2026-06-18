from __future__ import annotations

from typing import TYPE_CHECKING

from pn_ncbi_pkg.result import Err, Ok
from pn_ncbi_pkg.submission import SubmissionDB

from ..result_types import MetadataFailure, MetadataIssue, MetadataPatch
from ..rules.defaults import get_default_rules
from ..rules.standardization import get_standardization_rules
from ..rules.validation import (
    get_edit_validation_rules,
    get_patch_fields_validation_rules,
    get_validation_rules,
)
from .model import Metadata

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ..result_types import MetadataIssue, MetadataResult, ValidationResult
    from ..rules.metadata_rules.base_rules import (
        EditValidationRule,
        TransformRule,
        ValidationRule,
    )


def run_transforms(
    metadata: Metadata,
    rules: Iterable[TransformRule]
) -> MetadataResult:
    """Apply mutating rules in order.

    Transform rules may add, replace, or remove fields.
    If any transform fails, stop before later phases.
    """
    for rule in rules:
        match rule(metadata):
            case Ok(patch):
                metadata.apply(patch)
            case Err(failure):
                # Return as soon as an issue is found
                # so that order-dependence doesn't lead
                # to unexpected behavior
                return Err(failure)

    return Ok(metadata)


def run_validations(
    metadata: Metadata,
    rules: Iterable[ValidationRule]
) -> ValidationResult:
    """Run checking-only rules.

    Validation rules should not change metadata. They only report issues.
    """
    issues: list[MetadataIssue] = []

    for rule in rules:
        match rule(metadata):
            case Ok(_):
                pass
            case Err(failure):
                issues.extend(failure.issues)

    if issues:
        return Err(MetadataFailure(tuple(issues)))

    return Ok(None)


def run_edit_validations(
        existing_meta: Metadata,
        update_meta: Metadata,
        rules: Iterable[EditValidationRule]
        ) -> ValidationResult:
    issues: list[MetadataIssue] = []
    for rule in rules:
        match rule(existing_meta, update_meta):
            case Ok(_):
                pass
            case Err(failure):
                issues.extend(failure.issues)

    if issues:
        return Err(MetadataFailure(tuple(issues)))

    return Ok(None)


def prepare_metadata_for_submission(metadata: Metadata, submission_type: SubmissionDB) -> MetadataResult:
    """standardize fields, populate defaults, then validate

    Returns a standardized, validated copy of the metadata
    """
    # Copy so mutations are not in-place
    # shallow copy sufficient as `dict[str, str]` contents are immutable
    metadata = Metadata(metadata.copy(), package=metadata.package)

    standardizers = get_standardization_rules(submission_type)
    defaults = get_default_rules(submission_type, metadata.package)
    validators = get_validation_rules(submission_type, metadata.package)

    match run_transforms(metadata, standardizers):
        case Ok(transformed):
            metadata = transformed
        case Err(failure):
            return Err(failure)

    match run_transforms(metadata, defaults):
        case Ok(transformed):
            metadata = transformed
        case Err(failure):
            return Err(failure)

    match run_validations(metadata, validators):
        case Ok():
            return Ok(metadata)
        case Err(failure):
            return Err(failure)


def prepare_metadata_for_edit(existing_meta: Metadata, update_meta: Metadata) -> MetadataResult:
    """validate existing data, standardize and apply metadata patch, then validate patched metadata

    defaults are not applied to avoid silently editing existing metadata with values other than
    those explicitly provided by the user in their patch

    Returns a standardized, validated copy of the patched metadata.
    """
    target_package = update_meta.package or existing_meta.package

    # Check if any current fields have validation errors
    existing_validators = get_validation_rules(submission_type=SubmissionDB.BIOSAMPLE, metadata_package=target_package)

    existing_failure = None
    match run_validations(existing_meta, existing_validators):
        case Ok():
            # nothing to do
            pass
        case Err(failure):
            # store these to check if the update fixes them all
            existing_failure = failure

    # standardize update metadata
    cleaned_update_meta = Metadata(update_meta.copy(), package=target_package)
    update_standardizers = get_standardization_rules(submission_type=SubmissionDB.BIOSAMPLE)
    match run_transforms(cleaned_update_meta, update_standardizers):
        case Ok(transformed):
            cleaned_update_meta = transformed
        case Err(failure):
            return Err(failure)

    # validate edit
    edit_validators = get_patch_fields_validation_rules()
    match run_edit_validations(existing_meta, cleaned_update_meta, edit_validators):
        case Ok():
            # good to proceed
            pass
        case Err(failure):
            return Err(failure)

    # patch existing meta and overwrite with new package (if different)
    patch = MetadataPatch(cleaned_update_meta)
    patched_meta = Metadata(existing_meta.copy(), package=target_package)
    patched_meta.apply(patch)

    # run ordinary validations for this package
    validators = (
        get_validation_rules(SubmissionDB.BIOSAMPLE, target_package)
        + get_edit_validation_rules()
    )

    match run_validations(patched_meta, validators):
        case Ok():
            # either no issues, or patch fixed existing issues
            return Ok(patched_meta)
        case Err(failure):
            if existing_failure is None:
                # No existing failures to compare new ones against
                return Err(failure)

            # otherwise we need to figure out where the failure arose
            patched_failure = failure

            return Err(
                _rewrite_preexisting_failures(
                    existing_failure,
                    patched_failure,
                    set(cleaned_update_meta)
                )
            )

def _rewrite_preexisting_failures(
    existing_failure: MetadataFailure,
    patched_failure: MetadataFailure,
    patched_fields: Iterable[str]
) -> MetadataFailure:
    """
    Revise issue wording to clarify pre-existing vs user-introduced metadata issues

    If there are issues with the patched data, check if any of those issues were in the existing sample.
    Overwrite new failures with the versions from the existing sample.
    We need to find issues in the original sample that were not touched by the path.
    Those fields need to be reported back to the user as needing to be patched.
    Issues with patched fields should be reported as regular metadata validation failures.
    """

    existing_issue_fields = set([iss.field for iss in existing_failure.issues])
    preexisting_issues = tuple(
        iss for iss in patched_failure.issues if (
            (iss.field in existing_issue_fields) # issue in original
            and (iss.field not in patched_fields) # and issue wasn't patched
        )
    )
    if len(preexisting_issues) == 0:
        return patched_failure

    new_issues = tuple(
        iss for iss in patched_failure.issues if (
            (iss.field not in existing_issue_fields) # new issue
            or (iss.field in patched_fields) # or issue remains after patch
        )
    )

    fixed_message_preexisting = tuple(
        MetadataIssue(
            message=f"issue with existing sample metadata must be fixed: {iss.message}",
            phase=iss.phase,
            field=iss.field,
            rule=iss.rule,
            value=iss.value
        ) for iss in preexisting_issues
    )

    return MetadataFailure(fixed_message_preexisting + new_issues)
