# GL-validate-raw-data Nextflow Workflow

## Workflow overview

1. Create sample sheet from input directory
2. Copy/rename raw reads to standard format
3. Run FastQC on all reads
4. Run MultiQC to aggregate QC reports
5. Generate md5sums for all files
6. Check gzip integrity
7. Check fastq format
8. Concatenate logs
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
nextflow run /home/alexis/git/genelab-utils/nextflow/GL-validate-raw-data/workflow_code/main.nf \
  -profile conda,slurm \
  --input_dir GLDS-423-raw-reads/ \
  --accession GLDS-423 \
  --assay bulkRNAseq \
  --reference_md5_file GLDS-#-raw-fastq-md5sum.txt
```

> Use `-profile conda,local` for local runs or `-profile conda,slurm` for SLURM runs.


**Parameter Definitions:**

- `-profile`: Nextflow profiles to load, used to set up execution environment (see above)
- `--input_dir`: Directory with raw data fastq.gz files
- `--accession`: GLDS ID (e.g. GLDS-423, GLDS-PE-test)
- `--assay`: Assay type (e.g. AmpSeq, bulkRNAseq, etc, see [main.nf](./workflow_code/main.nf))
- `--reference_md5_file`: (Optional) Reference md5 file for md5sum validation

Outputs and logs will be written to `${input_dir}/${accession}`.

## Output

- All results, logs, and summary tables are written to `${input_dir}/${accession}/`
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
