process MULTIQC {
    // tag("Dataset-wide")
    publishDir "${ params.input_dir }/${ params.accession }/MultiQC_Reports",
        mode: params.publish_dir_mode,
        pattern: "{*.html,*.zip}"

    input:
    val(assay_suffix)
    path("mqc_in/*") // any number of multiqc compatible files
    path(multiqc_config)
    val(mqc_label)
    

    output:
    path("${ mqc_label }_multiqc${ assay_suffix }_data.zip"), emit: zipped_data
    path("${ mqc_label }_multiqc${ assay_suffix }.html"), emit: html
    path("${params.accession}-${ mqc_label }-multiqc.log"), emit: log
    
    script:
    def config_arg = multiqc_config.name != "NO_FILE" ? "--config ${ multiqc_config }" : ""
    def log_file = "${params.accession}-${ mqc_label }-multiqc.log"
    """
    multiqc \\
        --force \\
        --interactive \\
        -o . \\
        -n ${ mqc_label }_multiqc${ assay_suffix } \\
        ${ config_arg } \\
        . >> ${log_file} 2>&1
    
    # Clean paths and create zip
    clean_multiqc_paths.py ${ mqc_label }_multiqc${ assay_suffix }_data .

    """
}
