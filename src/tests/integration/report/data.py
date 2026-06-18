BS_DUP_REPORT = """
<?xml version='1.0' encoding='utf-8'?>
<SubmissionStatus status="processed-error" submission_id="SUB15699433" last_update="2025-10-10T17:44:29.242265">
<Action status="processed-error" action_id="SUB15699433-pnusae216567" target_db="BioSample" notify_submitter="true">
    <Response status="processed-error">
    <Message error_code="7" severity="error-stop" error_source="data">These samples have the same Sample Names and different attributes. If they are different samples, please provide a unique Sample Name for each. If one is intended to be an update of the other, please stop this submission and contact biosamplehelp@ncbi.nlm.nih.gov.</Message>
    <Object target_db="BioSample" object_id="" spuid="PNUSAE216567" spuid_namespace="EDLB-CDC">
        <Details>
        <ExistingSample>SAMN52211363</ExistingSample>
        </Details>
    </Object>
    </Response>
</Action>
<Tracking>
    <SubmissionLocation>/netmnt/ftp-trace/centers/pulsenet/submit/Production/M25F002217_2</SubmissionLocation>
</Tracking>
</SubmissionStatus>
""".lstrip()
SRA_DUP_REPORT = """
<?xml version='1.0' encoding='utf-8'?>
<SubmissionStatus status="processed-error" submission_id="SUB15699433" last_update="2025-10-10T17:44:29.242265">
<Action action_id="SUB15699433-pnusae216567_sra" target_db="SRA" status="processed-error" notify_submitter="true">
    <Response status="processed-error" error_source="system">
    <Message severity="error-stop">Submission is duplicate of SUB15682058. Same identifier(s). Identical files. Original submission RUNs accessions: SRR35706443</Message>
    </Response>
</Action>
<Tracking>
    <SubmissionLocation>/netmnt/ftp-trace/centers/pulsenet/submit/Production/M25F002217_2</SubmissionLocation>
</Tracking>
</SubmissionStatus>
""".lstrip()
BS_SRA_DUP_REPORT = """
<?xml version='1.0' encoding='utf-8'?>
<SubmissionStatus status="processed-error" submission_id="SUB15699433" last_update="2025-10-10T17:44:29.242265">
<Action status="processed-error" action_id="SUB15699433-pnusae216567" target_db="BioSample" notify_submitter="true">
    <Response status="processed-error">
    <Message error_code="7" severity="error-stop" error_source="data">These samples have the same Sample Names and different attributes. If they are different samples, please provide a unique Sample Name for each. If one is intended to be an update of the other, please stop this submission and contact biosamplehelp@ncbi.nlm.nih.gov.</Message>
    <Object target_db="BioSample" object_id="" spuid="PNUSAE216567" spuid_namespace="EDLB-CDC">
        <Details>
        <ExistingSample>SAMN52211363</ExistingSample>
        </Details>
    </Object>
    </Response>
</Action>
<Action action_id="SUB15699433-pnusae216567_sra" target_db="SRA" status="processed-error" notify_submitter="true">
    <Response status="processed-error" error_source="system">
    <Message severity="error-stop">Submission is duplicate of SUB15682058. Same identifier(s). Identical files. Original submission RUNs accessions: SRR35706443</Message>
    </Response>
</Action>
<Tracking>
    <SubmissionLocation>/netmnt/ftp-trace/centers/pulsenet/submit/Production/M25F002217_2</SubmissionLocation>
</Tracking>
</SubmissionStatus>
""".lstrip()


EXPECTED_PPO = """{
    "metadata": {
        "SRR_ID": "SRR35706443",
        "NCBI_ACCESSION": null,
        "Submission": "SUB15699433",
        "Submission_dir": null
    },
    "qc": {
        "result": "PASS",
        "issues": []
    },
    "status": "Completed"
}"""
