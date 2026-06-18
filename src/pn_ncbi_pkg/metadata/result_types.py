from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, TypeAlias

from ..result import Result

if TYPE_CHECKING:
    from .metadata_obj import Metadata

@dataclass(frozen=True)
class MetadataPatch:
    set_values: dict[str, str] = field(default_factory=dict)
    remove_fields: tuple[str, ...] = ()

    @classmethod
    def no_change(cls) -> MetadataPatch:
        """Used to indicate a success with no changes needed"""
        return cls()

class MetadataPhase(Enum):
    """Phases that can find metadata issues"""
    STANDARDIZATION = "standardization"
    VALIDATION = "validation"

@dataclass(frozen=True)
class MetadataIssue:
    message: str
    phase: MetadataPhase
    field: str
    rule: str
    value: str


@dataclass(frozen=True)
class MetadataFailure:
    issues: tuple[MetadataIssue, ...]

    def messages(self) -> list[str]:
        return [issue.message for issue in self.issues]


    @classmethod
    def single(cls, issue: MetadataIssue) -> MetadataFailure:
        return cls((issue,))


    @classmethod
    def issue(
        cls,
        *,
        phase: MetadataPhase,
        message: str,
        field: str,
        rule: str,
        value: str,
    ) -> MetadataFailure:
        return cls.single(MetadataIssue(
            phase=phase,
            field=field,
            rule=rule,
            message=message,
            value=value
        ))


TransformResult: TypeAlias = Result[MetadataPatch, MetadataFailure]

ValidationResult: TypeAlias = Result[None, MetadataFailure]

MetadataResult: TypeAlias = Result["Metadata", MetadataFailure]
