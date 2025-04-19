process FASTQ_INFO {
    tag "Sample: ${ sample }"

    publishDir "${ params.input_dir }/${ params.accession }/Fastq_Info/${sample}",
        mode: params.publish_dir_mode

    input:
        tuple val(sample), path(files)

    output:
        tuple val(sample), path("*.fastq_info"), emit: fastq_info

    script:
        """
        fastq_format_check.py ${files.join(' ')}
        """
}
