from enum import Enum


class SubmissionDB(Enum):
    SRA = "sra"
    BIOSAMPLE = "biosample"
    BOTH = "both"
