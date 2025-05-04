# GL-validate-raw-data Nextflow Workflow

## Workflow overview

1. Create sample sheet from input directory
2. Copy/rename raw reads to standard format
3. Run FastQC on all reads
4. Run MultiQC to aggregate QC reports
5. Generate md5sums for all files
6. Check gzip integrity
7. Check fastq format
8. Concatenate md5sums
9. Record software versions
10. (Optional) Validate computed md5sums against a provided reference md5 file.
10. Generate summary table with all results


## Requirements

- Nextflow
- Conda (or Docker/Singularity if you adapt the profile)
- Install the conda environment:
  ```
  conda env create -f workflow_code/env/environment.yml
  conda activate genelab-validate-raw-2025-04-17
  ```
  
- Make sure your Nextflow config points to the installed conda environment. See [workflow_code/conf/by_docker_image.config](workflow_code/conf/by_docker_image.config) to update the conda environment reference.

## Usage Example

```bash
nextflow run /path/to/genelab-utils/nextflow/GL-validate-raw-data/workflow_code/main.nf \
  -profile conda,slurm \
  --input_dir GLDS-423-raw-reads/ \
  --accession GLDS-423 \
  --assay bulkRNAseq \
  --files_per_sample 2 \
  --reference_md5_file GLDS-#-raw-fastq-md5sum.txt
```

> Use `-profile conda,local` for local runs or `-profile conda,slurm` for SLURM runs.


**Parameter Definitions:**

- `-profile`: Nextflow profiles to load, used to set up execution environment (see above)
- `--input_dir`: Path - Directory with raw data fastq.gz files
- `--accession`: String - GLDS ID (e.g. GLDS-423, GLDS-PE-test)
- `--assay`: String - Assay type. Must be one of:
  AmpSeq, bulkRNAseq, metabolomics, metagenomics, metatranscriptomics, MethylSeq, microarray, nanoporeRNAseq, proteomics, scATACseq, scRNAseq, smallRNAseq, snATACseq, snRNAseq, ST, targetNanoporeDNASeq, targetSeq, targetRNAseq, WGS
  (see [main.nf](./workflow_code/main.nf) for details)
- `--files_per_sample`: Integer - Number of read files expected per sample. Should be 1-4. Will break workflow on sample sheet generation process 'CREATE_SAMPLE_SHEET' if there is a mismatch. (Default: 0 / breaks workflow)
- `--reference_md5_file`: Path - (Optional) Reference md5 file for md5sum validation
- `--atacseq`: Boolean - Set if the data are ATACseq. Requires 3 or 4 files per sample (`--files_per_sample 3` or `4`)
- `--single_cell`: Boolean - Set if the data are single-cell. Requires 3 or 4 files per sample (`--files_per_sample 3` or `4`)

## Paired Read File Checking Logic

The workflow automatically checks paired read files for format consistency. The logic is:

- **Default (Paired-End, files_per_sample=2):** Paired check is performed between R1 and R2 for each sample.
- **ATACseq (`--atacseq true`):**
  - If `--files_per_sample 3` or `4`: Paired check is performed between R1 and R3 for each sample (R2 and R4 are not paired-checked; R2 is typically barcodes, R4 is ignored for pairing).
  - Any other value for `--files_per_sample` will cause the workflow to error.
- **Single-cell (`--single_cell true`):**
  - If `--files_per_sample 3`: Paired check is performed between R1 and R3 for each sample.
  - If `--files_per_sample 4`: No paired check is performed (all reads are checked individually).

The summary table output will include a `paired_fastq_format_check` column reflecting the result of the relevant paired check for each sample, or will be empty if not applicable.

Outputs will be written to `${input_dir}/${accession}`. 

## Output

- All results are written to `${input_dir}/${accession}/`
- Key output files:
  - **GLDS-#-raw-validation-summary.tsv**: Main summary table with all QC and md5 results
  - **GLDS-#-raw-fastq-md5sum_[assay suffix].txt**: md5sums for all processed files
  - **GLDS-#-raw_multiqc_[assay suffix]_data.zip**: MultiQC data archive
  - **GLDS-#-raw-validation-tool-versions.txt**: Software versions used

Typical output directory structure:

```
GLDS-#/
  Fastq/
  FastQC_Reports/
  Fastq_Info/
  Gzip_Checks/
  MultiQC_Reports/
    raw_multiqc_[assay suffix]_data.zip
    raw_multiqc_[assay suffix].html
  GLDS-#-raw-fastq-md5sum.txt
  GLDS-#-raw-validation-summary.tsv
  GLDS-#-raw-validation-tool-versions.txt
  GLDS-#-raw-fastqc-multiqc-log.txt
  sample_sheet.tsv
```
