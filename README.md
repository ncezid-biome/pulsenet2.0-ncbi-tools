# PN2.0_NCBI_submission_pipeline

This repo includes a python package ([pn_ncbi_pkg](src/pn_ncbi_pkg/)) that provides methods to perform the following actions related to submission to NCBI BioSample and SRA databases:

1. Process multiline submission metadata CSV
2. Validate sample metadata for submissions to NCBI
3. Create "submission.xml" files for submission to NCBI
4. Upload data to NCBI FTP/SFTP server
5. Check submission status on NCBI FTP/SFTP server by downloading and parsing the "report.xml" file created by NCBI during submission processing

Included in the package is a command line interface to use the components of the pn_ncbi_pkg package for the key steps in NCBI database submissions and accession retrieval. Additionally, a nextflow pipeline script ([main.nf](main.nf)) is included which wraps the command line scripts to perform end-to-end sample metadata validation and submission workflows for initial submission or existing submission edits, and an accession retrieval workflow.

Description of the design of the components of this repo is provided in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## Nextflow pipeline

The Nextflow pipeline wraps the command line interface of the [pn_ncbi_pkg](src/pn_ncbi_pkg/) package. The following parameters are required for each of the three workflows and can be used to control the behavior of the pipeline:

### New submission workflow (`--workflow submit_new`)

**Example command:**

```shell
nextflow run main.nf \
    -c <nf.config> \
    --workflow submit_new \
    --metadata_csv </path/to/mapping.csv> \
    --submission_db <biosample | sra | both> \
    --submission_type <Test | Production> \
    --publish_dir </path/to/publish_dir>
```

**Parameter explanation:**

| Parameter       | Function [acceptable values]                                                                                 |
|-----------------|--------------------------------------------------------------------------------------------------------------|
| metadata_csv    | Path to a csv file including required sample data                                                            |
| submission_type | To which database should the sample be submitted? ["Test", "Production"]                                     |
| meta_package    | Which BioSample metadata package should be used for validataion? ["OneHealthEnteric.1.0", "Pathogen.cl.1.0"] |
| submission_yaml | Path to yaml with NCBI FTP/SFTP address and credentials                                                      |
| submission_db   | Which databases should the submission.xml be formatted for? ["biosample", "sra", "both"]                     |
| protocol        | Should the submission use FTP or SFTP? ["ftp", "sftp"]                                                       |

For `submit_new` workflow runs the `metadata_csv` file must include the fields described in the [Metadata fields section](#metadata-fields) below.

### Edit submission workflow ('--workflow biosample_edit`)

**Example command:**

```shell
nextflow run main.nf \
    -c <nf.config> \
    --workflow biosample_edit \
    --edit_csv </path/to/edit.csv> \
    --submission_type <Test | Production> \
    --publish_dir </path/to/publish_dir>
```

**Parameter explanation:**

| Parameter       | Function [acceptable values]                                                                                 |
|-----------------|--------------------------------------------------------------------------------------------------------------|
| edit_csv        | Path to a csv file including required sample data                                                            |
| submission_type | To which database should the sample be submitted? ["Test", "Production"]                                     |
| meta_package    | Which BioSample metadata package should be used for validataion? ["OneHealthEnteric.1.0", "Pathogen.cl.1.0"] |
| submission_yaml | Path to yaml with NCBI FTP/SFTP address and credentials                                                      |
| protocol        | Should the submission use FTP or SFTP? ["ftp", "sftp"]                                                       |

For `biosample_edit` workflow runs, the metadata fields provided will overwrite existing data in the target sample entry in the BioSample database. See the [Metadata fields section](#metadata-fields) below for required and forbidden field information.

### Accession retrieval workflow

**Example command:**

```shell
nextflow run main.nf \
    -c <nf.config> \
    --workflow get_accessions \
    --accessions_csv </path/to/accessions_csv.csv> \
    --submission_type <Test | Production> \
    --publish_dir </path/to/publish_dir>
```

**Parameter explanation:**

| Parameter       | Function [acceptable values]                                                                                |
|-----------------|-------------------------------------------------------------------------------------------------------------|
| accessions_csv  | Path to a csv file including required sample data                                                           |
| submission_type | To which database was the sample submitted? ["Test", "Production"]                                          |
| submission_yaml | Path to yaml with NCBI FTP/SFTP address and credentials                                                     |
| protocol        | Should the submission use FTP or SFTP? ["ftp", "sftp"]                                                      |
| max_retries     | If submission processing is not yet complete, how many times should the pipeline re-check?                  |
| wait_time       | How long should the pipeline wait between checking if submission processing is complete?                    |

Unlike for the submission and edit workflows, the `accessions_csv` csv for a `get_accessions` workflow does not require any metadata information. Instead, it requires two columns: "sample" and "submission_dir". The "sample" column controls the publish directory to which results will be written. The "submission_dir" column determines which directory will be checked to retrieve the report.xml generated by NCBI during sample processing.


### Pipeline outputs

The pipeline produces a single file in whatever directory is specified as the `--publish_dir`. Specifically, within the publish directory, a subdirectory will be created with whatever was the sample name specified in the metadata/accession CSV and within that subdirectory a file called "PipelineProcessOutputs.json" will be written (PPO for short). The PPO file includes information about the submission including the location of the submission and any results or errors from the submission attempt.

The contents of the PPO file will look something like this:

```json
{
    "metadata": {
        "SRR_ID": <accession or null>,
        "NCBI_ACCESSION": <accession or null>,
        "Submission": <submission>,
        "Submission_dir": <submission_dir>
    },
    "qc": {
        "result": <"PASS" if no issues else "FAIL">,
        "issues": [
            <issue1>,
            <issue2>,
            ...
        ]
    },
    "status": <"Processing" or "Completed">
}
```

## Python library (`pn_ncbi_pkg`)

### Installation

This package requires Python 3.11 or newer.

Install the package from the main repository directory using the Python environment of your choice:

```shell
python -m pip install .
```

This installs the `pn-ncbi` command line tool. To confirm the installation:

```shell
pn-ncbi --help
```

### command line interface

The [pn_ncbi_pkg](src/pn_ncbi_pkg/) package includes a command line interface under the `pn-ncbi` command

| Subcommand             | Purpose                                                                                 |
|------------------------|-----------------------------------------------------------------------------------------|
| prepare-csv            | extract sample row from csv, copy reads out of input dir, change to .fastq.gz if needed |
| make-submission-xml    | Create submission.xml for new SRA/BioSample submissions                                 |
| make-bs-edit-xml       | Create submission.xml for BioSample metadata edit                                       |
| submit                 | Submit files for SRA/BioSample submissions                                              |
| get-submission-dirname | Get the directory name to use for submission to SRA/BioSample                           |
| get-accessions         | Retrieve report.xml from NCBI FTP and try to extract accessions                         |

See individual sub-command help messages for specific usage.

## Metadata fields

### Mandatory fields

NCBI specifies the [fields required for BioSample submissions](https://www.ncbi.nlm.nih.gov/biosample/docs/packages/). In addition to those fields, some fields are required for data processing purposes. Some of the fields specified for a BioSample metadata package can be provided as "missing". A description of which fields are required by the PN2.0 NCBI submission pipeline is provided in the following sections.

All submissions require the following fields.

N.B.,

* Some fields include aliases which provide backwards compatibility with previous PulseNet submission pipeline metadata. When aliases are allowed, those are specified in the "Alias" column
* some fields are only required for certain BioSample metadata packages. BioSample packages that require a field are indicated in the "Relevant BioSample metadata package" column.

| Field             | Alias                          | Description                                           | Target database | Relevant BioSample metadata package |
|-------------------|--------------------------------|-------------------------------------------------------|-----------------|-------------------------------------|
| sample            |                                | Determines submission dir and Nextflow PublishDir     | Both            | None                                |
| file1             |                                | First read file path                                  | SRA             | None                                |
| file2             |                                | Second read file path                                 | SRA             | None                                |
| spuid             | ncbi-spuid                     | Identifier to be used for this sample in the database | Both            | All                                 |
| bioproject        | ncbi-bioproject                | Bioproject ID under which submission should be made   | Both            | All                                 |
| source_type       |                                | human, animal, food, environmental, other             | BioSample       | OneHealthEnteric.1.0                |
| country           |                                | redundant with geo_loc_name                           | BioSample       | All                                 |
| geo_loc_name      |                                | redndant with country                                 | BioSample       | All                                 |
| instrument_model  | illumina_sequencing_instrument | Sequencing machine used                               | SRA             | None                                |
| library_source    | illumina_library_source        | Source data type (e.g., genomic)                      | SRA             | None                                |
| library_selection | illumina_library_selection     | Source DNA selection method (e.g., random, PCR, etc)  | SRA             | None                                |
| library_layout    | illumina_library_layout        | single or paired                                      | SRA             | None                                |

### Optional fields for Biosample submissions

In addition, fields can be specified which otherwise use default values. Below, mandatory fields that have default values are specified for BioSample submissions. The inclusion of these fields in the metadata CSV is optional - values are only needed if you wish to not use the default value.

Some fields are described in the corresponding BioSample metadata package documentation linked above. In those cases a description is not provided here.

| Field               | Alias                | Description                                        | Default value | Relevant BioSample metadata package |
|---------------------|----------------------|----------------------------------------------------|---------------|-------------------------------------|
| author              |                      | Submitting organization                            | CDC           | All                                 |
| spuid_namespace     | ncbi-spuid_namespace | organization name for sample name uniqueness check | EDLB-CDC      | All                                 |
| isolation_source    |                      | See metadata package description                   | missing       | All                                 |
| purpose_of_sampling |                      | See metadata package description                   | missing       | All                                 |
| collected_by        |                      | See metadata package description                   | missing       | All                                 |
| strain              |                      | See metadata package description                   | missing       | All                                 |
| host                |                      | See metadata package description                   | missing       | Pathogen.cl.1.0                     |
| host_disease        |                      | See metadata package description                   | missing       | Pathogen.cl.1.0                     |
| host_sex            |                      | See metadata package description                   | missing       | Pathogen.cl.1.0                     |
| state               |                      | See metadata package description                   | missing       | Pathogen.cl.1.0                     |
| lat_lon             |                      | See metadata package description                   | missing       | Pathogen.cl.1.0                     |
| sex                 |                      | See metadata package description                   | missing       | Pathogen.cl.1.0                     |
| age                 |                      | See metadata package description                   | missing       | Pathogen.cl.1.0                     |
| race                |                      | See metadata package description                   | missing       | Pathogen.cl.1.0                     |
| ethnicity           |                      | See metadata package description                   | missing       | Pathogen.cl.1.0                     |
| isolate             |                      | See metadata package description                   | missing       | Pathogen.cl.1.0                     |
| source_type         |                      | See metadata package description                   | missing       | Pathogen.cl.1.0                     |

### Controlled language fields for Biosample submissions

Some fields are goverened by controlled language rules where provided data must be one of the acceptable values. Check your target metadata package specification for details. `pn-ncbi make-submission-xml` will apply controlled language rules when possible.

### Custom metadata fields

In addition to the fields described above, any number of custom metadata fields can be provided in the metadata csv. Any fields which are not recognized as part of the normal BioSample or SRA submission metadata will not be validated and will be included as part of the BioSample submission as custom fields.

## Submission config

An [example config](example_submission_config.yml) file is included in this repo with fields required for use of the submission and accession retrieval workflows. Edit the file to populate the required fields with real data before attempting to use this software.