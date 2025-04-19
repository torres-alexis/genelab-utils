process SOFTWARE_VERSIONS {
    publishDir "${ params.input_dir }/${ params.accession }/",
        mode: params.publish_dir_mode

    input:
    
    output:
        path "${ params.accession }-raw-validation-tool-versions.txt", emit: software_versions

    script:
    """
    pyver=\$(python3 --version | awk '{print \$2}')
    echo "python=\$pyver" > ${params.accession}-raw-validation-tool-versions.txt

    pandasver=\$(python3 -c 'import pandas; print(pandas.__version__)')
    echo "pandas=\$pandasver" >> ${params.accession}-raw-validation-tool-versions.txt

    fastqcver=\$(fastqc --version | head -n1 | awk '{print \$2}' | sed 's/^v//')
    echo "fastqc=\$fastqcver" >> ${params.accession}-raw-validation-tool-versions.txt

    multiqcver=\$(multiqc --version | head -n1 | sed 's/.*, version //')
    echo "multiqc=\$multiqcver" >> ${params.accession}-raw-validation-tool-versions.txt

    fastqutilsver=\$(fastq_info -h 2>&1 | grep fastq_utils | awk '{print \$2}')
    echo "fastq_utils=\$fastqutilsver" >> ${params.accession}-raw-validation-tool-versions.txt

    coreutilsver=\$(ls --version | head -n1 | awk '{print \$NF}')
    echo "coreutils=\$coreutilsver" >> ${params.accession}-raw-validation-tool-versions.txt

    gzipver=\$(gzip --version | head -n1 | awk '{print \$2}')
    echo "gzip=\$gzipver" >> ${params.accession}-raw-validation-tool-versions.txt

    zipver=\$(zip -v | grep -E '^This is Zip' | awk '{print \$4}')
    echo "zip=\$zipver" >> ${params.accession}-raw-validation-tool-versions.txt

    nfver=\$(nextflow -version | grep -Eo 'version [0-9.]+' | awk '{print \$2}')
    echo "nextflow=\$nfver" >> ${params.accession}-raw-validation-tool-versions.txt

    echo "" >> ${params.accession}-raw-validation-tool-versions.txt
    echo "Protocol text:" >> ${params.accession}-raw-validation-tool-versions.txt
    echo "" >> ${params.accession}-raw-validation-tool-versions.txt
    echo "Fastq format was checked with fastq_utils v\$fastqutilsver. Quality assessment of reads was performed with FastQC v\$fastqcver and reports were combined with MultiQC v\$multiqcver." >> ${params.accession}-raw-validation-tool-versions.txt
    """
}