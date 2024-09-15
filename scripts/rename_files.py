#!/usr/bin/env python

"""
Script to rename input files according to GeneLab conventions.
"""

import argparse
import os
import shutil

def parse_arguments():
    parser = argparse.ArgumentParser(description='Rename files to follow GeneLab conventions.')
    parser.add_argument('--input_files', required=True, nargs='+', help='Input file paths.')
    parser.add_argument('--sample_id', required=True, help='Sample ID.')
    parser.add_argument('--output_dir', required=True, help='Output directory.')
    parser.add_argument('--assay', required=True, help='Assay type.')
    parser.add_argument('--single_ended', action='store_true', help='Use if data are single-end sequencing.')
    parser.add_argument('--ATACseq', action='store_true', help='Use if data are ATACseq.')
    parser.add_argument('--HRremoved_suffix', action='store_true', help='Use if "HRremoved" suffix is expected.')
    return parser.parse_args()

def get_standard_suffix(read_label, args):
    if args.HRremoved_suffix:
        suffix = f"_{read_label}_HRremoved_raw.fastq.gz"
    else:
        suffix = f"_{read_label}_raw.fastq.gz"
    return suffix

def rename_files(args):
    os.makedirs(args.output_dir, exist_ok=True)
    for filepath in args.input_files:
        filename = os.path.basename(filepath)
        # Determine read label (e.g., R1, R2)
        if '_R1_' in filename or '_R1.' in filename:
            read_label = 'R1'
        elif '_R2_' in filename or '_R2.' in filename:
            read_label = 'R2'
        elif '_R3_' in filename or '_R3.' in filename:
            read_label = 'R3'
        elif '_R4_' in filename or '_R4.' in filename:
            read_label = 'R4'
        else:
            print(f"Cannot determine read label for file {filename}. Skipping.")
            continue
        standard_suffix = get_standard_suffix(read_label, args)
        new_filename = f"{args.sample_id}{standard_suffix}"
        new_filepath = os.path.join(args.output_dir, new_filename)
        shutil.copy2(filepath, new_filepath)
        print(f"Renamed {filepath} to {new_filepath}")

def main():
    args = parse_arguments()
    rename_files(args)

if __name__ == '__main__':
    main()