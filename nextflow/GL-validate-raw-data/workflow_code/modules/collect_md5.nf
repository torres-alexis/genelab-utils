process COLLECT_MD5 {
    tag "Collecting md5sums"

    publishDir "${ params.input_dir }/${ params.accession }",
        mode: params.publish_dir_mode
    
    input:
        path("*.md5")
    
    output:
        path("md5sum.txt")

    script:
        """
        cat *.md5 > md5sum.txt
        """
}