from dataclasses import dataclass

from ..packages import BioSamplePackage


@dataclass(frozen=True)
class BioSampleRecord:
    biosample: str
    bioproject: str
    spuid: str
    spuid_namespace: str
    package: BioSamplePackage
    organism: str
    attrs: dict[str, str]

