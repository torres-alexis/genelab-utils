#!/usr/bin/env python

"""
Script to map input files to sample IDs for the GL-validate-raw-data pipeline.
"""

import argparse
import os
import re
import json

def parse_arguments():
    parser = argparse.ArgumentParser(description='Map input files to sample IDs.')
    parser.add_argument('--input_dir', required=True, help='Directory containing input files.')
    parser.add_argument('--assay', required=True, help='Assay type.')
    parser.add_argument('--single_ended', action='store_true', help='Use if data are single-end sequencing.')
    parser.add_argument('--ATACseq', action='store_true', help='Use if data are ATACseq.')
    parser.add_argument('--single_cell', action='store_true', help='Use if data are single-cell data.')
    parser.add_argument('--number_of_read_files_per_sample', type=int, choices=[3, 4],
                        help='Number of read files per sample (for single-cell data).')
    parser.add_argument('--output', required=True, help='Output mapping file.')
    return parser.parse_args()

def map_input_files(args):
    input_dir = args.input_dir
    file_list = os.listdir(input_dir)

    # Define regex patterns based on assay and sequencing configuration
    patterns = {
        'R1': re.compile(r'(.+)_R1_.*\.fastq\.gz$'),
        'R2': re.compile(r'(.+)_R2_.*\.fastq\.gz$'),
        'R3': re.compile(r'(.+)_R3_.*\.fastq\.gz$'),
        'R4': re.compile(r'(.+)_R4_.*\.fastq\.gz$'),
    }

    sample_mapping = {}

    for filename in file_list:
        filepath = os.path.join(input_dir, filename)
        if os.path.isfile(filepath):
            matched = False
            for read_label, pattern in patterns.items():
                match = pattern.match(filename)
                if match:
                    sample_id = match.group(1)
                    if sample_id not in sample_mapping:
                        sample_mapping[sample_id] = {}
                    sample_mapping[sample_id][read_label] = filepath
                    matched = True
                    break
            if not matched:
                print(f"File {filename} does not match expected patterns.")

    # Save mapping to output file
    with open(args.output, 'w') as out_file:
        json.dump(sample_mapping, out_file, indent=4)

    return sample_mapping

def main():
    args = parse_arguments()
    sample_mapping = map_input_files(args)
    print(f"Sample mapping written to {args.output}")

if __name__ == '__main__':
    main()