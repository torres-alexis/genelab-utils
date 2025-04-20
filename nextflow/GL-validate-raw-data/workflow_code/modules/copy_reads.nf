process COPY_READS {
    tag "${sample}"

    publishDir "${ params.input_dir }/${ params.accession }",
        mode: params.publish_dir_mode

    input:
        tuple val(sample), path(reads)

    output:
        tuple val(sample), path("Fastq/*.gz"), emit: raw_reads

    script:
        def suffix = params.hrr ? "_HRremoved_raw.fastq.gz" : "_raw.fastq.gz"
        def cmds = []
        reads.eachWithIndex { f, i ->
            cmds << "cp ${f} Fastq/${sample}_R${i+1}${suffix}"
        }
        """
        mkdir -p Fastq
        ${cmds.join('\n')}
        """
}