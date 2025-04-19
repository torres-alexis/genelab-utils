process GZIP_CHECK {
    tag "${sample}"

    publishDir "${ params.input_dir }/${ params.accession }/Gzip_Checks",
        mode: params.publish_dir_mode

    stageInMode "copy"

    input:
        tuple val(sample), path(files)

    output:
        tuple val(sample), path("*.gzip_check"), emit: gzip_checks

    script:
        """
        for f in *.gz; do
            if gzip -t "\$f"; then
                echo PASS > "\$f.gzip_check"
            else
                echo FAIL > "\$f.gzip_check"
            fi
        done
        """
}