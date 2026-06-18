from __future__ import annotations

import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from pn_ncbi_pkg.metadata.packages import BioSamplePackage

class BaseSubmission(ABC):
    def __init__(self, role: str, role_type: str, name: str, email: str,
                 first: str, last: str, bioproject: str, spuid: str,
                 spuid_namespace: str, comment: str="Not Provided"):
        # init base info
        self.role = role
        self.role_type = role_type
        self.name = name
        self.email = email
        self.first = first
        self.last = last
        self.bioproject = bioproject
        self.spuid = spuid
        self.spuid_namespace = spuid_namespace
        self.comment = comment
        self._xml: ET.Element[str] | None = None

    @property
    def xml(self) -> ET.Element[str]:
        if self._xml is None:
            self.build_xml()
        if self._xml is None:
            raise RuntimeError("build_xml() did not initialize XML")
        return self._xml

    @xml.setter
    def xml(self, data: ET.Element[str]) -> None:
        self._xml = data

    @abstractmethod
    def build_xml(self):
        self._build_doc_skeleton()


    def _build_doc_skeleton(self):
        xml = ET.Element("Submission")
        desc = ET.SubElement(xml, "Description")
        comment = ET.SubElement(desc, 'Comment')
        comment.text = self.comment
        organization = ET.SubElement(
            desc,
            'Organization',
            {
                'role': self.role,
                'type': self.role_type
            }
        )
        name = ET.SubElement(organization, "Name")
        name.text = self.name
        contact = ET.SubElement(organization, "Contact", {"email": self.email})
        first_last = ET.SubElement(contact, "Name")
        first = ET.SubElement(first_last, "First")
        first.text = self.first
        last = ET.SubElement(first_last, "Last")
        last.text = self.last

        self.xml = xml

    @staticmethod
    def _get_common_args_from_yaml(yaml_file: str) -> dict[str, str]:
        args: dict[str, str] = {}
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
            args["role"] = data["Role"]
            args["role_type"] = data["Type"]
            args["name"] = data["Submitting_Org"]
            args["email"] = data["Email"]
            args["first"] = data["Submitter"]["Name"]["First"]
            args["last"] = data["Submitter"]["Name"]["Last"]
        return args


    def to_string(self, pretty: bool=True):
        if pretty:
            return minidom.parseString(
                ET.tostring(self.xml, encoding='utf-8')
            ).toprettyxml(indent="  ")
        else:
            return minidom.parseString(
                ET.tostring(self.xml, encoding='utf-8')
            ).toxml()

    def to_file(self, path: str, pretty: bool=True):
        with open(path, 'w') as fout:
            fout.write(self.to_string(pretty=pretty))


class SRAXMLMixin:
    if TYPE_CHECKING:
        @property
        def xml(self) -> ET.Element[str]: ...

        spuid_namespace: str
        spuid: str
        bioproject: str

    def _init_sra_fields(
        self, *, file1: str, file2: str, instrument_model: str, library_strategy: str,
        library_source: str, library_selection: str, library_layout: str,
        library_construction_protocol: str, library_name: str = "Not Provided",
        sra_namespace: str|None=None,
        sra_samplename: str|None=None,
        sra_only: bool=True,
        biosample: str|None=None,
    ) -> None:
        self.files: list[str] = [file1, file2]
        self.instrument_model = instrument_model
        self.library_strategy = library_strategy
        self.library_source = library_source
        self.library_selection = library_selection
        self.library_layout = library_layout
        self.library_construction_protocol = library_construction_protocol
        self.library_name = library_name
        self.sra_namespace = sra_namespace or self.spuid_namespace + "_sra"
        self.sra_samplename = sra_samplename or self.spuid + "_sra"
        self.biosample = biosample
        self._sra_only = sra_only

    def _build_sra_doc(self) -> None:
        action = ET.SubElement(self.xml, "Action")
        add_files = ET.SubElement(action, "AddFiles", {"target_db": "SRA"})
        for file_path in self.files:
            file = ET.SubElement(add_files, "File", {"file_path": file_path})
            datatype = ET.SubElement(file, "DataType")
            datatype.text = "generic-data"
        for attribute in ["instrument_model", "library_strategy", "library_source",
                          "library_selection", "library_layout",
                          "library_construction_protocol", "library_name"]:
            attr = ET.SubElement(add_files, "Attribute", {"name": attribute})
            attr.text = self.__dict__[attribute]

        bp_attrib = ET.SubElement(add_files, "AttributeRefId", {"name": "BioProject"})
        bp_refid = ET.SubElement(bp_attrib, "RefId")
        primary_id = ET.SubElement(bp_refid, "PrimaryId")
        primary_id.text = self.bioproject


        bs_attrib = ET.SubElement(add_files, "AttributeRefId", {"name": "BioSample"})
        bs_refid = ET.SubElement(bs_attrib, "RefId")
        if self.biosample is not None and self._sra_only:
            bs_id = ET.SubElement(bs_refid, "PrimaryId", {"db": "BioSample"})
            bs_id.text = self.biosample
        else:
            spuid = ET.SubElement(bs_refid, "SPUID", {"spuid_namespace": self.spuid_namespace})
            spuid.text = self.spuid

        sra_spuid = ET.SubElement(add_files, "Identifier")
        spuid = ET.SubElement(sra_spuid, "SPUID", {"spuid_namespace": self.sra_namespace})
        spuid.text = self.sra_samplename


class BioSampleXMLMixin:
    if TYPE_CHECKING:
        @property
        def xml(self) -> ET.Element[str]: ...

        spuid_namespace: str
        spuid: str
        bioproject: str

    def _init_biosample_fields(
        self,
        *,
        package: BioSamplePackage,
        attribs: dict[str, str],
        organism: str | None = None,
        edit: bool = False
    ) -> None:
        self.organism = organism
        self.package = package
        self.bs_attributes = attribs
        self.edit = edit
        if self.edit:
            self.biosample = attribs.pop("biosample")

    def _build_biosample_doc(self) -> None:
        non_bs_fields = {
            "sample",
            "file_path",
            "files",
            "file1",
            "file2",
            "instrument_model",
            "library_strategy",
            "library_source",
            "library_selection",
            "library_layout",
            "library_construction_protocol",
            "library_name",
            "illumina_sequencing_instrument",
            "illumina_library_strategy",
            "illumina_library_source",
            "illumina_library_selection",
            "illumina_library_layout",
            "illumina_library_protocol",
            "sra_namespace",
            "sra_samplename",
            "biosample"
        }

        action = ET.SubElement(self.xml, "Action")
        add_data = ET.SubElement(action, "AddData", {"target_db": "BioSample"})
        data = ET.SubElement(add_data, "Data", {"content_type": "XML"})
        xml_content = ET.SubElement(data, "XmlContent")
        biosample = ET.SubElement(xml_content, "BioSample", {"schema_version": "2.0"})
        sample_id = ET.SubElement(biosample, "SampleId")
        if self.edit:
            primary_id = ET.SubElement(sample_id, "PrimaryId", {"db": "BioSample"})
            primary_id.text = self.biosample
        spuid1 = ET.SubElement(sample_id, "SPUID", {"spuid_namespace": self.spuid_namespace})
        spuid1.text = self.spuid
        ET.SubElement(biosample, "Descriptor") # No content
        if self.organism is not None:
            organism = ET.SubElement(biosample, "Organism")
            org_name = ET.SubElement(organism, "OrganismName")
            org_name.text = self.organism
        bioproject = ET.SubElement(biosample, "BioProject")
        bp_primary = ET.SubElement(bioproject, "PrimaryId")
        bp_primary.text = self.bioproject
        package = ET.SubElement(biosample, "Package")
        package.text = self.package.value
        attribs = ET.SubElement(biosample, "Attributes")
        for name, data in self.bs_attributes.items():
            if name in non_bs_fields:
                continue # sample field just used for nextflow sample naming
            attr = ET.SubElement(attribs, "Attribute", {"attribute_name": name})
            attr.text = data
        identifier = ET.SubElement(add_data, "Identifier")
        spuid2 = ET.SubElement(identifier, "SPUID", {"spuid_namespace": self.spuid_namespace})
        spuid2.text = self.spuid


class SRASubmission(BaseSubmission, SRAXMLMixin):
    def __init__(
        self, *, role: str, role_type: str, name: str, email: str,
        first: str, last: str, bioproject: str, file1: str, file2: str,
        instrument_model: str, library_strategy: str, library_source: str,
        library_selection: str, library_layout: str,
        library_construction_protocol: str,
        library_name: str = "Not Provided",
        spuid: str, spuid_namespace: str,
        sra_namespace: str|None=None,
        sra_samplename: str|None=None,
        comment: str="Not Provided",
        sra_only: bool=True,
        biosample: str|None=None,
        **_: str
    ):
        BaseSubmission.__init__(
            self, role, role_type, name, email, first, last,
            bioproject, spuid, spuid_namespace, comment=comment,
        )
        self._init_sra_fields(
            file1=file1,
            file2=file2,
            instrument_model=instrument_model,
            library_strategy=library_strategy,
            library_source=library_source,
            library_selection=library_selection,
            library_layout=library_layout,
            library_construction_protocol=library_construction_protocol,
            library_name=library_name,
            sra_namespace=sra_namespace,
            sra_samplename=sra_samplename,
            biosample=biosample,
            sra_only=True,
        )
    @classmethod
    def from_yaml(cls, yaml_file: str, **kwargs: str,):
        return cls(sra_only=True, **BaseSubmission._get_common_args_from_yaml(yaml_file), **kwargs)


    def build_xml(self) -> None:
        self._build_doc_skeleton()
        self._build_sra_doc()



class BiosampleSubmission(BaseSubmission, BioSampleXMLMixin):
    def __init__(
        self,
        *,
        role: str,
        role_type: str,
        name: str,
        email: str,
        first: str,
        last: str,
        bioproject: str,
        spuid: str,
        spuid_namespace: str,
        package: BioSamplePackage,
        comment: str="Not Provided",
        organism: str | None=None,
        edit: bool = False,
        **attribs: str
    ):
        BaseSubmission.__init__(
            self, role, role_type, name, email, first, last,
            bioproject, spuid, spuid_namespace, comment=comment,
        )
        self._init_biosample_fields(
            package=package,
            attribs=attribs,
            organism=organism,
            edit=edit
        )


    @classmethod
    def from_yaml(cls, yaml_file: str, *, package: BioSamplePackage, edit: bool = False, **kwargs: str,):
        return cls(**BaseSubmission._get_common_args_from_yaml(yaml_file), package=package, edit=edit, **kwargs)


    def build_xml(self) -> None:
        self._build_doc_skeleton()
        self._build_biosample_doc()



class CombinedSubmission(BaseSubmission, SRAXMLMixin, BioSampleXMLMixin):
    def __init__(self, *, package: BioSamplePackage, organism: str,
        role: str, role_type: str, name: str, email: str,
        first: str, last: str, bioproject: str, spuid: str,
        spuid_namespace: str, comment: str = "Not Provided",
        file1: str, file2: str, instrument_model: str,
        library_strategy: str, library_source: str,
        library_selection: str, library_layout: str,
        library_construction_protocol: str,
        library_name: str = "Not Provided",
        sra_namespace: str | None = None,
        sra_samplename: str | None = None,
        biosample: str | None = None,
        **attribs: str
    ) -> None:
        BaseSubmission.__init__(
            self, role, role_type, name, email, first, last,
            bioproject, spuid, spuid_namespace, comment=comment,
        )
        self._init_sra_fields(
            file1=file1,
            file2=file2,
            instrument_model=instrument_model,
            library_strategy=library_strategy,
            library_source=library_source,
            library_selection=library_selection,
            library_layout=library_layout,
            library_construction_protocol=library_construction_protocol,
            library_name=library_name,
            sra_namespace=sra_namespace,
            sra_samplename=sra_samplename,
            biosample=biosample,
            sra_only=False,
        )
        self._init_biosample_fields(
            organism=organism,
            package=package,
            attribs=attribs,
        )


    @classmethod
    def from_yaml(cls, yaml_file: str, *, package: BioSamplePackage, **kwargs: str,):
        return cls(**BaseSubmission._get_common_args_from_yaml(yaml_file), package=package, **kwargs)


    def build_xml(self) -> None:
        self._build_doc_skeleton()
        self._build_sra_doc()
        self._build_biosample_doc()


if __name__ == "__main__":
    x = SRASubmission(
        role = "owner",
        role_type = "consortium",
        name = "CDC",
        email = "Pulsenet@cdc.gov",
        first = "Pulsenet",
        last = "CDC",
        bioproject = "PRJNA357722",
        spuid="spuid",
        spuid_namespace="namespace",
        comment = "No comment",
        file1= "Read1.fastq.gz",
        file2 = "Read2.fastq.gz",
        instrument_model = "Illumina MiSeq",
        library_strategy = "WGS",
        library_source = "GENOMIC",
        library_selection = "RANDOM",
        library_layout = "PAIRED",
        library_construction_protocol = "Illumina DNA Prep",
        library_name = "Not Provided",
        sra_namespace = "GenomeTrakr_SRA",
        sra_samplename = "test_SRA",
        biosample_namespace = "GenomeTrakr_BS",
        biosample_samplename = "test_BS"
    )
    print(x.to_string(True))
