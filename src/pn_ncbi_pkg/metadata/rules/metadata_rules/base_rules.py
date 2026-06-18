from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from ...result_types import MetadataPatch

if TYPE_CHECKING:
    from pn_ncbi_pkg.result import Result

    from ...metadata_obj import Metadata
    from ...result_types import MetadataFailure, ValidationResult

SuccessT = TypeVar("SuccessT")

class MetadataRule(ABC, Generic[SuccessT]):
    """Base class for metadata rules for standardization, defaulting, and validation"""

    @abstractmethod
    def __call__(self, metadata: Metadata) -> Result[SuccessT, MetadataFailure]:
        """Given a dict of fields (keys) and data (values) for a sample, apply this rule"""
        ...


class FieldScopedRuleMixin:
    """Add field-specific scope to rule"""
    def __init__(self, *, field: str):
        self.field = field.lower().strip()


class TransformRule(MetadataRule[MetadataPatch], ABC):
    pass


class ValidationRule(MetadataRule[None], ABC):
    pass


class StandardizationRule(TransformRule, ABC):
    pass


class DefaultRule(FieldScopedRuleMixin, TransformRule, ABC):
    pass


class FieldValidationRule(FieldScopedRuleMixin, ValidationRule, ABC):
    pass


### Specific to edit pipeline validations

class EditValidationRule(ABC):
    @abstractmethod
    def __call__(
        self,
        existing_metadata: Metadata,
        update_metadata: Metadata,
    ) -> ValidationResult:
        ...


class FieldEditValidationRule(FieldScopedRuleMixin, EditValidationRule, ABC):
    pass
