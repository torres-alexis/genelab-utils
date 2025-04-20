process CREATE_SAMPLE_SHEET {
    tag("Dataset-wide")
    publishDir "${ params.input_dir }/${ params.accession }",
        mode: params.publish_dir_mode

    input:
        val input_dir

    output:
        path "sample_sheet.tsv", emit: sample_sheet

    script:
    """
    create_sample_sheet.py $input_dir
    """
}
