include { CREATE_SAMPLE_SHEET } from '../modules/create_sample_sheet.nf'
include { COPY_READS } from '../modules/copy_reads.nf'
include { FASTQC } from '../modules/fastqc.nf'
include { MULTIQC } from '../modules/multiqc.nf'
include { MD5SUM } from '../modules/m5sum.nf'
include { COLLECT_MD5 } from '../modules/collect_md5.nf'
include { GZIP_CHECK } from '../modules/gzip_check.nf'
include { FASTQ_INFO } from '../modules/fastq_info.nf'
include { SOFTWARE_VERSIONS } from '../modules/software_versions.nf'
include { CONCAT_LOGS } from '../modules/concat_logs.nf'

def parseSampleSheet(sample_sheet_ch) {
    sample_sheet_ch
        .splitCsv(header: true, sep: '\t')
        .map { row ->
            def reads = []
            row.keySet().findAll { it.startsWith('read') && it.endsWith('_path') }
                .sort()
                .each { col ->
                    def val = row[col]
                    if (val && val.trim()) reads << val
                }
            tuple(row['Sample Name'], reads)
        }
}


workflow GL_VALIDATE_RAW_DATA {
    take:
        input_dir
        assay_suffix
        

    main:
        // Read in the input directory and create a sample sheet
        //      Row: Sample, read1_path, [read2_path, read3_path, read4_path]
        sample_sheet = CREATE_SAMPLE_SHEET(input_dir)
        parsed_samples = parseSampleSheet(sample_sheet)


        parsed_samples | COPY_READS
        renamed_reads = COPY_READS.out.raw_reads

        renamed_reads | FASTQC

        // FastQC
        FASTQC.out.fastqc | map { it -> [ it[1], it[2]] } // Collect the raw read fastqc zip files
            | flatten
            | collect // Collect all zip files into a single list
            | set { raw_fastqc_zip } // Create a channel with all zip files
        
        // MultiQC
        ch_multiqc_config = params.multiqc_config ? Channel.fromPath( params.multiqc_config ) : Channel.fromPath("NO_FILE")
        MULTIQC(assay_suffix, raw_fastqc_zip, ch_multiqc_config, "raw")
        
        // Run samplewise md5sum then collect all md5s into a single file
        MD5SUM(renamed_reads)
        MD5SUM.out.checksum.map { meta, md5file -> md5file }
            .collect()
            .map { files -> files.sort() }
            | COLLECT_MD5

        // Gzip integrity check with `gzip -t` 
        GZIP_CHECK(renamed_reads)

        // Check fastq format with fastq_info
        FASTQ_INFO(renamed_reads)


        // Concatenate FastQC and MultiQC logs
        CONCAT_LOGS(
            FASTQC.out.log.map { meta, logfile -> logfile }
            | collect
            | map { it.sort() },
            MULTIQC.out.log
        )


        // Create software versions file
        SOFTWARE_VERSIONS()



    emit:
        parsed_samples
}
