#!/usr/bin/env nextflow

nextflow.enable.dsl=2


def requireParam(String name) {
    def value = params[name]
    if (value == null || value.toString().trim() == '') {
        error("Missing required parameter --${name}")
    }
    return value
}


def requireRowValue(row, String field, String context) {
    def value = row[field]
    if (value == null || value.toString().trim() == '') {
        error("${context} requires column '${field}'")
    }
    return value.toString()
}


def sampleRows(csvPath) {
    Channel
        .fromPath(csvPath, checkIfExists: true)
        .splitCsv(header: true, strip: true, quote: '"')
        .map { row ->
            def sample = requireRowValue(row, 'sample', csvPath.toString())
            tuple(sample, row)
        }
}


def filterQCFail(inQC) {
    return inQC
        .filter{it[-1] != "FAIL"}
        .map { it[0..it.size()-2] }
}


def quoteForBash(value) {
    return "'" + value.toString().replace("'", "'\"'\"'") + "'"
}


process PREPARE_CSV {
    tag "$sample"

    input:
        tuple val(sample), path(source_csv)

    output:
        tuple val(sample), path("${sample}.csv"), emit: prepared

    script:
    """
    pn-ncbi prepare-csv \
        --sample "$sample" \
        --csv "$source_csv" \
        --drop-column file_path \
        --out-csv "${sample}.csv"
    """
}


process PREPARE_EDIT_CSV {
    tag "$sample"

    input:
        tuple val(sample), path(source_csv)

    output:
        tuple val(sample), path("${sample}.csv"), emit: prepared

    script:
    """
    pn-ncbi prepare-csv \
        --sample "$sample" \
        --csv "$source_csv" \
        --drop-column file_path submission_xml \
        --out-csv "${sample}.csv"
    """
}


process PREPARE_CSV_WITH_READS {
    tag "$sample"

    input:
        tuple val(sample), path(source_csv), path(read_dir)

    output:
        tuple val(sample), path("${sample}.csv"), path("*.fastq.gz"), emit: prepared

    script:
    """
    pn-ncbi prepare-csv \
        --sample "$sample" \
        --csv "$source_csv" \
        --read-dir "$read_dir" \
        --out-csv "${sample}.csv"
    """
}


process MAKE_SUBMISSION_XML {
    tag "$sample"
    publishDir { "${params.publish_dir}/${sample}" }, mode: 'copy', overwrite: true, pattern: 'PipelineProcessOutputs.json'
    publishDir { "${params.publish_dir}/${sample}" }, mode: 'copy', overwrite: true, pattern: 'submission.xml'

    input:
        tuple val(sample), path(metadata_csv)

    output:
        tuple val(sample), path("submission.xml"), env("QC"), emit: xml
        path("PipelineProcessOutputs.json")

    script:
    """
    pn-ncbi make-submission-xml \
        --csv "$metadata_csv" \
        --metadata-package "$params.meta_package" \
        --submission-db "$params.submission_db" \
        --submission-yaml "$params.submission_yaml" \
        --out-xml submission.xml \
        --out-ppo PipelineProcessOutputs.json

    QC=\$(grep -Eo "PASS|FAIL" PipelineProcessOutputs.json)
    """
}


process FETCH_BIOSAMPLE_XML {
    tag "$sample"

    errorStrategy 'retry'
    maxRetries 3

    input:
        tuple val(sample), val(accession)

    output:
        tuple val(sample), path("existing_biosample.xml"), emit: xml

    script:
    """
    set -o pipefail

    esearch -db biosample -query "${accession}[Accession]" \\
        | efetch -format xml \\
        > existing_biosample.xml

    test -s existing_biosample.xml
    """
}


process MAKE_BIOSAMPLE_EDIT_XML {
    tag "$sample"
    stageInMode 'copy'
    publishDir { "${params.publish_dir}/${sample}" }, mode: 'copy', overwrite: true, pattern: 'PipelineProcessOutputs.json'

    input:
        tuple val(sample), path(update_csv), path(source_xml, stageAs: 'existing.xml'), val(source_arg)

    output:
        tuple val(sample), path("submission.xml"), env("QC"), emit: xml
        tuple val(sample), path("PipelineProcessOutputs.json"), emit: ppo

    script:
    """
    pn-ncbi make-bs-edit-xml \
        $source_arg existing.xml \
        --update-csv "$update_csv" \
        --metadata-package "$params.meta_package" \
        --submission-yaml "$params.submission_yaml" \
        --out-xml submission.xml \
        --out-ppo PipelineProcessOutputs.json 

    QC=\$(grep -Eo "PASS|FAIL" PipelineProcessOutputs.json)
    """
}


process SUBMIT {
    tag "$sample"
    publishDir { "${params.publish_dir}/${sample}" }, mode: 'copy', overwrite: true, pattern: 'PipelineProcessOutputs.json'

    input:
        tuple val(sample), path(files)

    output:
        tuple val(sample), env("submission_dir"), path("PipelineProcessOutputs.json"), emit: submitted

    script:
    def stagedFiles = files instanceof List ? files : [files]
    def fileArgs = stagedFiles.collect { quoteForBash(it) }.join(' ')
    """
    submission_dir=\$(pn-ncbi get-submission-dirname \
        --protocol "$params.protocol" \
        --submission-type "$params.submission_type" \
        --directory-prefix "$sample" \
        --submission-yaml "$params.submission_yaml" \
        --out-ppo get_submission_dir.PipelineProcessOutputs.json)

    if [[ -n "\$submission_dir" ]]; then
        pn-ncbi submit \
            --submission-dir "\$submission_dir" \
            --submission-type "$params.submission_type" \
            --files $fileArgs \
            --protocol "$params.protocol" \
            --submission-yaml "$params.submission_yaml" \
            --out-ppo PipelineProcessOutputs.json
    else
        cp get_submission_dir.PipelineProcessOutputs.json PipelineProcessOutputs.json
    fi
    """
}


process GET_ACCESSIONS {
    tag "$sample"
    publishDir { "${params.publish_dir}/${sample}" }, mode: 'copy', overwrite: true, pattern: 'PipelineProcessOutputs.json'
    errorStrategy { sleep(params.wait_time * 1000); task.exitStatus == 2 ? 'retry' : 'terminate' }
    maxRetries params.max_retries

    input:
        tuple val(sample), val(submission_dir)

    output:
        tuple val(sample), path("PipelineProcessOutputs.json"), emit: ppo

    script:
    def zeroExit = task.attempt > params.max_retries ? '--zero-exit' : ''
    """
    pn-ncbi get-accessions \
        --sample-name "$submission_dir" \
        --submission-type "$params.submission_type" \
        --out-ppo PipelineProcessOutputs.json \
        --protocol "$params.protocol" \
        --config-path "$params.submission_yaml" \
        $zeroExit
    """
}


workflow submit_new {
    requireParam('metadata_csv')
    requireParam('submission_yaml')

    rows = sampleRows(params.metadata_csv)

    if (params.submission_db in ['sra', 'both']) {
        rows_with_reads = rows.map { sample, row ->
            def read_dir = requireRowValue(row, 'file_path', "New SRA/combined submission for ${sample}")
            tuple(sample, file(params.metadata_csv), file(read_dir))
        }

        PREPARE_CSV_WITH_READS(rows_with_reads)
        MAKE_SUBMISSION_XML(
            PREPARE_CSV_WITH_READS.out.prepared.map { sample, csv, reads ->
                tuple(sample, csv)
            }
        )

        reads_by_sample = PREPARE_CSV_WITH_READS.out.prepared.map { sample, csv, reads ->
            tuple(sample, reads)
        }

        files_to_submit = filterQCFail(MAKE_SUBMISSION_XML.out.xml)
            .join(reads_by_sample)
            .map { sample, xml, reads ->
                def readFiles = reads instanceof List ? reads : [reads]
                tuple(sample, [xml] + readFiles)
            }
    }
    else if (params.submission_db == 'biosample') {
        PREPARE_CSV(
            rows.map { sample, row ->
                tuple(sample, file(params.metadata_csv))
            }
        )
        MAKE_SUBMISSION_XML(PREPARE_CSV.out.prepared)

        files_to_submit = filterQCFail(MAKE_SUBMISSION_XML.out.xml)
            .map { sample, xml ->
                tuple(sample, [xml])
            }
    }
    else {
        error("Unsupported --submission_db '${params.submission_db}'")
    }

    SUBMIT(files_to_submit)
}


workflow biosample_edit {
    requireParam('edit_csv')
    requireParam('submission_yaml')

    edit_rows = sampleRows(params.edit_csv)
        .collect(flat: false)
        .map { records ->
            def hasSubXml = records.collect { record ->
                def sample = record[0]
                def row = record[1]
                requireRowValue(row, 'biosample', "BioSample edit for ${sample}")
                def submissionXml = row.submission_xml?.toString()?.trim()
                submissionXml ? true : false
            }.unique()

            if (hasSubXml.size() > 1) {
                error("BioSample edit CSV must provide submission_xml for every row or for no rows")
            }
            
            tuple(hasSubXml ? hasSubXml[0] : false, records)
        }

    PREPARE_EDIT_CSV(
        edit_rows.flatMap { hasSubXml, records ->
            records.collect { record ->
                def sample = record[0]
                tuple(sample, file(params.edit_csv))
            }
        }
    )  

    original_sources = edit_rows
        .filter { hasSubXml, records -> hasSubXml }
        .flatMap { hasSubXml, records ->
            records.collect { record ->
                def sample = record[0]
                def row = record[1]
                tuple(
                    sample,
                    file(row.submission_xml.toString().trim(), checkIfExists: true),
                    '--original-submission-xml'
                )
            }
        }

    accessions = edit_rows
        .filter { hasSubXml, records -> !hasSubXml }
        .flatMap { hasSubXml, records ->
            records.collect { record ->
                def sample = record[0]
                def row = record[1]
                tuple(sample, row.biosample.toString().trim())
            }
        }

    FETCH_BIOSAMPLE_XML(accessions)

    source_xmls = original_sources.mix(
        FETCH_BIOSAMPLE_XML.out.xml.map { sample, existing_xml ->
            tuple(sample, existing_xml, '--existing-biosample-xml')
        }
    )

    edit_inputs = PREPARE_EDIT_CSV.out.prepared
        .join(source_xmls)
        .map { sample, update_csv, source_xml, source_arg ->
            tuple(sample, update_csv, source_xml, source_arg)
        }

    MAKE_BIOSAMPLE_EDIT_XML(edit_inputs)

    files_to_submit = filterQCFail(MAKE_BIOSAMPLE_EDIT_XML.out.xml)
        .map { sample, xml ->
            tuple(sample, [xml])
        }

    SUBMIT(files_to_submit)
}


workflow get_accessions {
    requireParam('accessions_csv')
    requireParam('submission_yaml')

    rows = sampleRows(params.accessions_csv)
    samples = rows.map { sample, row ->
        def submission_dir = requireRowValue(row, 'submission_dir', "Accession retrieval for ${sample}")
        tuple(sample, submission_dir)
    }

    GET_ACCESSIONS(samples)
}


workflow {
    if (params.workflow == 'submit_new') {
        submit_new()
    }
    else if (params.workflow == 'biosample_edit') {
        biosample_edit()
    }
    else if (params.workflow == 'get_accessions') {
        get_accessions()
    }
    else {
        error(
            "Unsupported --workflow '${params.workflow}'. Expected submit_new, biosample_edit, or get_accessions."
        )
    }
}
