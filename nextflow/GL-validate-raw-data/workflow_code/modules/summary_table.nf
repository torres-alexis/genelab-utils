process SUMMARY_TABLE {

    publishDir "${ params.input_dir }/${ params.accession }",
        mode: params.publish_dir_mode

    input:
        path(sample_sheet)      // Sample sheet
        path("Fastq/*")         // Raw reads
        path(md5_file)          // collected md5 file
        path("Gzip_Checks/*")   // Gzip checks
        path("Fastq_Info/*")    // Fastq info
        path(multiqc_data_zip)  // MultiQC data zip
        path(reference_md5)     // Reference md5 if provided

    output:
        path("${params.accession}-raw-validation-summary.tsv")

    script:
        """
        ref_md5_arg=""
        if [ "\$(basename ${reference_md5})" != "PLACEHOLDER" ]; then
            ref_md5_arg="--reference_md5 ${reference_md5}"
        fi

        create_summary_table.py \
          --sample_sheet ${sample_sheet} \
          --accession ${params.accession} \
          --read_dir Fastq/ \
          --gzip_dir Gzip_Checks/ \
          --fastq_info_dir Fastq_Info/ \
          --md5 ${md5_file} \
          --multiqc_data_zip ${multiqc_data_zip} \
          \$ref_md5_arg
        """
}