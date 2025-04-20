process CONCAT_LOGS {
    input:
        path(fastqc_logs)
        path(multiqc_log)

    publishDir "${ params.input_dir }/${ params.accession }",
        mode: params.publish_dir_mode

    output:
        path("${params.accession}-raw-fastqc-multiqc-log.txt")

    script:
        def log_file = "${params.accession}-raw-fastqc-multiqc-log.txt"
        """
        cat ${fastqc_logs.sort().join(' ')} ${multiqc_log} > ${log_file}
        """
}
