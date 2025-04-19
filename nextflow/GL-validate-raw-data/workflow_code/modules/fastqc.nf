process FASTQC {
  // memory and versioning adapted from https://github.com/nf-core/modules/blob/master/modules/nf-core/fastqc/main.nf
  // FastQC performed on reads
  tag "Sample: ${ sample }"

    publishDir "${ params.input_dir }/${ params.accession }/FastQC_Reports",
        mode: params.publish_dir_mode,
        pattern: "{*.html,*.zip}"

  input:
    tuple val(sample), path(reads)

  output:
    tuple val(sample), path("${ sample }*.html"), path("${ sample }*.zip"), emit: fastqc
    path("${sample}_fastqc.log"), emit: log
    

  script:
    // Calculate memory per thread (100MB minimum, 10000MB maximum)
    def memory_in_mb = MemoryUnit.of("${task.memory}").toUnit('MB') / task.cpus
    def fastqc_memory = memory_in_mb > 10000 ? 10000 : (memory_in_mb < 100 ? 100 : memory_in_mb)

    """
    fastqc \\
        -o . \\
        -t $task.cpus \\
        --memory $fastqc_memory \\
        $reads \\
        > ${sample}_fastqc.log 2>&1
    """
}