process SUMMARY_TABLE {

    publishDir "${ params.input_dir }/${ params.accession }/",
        mode: params.publish_dir_mode

    input:
        path(sample_sheet)
        path(gzip_checks)
        path(fastq_checks)
        path(md5_file)
        path(md5_validation_file)
        // Add more QC outputs as needed

    output:
        path("summary.tsv"), emit: summary

    script:
    """
    summary_table.py \
        --sample-sheet ${sample_sheet} \
        --md5-file ${md5_file} \
        --gzip-checks ${gzip_checks.join(' ')} \
        --fastq-checks ${fastq_checks.join(' ')} \
        --md5-validation-file ${md5_validation_file} \
        --output ${params.accession}-test-raw-validation-summary.tsv
    """
} 