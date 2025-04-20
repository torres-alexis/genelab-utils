process COLLECT_MD5 {

    publishDir "${ params.input_dir }/${ params.accession }",
        mode: params.publish_dir_mode
    
    input:
        path("*.md5")
    
    output:
        path("${params.accession}-raw-fastq-md5sum.txt")

    script:
        """
        cat *.md5 > ${params.accession}-raw-fastq-md5sum.txt
        """
}