
import json
from pathlib import Path

from pn_ncbi_pkg.metadata import BioSamplePackage, Metadata


class _DeleteSentinel:
    pass


_DELETE = _DeleteSentinel()


def valid_ohe_metadata(**overrides: str | _DeleteSentinel):
    data = {
        "sample": "test_sample",
        "strain": "strain_name",
        "sample_name": "test_sample",
        "ncbi-spuid": "spuid",
        "ncbi-spuid_namespace": "some_namespace",
        "ncbi-bioproject": "PRJNA000000",
        "author": "CDC",
        "serovar": "serovar_name",
        "source_type": "food",
        "isolate_name_alias": "test_sample",
        "isolation_source": "source",
        "geo_loc_name": "USA:TX",
        "organism": "Escherichia coli",
        "collection_date": "2025-01-01",
        "collected_by": "collector",
        "project_name": "project",
        "sequenced_by": "sequencer",
        "intended_consumer": "missing",
        "food_origin": "origin",
        "food_processing_method": "food_proc_method",
        "purpose_of_sampling": "purpose",
    }
    for key, value in overrides.items():
        if isinstance(value, _DeleteSentinel):
            data.pop(key, None)
        else:
            data[key] = value
    return Metadata(data, package=BioSamplePackage.OHE)


def valid_ill_sra_metadata(**overrides: str | _DeleteSentinel):
    data = {
        "file1": "r1.fq",
        "file2": "r2.fq",
        "ncbi-spuid": "spuid",
        "ncbi-spuid_namespace": "some_namespace",
        "ncbi-bioproject": "PRJNA000000",
        "biosample": "SAMN1234",
        "illumina_sequencing_instrument": "Illumina MiSeq",
        "illumina_library_strategy": "WGS",
        "illumina_library_source": "GENOMIC",
        "illumina_library_selection": "RANDOM",
        "illumina_library_layout": "paired",
        "illumina_library_protocol": "Illumina DNA Prep",
    }
    for key, value in overrides.items():
        if isinstance(value, _DeleteSentinel):
            data.pop(key, None)
        else:
            data[key] = value
    return Metadata(data)


def error_text(result):
    payload = getattr(result, "error", result)
    if isinstance(payload, (list, tuple)):
        return "\n".join(str(item) for item in payload)
    return str(payload)


class FakeReportConnection:
    def __init__(
            self,
            *,
            report_xml: str="",
            change_directory_exc: BaseException | None =None,
            read_exc: BaseException | None =None
        ):
        self.report_xml = report_xml
        self.change_directory_exc = change_directory_exc
        self.read_exc = read_exc
        self.changed_to = None
        self.closed = False

    def change_directory(self, directory: str) -> None:
        if self.change_directory_exc:
            raise self.change_directory_exc
        self.changed_to = directory

    def read_file(self, remote_path: str) -> str:
        if self.read_exc:
            raise self.read_exc
        return self.report_xml

    def close_connection(self) -> None:
        self.closed = True


def load_json(path):
    return json.loads(Path(path).read_text())
