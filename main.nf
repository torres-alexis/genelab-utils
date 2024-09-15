#!/usr/bin/env nextflow

nextflow.enable.dsl=2

include { 
    mapInputFiles;
    renameFiles;
    checkGzipIntegrity;
    checkFastqFormat;
    generateMd5s;
    runFastqc;
    extractReadCounts;
    runMultiqc;
    generateSummaryTable;
    packageOutputs;
} from './modules/validate_raw_data.nf'

workflow {

    // Step 1: Map Input Files
    sample_info_ch = mapInputFiles(params.input_dir)

    // Step 2 to 7: Per-sample Processing
    processed_samples_ch = sample_info_ch
        .ifEmpty { error "No samples found in input directory." }
        | renameFiles
        | checkGzipIntegrity
        | checkFastqFormat
        | generateMd5s
        | runFastqc
        | extractReadCounts

    // Step 8: Run MultiQC
    multiqc_report_ch = processed_samples_ch.collectFile()
        | runMultiqc

    // Step 9: Generate Summary Table
    summary_table_ch = processed_samples_ch
        | generateSummaryTable

    // Step 10: Package Outputs
    packageOutputs(
        md5sums_ch: processed_samples_ch.map { it.md5sum },
        multiqc_ch: multiqc_report_ch,
        summary_ch: summary_table_ch
    )
}