from __future__ import annotations

import ftplib
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol

import paramiko

from pn_ncbi_pkg.report.ppo import format_ppo_data, write_ppo


class ReportConnection(Protocol):
    def change_directory(self, directory: str) -> None:
        ...

    def read_file(self, remote_path: str) -> str:
        ...

    def close_connection(self) -> None:
        ...

class TargetDB(Enum):
    SRA = "SRA"
    BioSample = "BioSample"

@dataclass
class Report:
    biosample_accession: str | None=None
    sra_accession: str | None=None
    submission: str | None=None
    submission_dir: str | None=None
    _stop: list[bool]=field(default_factory=list) # let all target DBs vote on whether there is a point in trying again later
    _qc: str | None=None
    errors: list[str]=field(default_factory=list)
    status: str="Completed"

    @property
    def qc(self):
        if len(self.errors) == 0:
            return "PASS"
        return "FAIL"


    @property
    def stop(self):
        # If everything went fine then stop
        if self.qc == "PASS":
            return True
        # otherwise consider votes based on errors
        # true if all target DBs voted to stop, otherwise false
        return all(self._stop)

    def vote_stop(self):
        self._stop.append(True)

    def vote_retry(self):
        self._stop.append(False)

    @classmethod
    def from_report_xml(cls, report_path: str, submission_dir: str|None=None):
        rep = cls(submission_dir=submission_dir)
        try:
            xml = ET.parse(report_path)
            root = xml.getroot()
            rep._from_xml_root(root)
        except ET.ParseError:
            rep.errors.append("report.xml could not be parsed.")
            rep.vote_retry()
        return rep

    @classmethod
    def from_xml_string(cls, xml: str, submission_dir: str|None=None):
        rep = cls(submission_dir=submission_dir)
        try:
            root = ET.fromstring(xml)
            rep._from_xml_root(root)
        except ET.ParseError:
            rep.errors.append("report.xml could not be parsed.")
            rep.vote_retry()
        return rep

    def _from_xml_root(self, root: ET.Element):
        self.submission = root.attrib.get("submission_id")
        # Check if whole submission failed
        status = root.attrib.get("status")
        if status == "failed":
            self.status = "Completed"
            self._process_fail(root)
            # stop processing if failed
            return self
        for action in root.iter("Action"):
            try:
                db = TargetDB(action.attrib["target_db"])
            except ValueError: # Doesn't match TargetDB enum
                self.status = "Completed"
                self.errors.append(f"Report contains unexpected target database: {action.attrib['target_db']}")
                continue
            except KeyError: # No target_db in action
                self.status = "Completed"
                self.errors.append("submission target DB could not be found")
                self.vote_stop()
                continue

            status = action.attrib.get('status')
            match status:
                case "processing":
                    self.status = "Processing"
                    self.errors.append("sample processing.")
                    self.vote_retry()
                case "submitted":
                    self.status = "Processing"
                    self.errors.append("sample processing.")
                    self.vote_retry()
                case "processed-error":
                    self.status = "Completed"
                    self._process_error(action, db)
                case "processed-ok":
                    self.status = "Completed"
                    self._process_ok(action, db)
                case None:
                    self.status = "Completed"
                    self.errors.append("submission status could not be found")
                    self.vote_stop()
                case _:
                    self.status = "Completed"
                    self.errors.append(f"unrecognized status encountered: {status}")
                    self.vote_stop()



    @classmethod
    def from_server(cls, connection: ReportConnection, submission_dir: str, output_dir: str="./"):
        rep = cls()
        rep.submission_dir = submission_dir
        try:
            connection.change_directory(submission_dir)
        except FileNotFoundError:
            error = f"Error: There is no submission in the submission directory '{submission_dir}' on the NCBI server."
            connection.close_connection()
            rep.errors.append(error)
            rep.vote_stop()
            return rep
        except (*ftplib.all_errors, paramiko.AuthenticationException, paramiko.SSHException, OSError, TimeoutError) as error:
            # retry no matter the exception
            connection.close_connection()
            rep.errors.append(str(error))
            rep.vote_retry()
            return rep

        try:
            report_xml = connection.read_file("report.xml")
        except (FileNotFoundError, ConnectionError) as error:
            rep.errors.append(str(error))
            rep.vote_retry()
            return rep

        return cls.from_xml_string(xml=report_xml, submission_dir=submission_dir)


    def _process_fail(self, root: ET.Element):
        message = root.find(".//Message")
        if message is not None:
            self.errors.append(message.text if message.text is not None else "")
        else:
            self.errors.append("Submission failed but no error message was found.")
        self.vote_stop()


    def _process_error(self, action: ET.Element, db: TargetDB):
        existing_sample = action.find(".//ExistingSample")
        if existing_sample is not None:
            accession = existing_sample.text
            match db:
                case TargetDB.BioSample:
                    self.biosample_accession = accession
                case TargetDB.SRA:
                    self.sra_accession = accession
            return

        # check attribute issues
        all_attrs = action.find(".//Attributes")
        if all_attrs is not None:
            for attr in all_attrs.iter("Attribute"):
                field = attr.get("attribute_name")
                status = attr.get("status")
                provided = attr.text
                self.errors.append(f"Invalid metadata provided. Problem field: {field}. Status: {status}. Provided data: {provided}")

        message = action.find(".//Message")
        if message is not None and message.text is not None:
            # Check if duplicate
            if message.text.startswith("Submission is duplicate of"):
                accession = re.search(r"SRR\d+", message.text)
                if accession is not None:
                    self.sra_accession = accession[0]
                else:
                    self.errors.append(message.text)
            else:
                self.errors.append(message.text)
        else:
            if self.errors == []:
                self.errors.append("An error occurred, but no error message could be found in the report")
        self.vote_stop()


    def _process_ok(self, action: ET.Element, db: TargetDB):
        obj = action.find(".//Object")
        if obj is not None:
            accession = obj.get("accession")
            if accession is not None:
                match db:
                    case TargetDB.BioSample:
                        self.biosample_accession = accession
                    case TargetDB.SRA:
                        self.sra_accession = accession
                return
        self.errors.append("An error occurred: the report indicates processing succeeded, but no accession is found.")
        self.vote_stop()


    def to_file(self, file_path: str):
        write_ppo(
            srr=self.sra_accession,
            samn=self.biosample_accession,
            submission=self.submission,
            submission_dir=self.submission_dir,
            issues=self.errors,
            status=self.status,
            file_path=file_path
        )

    def to_dict(self):
        return format_ppo_data(
            srr=self.sra_accession,
            samn=self.biosample_accession,
            submission=self.submission,
            submission_dir=self.submission_dir,
            issues=self.errors,
            status=self.status
        )


