from __future__ import annotations

import re
from collections.abc import Callable
from typing import TYPE_CHECKING

from pn_ncbi_pkg.result import Err, Ok

from ...result_types import MetadataFailure, MetadataPhase
from .base_rules import FieldEditValidationRule, FieldValidationRule, ValidationRule

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ...metadata_obj import Metadata
    from ...result_types import ValidationResult


class MandatoryField(FieldValidationRule):
    """Check if mandatory field is provided.

    If the field is found return Ok(FieldValues({})).
    Else return an error.
    """
    def __init__(self, *, field: str):
        super().__init__(field=field)

    def __call__(self, metadata: dict[str, str]) -> ValidationResult:
        # return value if found and not blank
        if self.field in metadata and metadata[self.field] != "":
            return Ok(None)

        # otherwise this validation was failed
        return Err(MetadataFailure.issue(
            phase=MetadataPhase.VALIDATION,
            field=self.field,
            rule=type(self).__name__,
            message=f"{self.field} is required.",
            value=""
        ))


class MandatoryGroup(ValidationRule):
    """Check if at least one member of mandatory group is provided.

    If one or more field is found return Ok(FieldValues({})).
    Else return an error.
    """
    def __init__(self, *, fields: Iterable[str]):
        self.fields = fields

    def __call__(self, metadata: Metadata) -> ValidationResult:
        found: list[str] = []
        for field in self.fields:
            if field in metadata and metadata[field] != "":
                found.append(field)


        if len(found) == 0:
            # otherwise this validation was failed
            return Err(MetadataFailure.issue(
                phase=MetadataPhase.VALIDATION,
                field=f"field group: {','.join(self.fields)}",
                rule=type(self).__name__,
                message=f"At least one of {','.join(self.fields)} is required.",
                value=""
            ))

        return Ok(None)


class ControlledLanguageField(FieldValidationRule):
    """Check if value for field is one of the controlled language options"""
    def __init__(self, *, field: str, acceptable_values: set[str],
                 case_sensitive: bool=False):
        super().__init__(field=field)
        self._case_sensitive = case_sensitive
        self._accepted_values = frozenset(
            self._normalize(value) for value in acceptable_values
        )

    def _normalize(self, value: str) -> str:
        value = str(value).strip()
        return value if self._case_sensitive else value.casefold()


    def __call__(self, metadata: Metadata) -> ValidationResult:
        # return if value not found
        if self.field not in metadata:
            return Ok(None)

        # validate value is in accepted set
        value = metadata[self.field].strip()

        if not self._case_sensitive:
            value = value.casefold()
        if value in self._accepted_values:
            return Ok(None)

        # otherwise this validation was failed
        return Err(MetadataFailure.issue(
            phase=MetadataPhase.VALIDATION,
            field=self.field,
            rule=type(self).__name__,
            message=f"{self.field} is a controlled language field, but {metadata[self.field]} is "
                    f"not an accepted value.",
            value=metadata[self.field]
        ))


class ControlledLanguageSubField(FieldValidationRule):
    def __init__(self, *, field: str, acceptable_values: set[str],
                 get_subvalue_method: Callable[[str], str], case_sensitive: bool=False):
        super().__init__(field=field)
        self._case_sensitive = case_sensitive
        self._accepted_values = frozenset(
            self._normalize(value) for value in acceptable_values
        )
        self.get_subvalue = get_subvalue_method

    def _normalize(self, value: str) -> str:
        value = str(value).strip()
        return value if self._case_sensitive else value.casefold()


    def __call__(self, metadata: Metadata) -> ValidationResult:
        # return if value not found
        if self.field not in metadata:
            return Ok(None)

        # validate value is in accepted set
        value = self.get_subvalue(metadata[self.field].strip())

        if not self._case_sensitive:
            value = value.casefold()
        if value in self._accepted_values:
            return Ok(None)

        # otherwise this validation was failed
        return Err(MetadataFailure.issue(
            phase=MetadataPhase.VALIDATION,
            field=self.field,
            rule=type(self).__name__,
            message=f"{self.field} is a controlled language field, but {metadata[self.field]} is "
                    f"not an accepted value.",
            value=metadata[self.field]
            )
        )


class RegexField(FieldValidationRule):
    """Check if value for field matches expected regex"""
    def __init__(self, *, field: str, pattern: str,
                 case_sensitive: bool=False):
        super().__init__(field=field)
        flags = 0 if case_sensitive else re.IGNORECASE
        self._pattern = re.compile(pattern, flags)
        self._case_sensitive = case_sensitive

    def __call__(self, metadata: Metadata) -> ValidationResult:
        # return if value not found
        if self.field not in metadata:
            return Ok(None)

        # validate value is in accepted set
        value = metadata[self.field].strip()

        if self._pattern.fullmatch(value):
            return Ok(None)

        return Err(MetadataFailure.issue(
            phase=MetadataPhase.VALIDATION,
            field=self.field,
            rule=type(self).__name__,
            message=f"{self.field} has invalid format: {value}.",
            value= value
        ))


class ImmutableField(FieldEditValidationRule):
    """Check if immutable field is provided.

    If the field is found, check if the value is different from the existing
    If the value is absent or identical to the existing value return Ok(FieldValues({})).
    Else return an error.
    """
    def __init__(self, *, field: str):
        super().__init__(field=field)

    def __call__(self, existing_metadata: dict[str, str], update_metadata: dict[str, str]) -> ValidationResult:
        if self.field not in update_metadata:
            return Ok(None)

        if existing_metadata.get(self.field) == update_metadata.get(self.field):
            return Ok(None)

        return Err(MetadataFailure.issue(
            phase=MetadataPhase.VALIDATION,
            field=self.field,
            rule=type(self).__name__,
            message=(
                f"{self.field} cannot be updated automatically. "
                "Contact pulsenet@cdc.gov to update this field."
            ),
            value=update_metadata.get(self.field, "")
        ))
