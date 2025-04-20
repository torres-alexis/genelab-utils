// main.nf
nextflow.enable.dsl=2

def assay_suffixes = [
    "AmpSeq": "_GLAmpSeq",
    "bulkRNAseq": "_GLbulkRNAseq",
    "metabolomics": "_GLmetabolomics",
    "metagenomics": "_GLmetagenomics",
    "metatranscriptomics": "_GLmetatranscriptomics",
    "MethylSeq": "_GLMethylSeq",
    "microarray": "_GLmicroarray",
    "nanoporeRNAseq": "_GLnanoporeRNAseq",
    "proteomics": "_GLproteomics",
    "scATACseq": "_GLscATACseq",
    "scRNAseq": "_GLscRNAseq",
    "smallRNAseq": "_GLsmallRNAseq",
    "snATACseq": "_GLsnATACseq",
    "snRNAseq": "_GLsnRNAseq",
    "ST": "_GLSpatialTranscriptomics",
    "targetNanoporeDNASeq": "_GLTargetNanoporeDNAseq",
    "targetSeq": "_GLtargetSeq",
    "targetRNAseq": "_GLtargetRNAseq",
    "WGS": "_GLwgs"
]

def colorCodes = [
    c_line: "─" * 70,
    c_bright_green: "\u001b[32;1m",
    c_blue: "\u001b[36;1m",
    c_yellow: "\u001b[33;1m",
    c_white: "\u001b[37;1m",
    c_reset: "\u001b[0m"
]


println """
${colorCodes.c_bright_green}${colorCodes.c_line}
${colorCodes.c_blue}${workflow.manifest.name}${colorCodes.c_reset}
Workflow Version: ${workflow.manifest.version}${colorCodes.c_reset}
${colorCodes.c_bright_green}${colorCodes.c_line}${colorCodes.c_reset}

Inputs:${colorCodes.c_reset}
  GLDS ID:          ${colorCodes.c_yellow}${params.accession}${colorCodes.c_reset}
  Assay:            ${colorCodes.c_yellow}${params.assay}${colorCodes.c_reset}
  MD5 File:         ${colorCodes.c_yellow}${params.md5_file}${colorCodes.c_reset}
  HRremoved Suffix: ${colorCodes.c_yellow}${params.hrr}${colorCodes.c_reset}
  Input Dir:        ${colorCodes.c_yellow}${params.input_dir}${colorCodes.c_reset}

Output will be written to:${colorCodes.c_reset} ${colorCodes.c_yellow}${params.input_dir}${params.accession}${colorCodes.c_reset}

${colorCodes.c_bright_green}${colorCodes.c_line}${colorCodes.c_reset}
""".stripIndent()

// Command for: 'nextflow run main.nf --version'
if (params.version) {
    println """${workflow.manifest.name}
Workflow Version: ${workflow.manifest.version}"""
    exit 0
}


include { GL_VALIDATE_RAW_DATA } from './workflows/gl-validate-raw-data.nf'

input_dir = params.input_dir ? Channel.fromPath(params.input_dir, checkIfExists: true) : null

ch_accession = params.accession ? Channel.value(params.accession) : null
assay = params.assay ? Channel.value(params.assay) : null
files_per_sample = params.files_per_sample ? Channel.value(params.files_per_sample) : null


// Lookup the suffix
assay_suffix = params.assay ? assay_suffixes[params.assay] : null



// To do

md5_file = params.md5_file ? Channel.fromPath(params.md5_file) : null

// Main workflows
workflow {
    GL_VALIDATE_RAW_DATA(
        input_dir,
        assay_suffix
    )
}
