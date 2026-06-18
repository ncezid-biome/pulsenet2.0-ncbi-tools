from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..packages import BioSamplePackage
    from ..result_types import MetadataPatch


class Metadata(dict[str,str]):
    def __init__(
        self,
        data: dict[str, str] | None = None,
        *,
        package: BioSamplePackage | None = None,
    ):
        super().__init__(data or {})
        self.package = package

    def apply(self, mp: MetadataPatch, **kwargs: str):
        self.update(mp.set_values, **kwargs)
        for field in mp.remove_fields:
            del self[field]









