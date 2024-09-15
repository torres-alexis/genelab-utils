process mapInputFiles {
    input:
    val input_dir from params.input_dir

    output:
    tuple val(sample_id), path(read_files), val(params.assay), val(params.single_ended), val(params.ATACseq), val(params.single_cell), val(params.number_of_read_files_per_sample) into sample_info_ch

    script:
    """
    python scripts/map_input_files.py \\
        --input_dir "${input_dir}" \\
        --assay "${params.assay}" \\
        [additional arguments] \\
        --output "sample_mapping.tsv"
    """
}

process renameFiles {
    tag { sample_id }

    input:
    tuple val(sample_id), path(read_files), val(*)

    output:
    tuple val(sample_id), path("renamed/${sample_id}_*"), val(*)

    script:
    """
    mkdir -p renamed
    python scripts/rename_files.py \\
        --input_files "${read_files}" \\
        --sample_id "${sample_id}" \\
        --output_dir "renamed" \\
        --assay "${assay}" \\
        [additional arguments]
    """
}

process checkGzipIntegrity {
    tag { sample_id }

    input:
    tuple val(sample_id), path(renamed_files), val(*)

    output:
    tuple val(sample_id), path("gzip_checked/${sample_id}_*"), val(*)

    script:
    """
    mkdir -p gzip_checked
    python scripts/check_gzip_integrity.py \\
        --input_files "${renamed_files}" \\
        --sample_id "${sample_id}" \\
        --output_dir "gzip_checked"
    """
}

process checkFastqFormat {
    tag { sample_id }

    input:
    tuple val(sample_id), path(gzip_files), val(*)

    output:
    tuple val(sample_id), path("format_checked/${sample_id}_*"), val(*)

    script:
    """
    mkdir -p format_checked
    python scripts/check_fastq_format.py \\
        --input_files "${gzip_files}" \\
        --sample_id "${sample_id}" \\
        --output_dir "format_checked"
    """
}

process generateMd5s {
    tag { sample_id }

    input:
    tuple val(sample_id), path(checked_files), val(*)

    output:
    tuple val(sample_id), path("md5sums/${sample_id}.md5"), val(*)

    script:
    """
    mkdir -p md5sums
    python scripts/generate_md5s.py \\
        --input_files "${checked_files}" \\
        --sample_id "${sample_id}" \\
        --output_dir "md5sums"
    """
}

process runFastqc {
    tag { sample_id }

    input:
    tuple val(sample_id), path(checked_files), val(*)

    output:
    tuple val(sample_id), path("fastqc/${sample_id}_fastqc.zip"), val(*)

    script:
    """
    mkdir -p fastqc
    fastqc -t ${task.cpus} -o fastqc ${checked_files}
    """
}

process extractReadCounts {
    tag { sample_id }

    input:
    tuple val(sample_id), path(checked_files), val(*)

    output:
    tuple val(sample_id), val(read_counts), val(*)

    script:
    """
    read_counts=$(python scripts/extract_read_counts.py \\
        --input_files "${checked_files}")
    echo -e "${sample_id}\t${read_counts}" > "read_counts/${sample_id}_counts.txt"
    """
}

process runMultiqc {
    input:
    path fastqc_zips

    output:
    path "multiqc_report.html"

    script:
    """
    multiqc fastqc/*_fastqc.zip -o .

    """
}

process generateSummaryTable {
    input:
    tuple val(sample_id), val(read_counts), val(*)

    collect:
    sample_data_ch

    output:
    path "validation_summary.tsv"

    script:
    """
    python scripts/generate_summary_table.py \\
        --sample_data "sample_data.json" \\
        --output "validation_summary.tsv"
    """
}

process packageOutputs {
    input:
    path md5sums_ch
    path multiqc_report_ch
    path summary_table_ch

    output:
    path "packaged_outputs.zip"

    script:
    """
    zip -r packaged_outputs.zip md5sums/ multiqc_report.html validation_summary.tsv
    """
}

