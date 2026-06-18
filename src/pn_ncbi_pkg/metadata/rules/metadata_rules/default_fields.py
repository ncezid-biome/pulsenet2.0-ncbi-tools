from __future__ import annotations

from typing import TYPE_CHECKING

from pn_ncbi_pkg.result import Ok

from ...result_types import MetadataPatch
from .base_rules import DefaultRule

if TYPE_CHECKING:
    from ...metadata_obj import Metadata
    from ...result_types import TransformResult


class DefaultField(DefaultRule):
    def __init__(self, *, field: str, value: str):
        super().__init__(field=field)
        self.value = value.strip()

    def __call__(self, metadata: Metadata) -> TransformResult:
        if self.field not in metadata or metadata[self.field] == "":
            return Ok(MetadataPatch(set_values={self.field: self.value}))

        return Ok(MetadataPatch.no_change())
