from ...metadata import Metadata
from .model import BioSampleRecord


def to_metadata(bs_record: BioSampleRecord) -> Metadata:
    data: dict[str, str] = {
        "biosample": bs_record.biosample,
        "bioproject": bs_record.bioproject,
        "spuid": bs_record.spuid,
        "spuid_namespace": bs_record.spuid_namespace,
        "organism": bs_record.organism,
    }
    data.update(bs_record.attrs)
    return Metadata(
        data=data,
        package=bs_record.package
    )
