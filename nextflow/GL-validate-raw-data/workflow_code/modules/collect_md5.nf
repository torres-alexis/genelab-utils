process COLLECT_MD5 {

    publishDir "${ params.input_dir }/${ params.accession }",
        mode: params.publish_dir_mode,
        saveAs: { "${params.accession}-raw-fastq-md5sum.txt" }
    
    input:
        path("*.md5")
    
    output:
        path("raw-fastq-md5sum.txt"), emit: md5_file
    script:
        """
        cat *.md5 > raw-fastq-md5sum.txt
        """
}