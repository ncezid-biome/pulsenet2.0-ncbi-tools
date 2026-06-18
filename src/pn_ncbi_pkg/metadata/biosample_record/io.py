import xml.etree.ElementTree as ET

from ..packages import BioSamplePackage
from .model import BioSampleRecord


class XMLParseError(Exception):
    pass

def required_elem(parent: ET.Element, path: str) -> ET.Element:
    elem = parent.find(path)
    if elem is None:
        raise XMLParseError(f"Missing required XML element: {path}")
    return elem


def required_text(parent: ET.Element, path: str) -> str:
    elem = required_elem(parent, path)
    if elem.text is None:
        raise XMLParseError(f"Missing text for required XML element: {path}")
    return elem.text


def required_elem_text(elem: ET.Element, *, context: str) -> str:
    if elem.text is None:
        raise XMLParseError(f"Missing text for required XML element: {context}")
    return elem.text


def required_attr(elem: ET.Element, attr: str, *, context: str) -> str:
    try:
        return elem.attrib[attr]
    except KeyError:
        raise XMLParseError(f"Missing required XML attribute {attr!r} on {context}") from None


def load_biosample_xml(xml_path: str) -> BioSampleRecord:
    try:
        xml = ET.parse(xml_path)
        root = xml.getroot()
        if root.tag != "BioSampleSet":
            raise XMLParseError("Existing sample XML cannot be processed.")

        bs_elem = required_elem(root, "BioSample")

        # BioSample accession
        biosample: str = required_attr(bs_elem, "accession", context="BioSampleSet/BioSample")

        # spuid and namespace
        ids_elem = required_elem(bs_elem, "Ids")

        spuid_ids = [
            id_elem
            for id_elem in ids_elem.findall("Id")
            if id_elem.attrib.get("db") not in {"BioSample", "SRA"}
        ]

        if len(spuid_ids) != 1:
            raise XMLParseError("Expected exactly one non-BioSample/SRA Id")

        spuid_elem = spuid_ids[0]
        spuid_ns = required_attr(spuid_elem, "db", context="Ids/Id")

        spuid = required_elem_text(spuid_elem, context="Ids/Id")

        # organism name
        organism = required_text(bs_elem, "Description/Organism/OrganismName")

        # biosample package
        package_name = required_text(bs_elem, "Package")
        try:
            bs_package = BioSamplePackage(package_name)
        except ValueError:
            raise XMLParseError(f"Unrecognized BioSample metadata package: {package_name}") from None

        # Attributes
        attrs_elem = required_elem(bs_elem, "Attributes")
        attributes: dict[str, str] = {}
        for attr in attrs_elem.iter("Attribute"):
            attr_name = required_attr(attr, "attribute_name", context="Attributes/Attribute")
            attr_value = required_elem_text(attr, context="Attributes/Attribute")
            attributes[attr_name] = attr_value

        link_elem = required_elem(bs_elem, "Links/Link")
        bioproject = required_attr(link_elem, "label", context="Links/Link")

        return BioSampleRecord(
            biosample=biosample,
            bioproject=bioproject,
            spuid=spuid,
            spuid_namespace=spuid_ns,
            package=bs_package,
            organism=organism,
            attrs = attributes
        )

    except ET.ParseError as err:
        raise XMLParseError("Existing BioSample XML seems malformed and could not be parsed") from err


def load_submission_xml(xml_path: str, biosample: str) -> BioSampleRecord:
    try:
        xml = ET.parse(xml_path)
        root = xml.getroot()
        if root.tag != "Submission":
            raise XMLParseError("Existing sample XML cannot be processed.")

        bs_root = required_elem(root, "Action/AddData/Data/XmlContent/BioSample")

        # spuid
        spuid_elem = required_elem(bs_root, "SampleId/SPUID")
        spuid_ns = required_attr(spuid_elem, "spuid_namespace", context="SampleId/SPUID")
        spuid = required_elem_text(spuid_elem, context="SampleId/SPUID")

        # organism name
        organism = required_text(bs_root, "Organism/OrganismName")

        # biosample package
        package_name = required_text(bs_root, "Package")
        try:
            bs_package = BioSamplePackage(package_name)
        except ValueError:
            raise XMLParseError(f"Unrecognized BioSample metadata package: {package_name}") from None

        bioproject = required_text(bs_root, "BioProject/PrimaryId")

        # Attributes
        attrs_elem = required_elem(bs_root, "Attributes")
        attributes: dict[str, str] = {}
        for attr in attrs_elem.iter("Attribute"):
            attr_name = required_attr(attr, "attribute_name", context="Attributes/Attribute")
            attr_value = required_elem_text(attr, context="Attributes/Attribute")
            attributes[attr_name] = attr_value

        return BioSampleRecord(
            biosample=biosample,
            bioproject=bioproject,
            spuid=spuid,
            spuid_namespace=spuid_ns,
            package=bs_package,
            organism=organism,
            attrs = attributes
        )

    except ET.ParseError as err:
        raise XMLParseError("Existing BioSample XML seems malformed and could not be parsed") from err
