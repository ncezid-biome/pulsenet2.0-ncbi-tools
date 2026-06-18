from pn_ncbi_pkg.metadata import prepare_metadata_for_submission
from pn_ncbi_pkg.result import Err, Ok
from pn_ncbi_pkg.submission import SRASubmission, SubmissionDB
from tests.helpers import error_text, valid_ill_sra_metadata


def test_valid_biosample_accession_is_rendered_as_primary_id():
    metadata = valid_ill_sra_metadata(biosample="SAMN12345678")
    print(metadata)
    result = prepare_metadata_for_submission(metadata, SubmissionDB.SRA)

    assert isinstance(result, Ok)

    submission = SRASubmission(
        role="owner",
        role_type="consortium",
        name="CDC",
        email="test@example.gov",
        first="PulseNet",
        last="CDC",
        **result.unwrap(),
        sra_only=True,
    )

    primary_id = submission.xml.find(".//AttributeRefId[@name='BioSample']/RefId/PrimaryId")

    assert primary_id is not None
    assert primary_id.get("db") == "BioSample"
    assert primary_id.text == "SAMN12345678"


def test_invalid_biosample_accession_fails_validation():
    metadata = valid_ill_sra_metadata(biosample="not-a-samn")

    result = prepare_metadata_for_submission(metadata, SubmissionDB.SRA)

    assert isinstance(result, Err)
    assert "biosample" in error_text(result).lower()
