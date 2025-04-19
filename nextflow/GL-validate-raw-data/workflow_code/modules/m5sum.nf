process MD5SUM {
    tag "Sample: ${ sample }"

    // publishDir "${ params.input_dir }/${ params.GLDS_ID }/md5sum",
    //     mode: params.publish_dir_mode
    
    input:
        tuple val(sample), path(files)
    
    output:
        tuple val(sample), path("*.md5"), emit: checksum

    when:
    task.ext.when == null || task.ext.when

    script:
        """
        find -L * -maxdepth 0 -type f \\
            ! -name '*.md5' \\
            -exec sh -c 'md5sum ${args} "\$1" > "\$1.md5"' _ "{}" \\;

        """
}