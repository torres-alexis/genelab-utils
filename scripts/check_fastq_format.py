#!/usr/bin/env python

"""
Script to check FASTQ format of files.
"""

import argparse
import os
import gzip

def parse_arguments():
    parser = argparse.ArgumentParser(description='Check FASTQ format of files.')
    parser.add_argument('--input_files', required=True, nargs='+', help='Input file paths.')
    parser.add_argument('--output_dir', required=True, help='Output directory for validated files.')
    parser.add_argument('--sample_id', required=True, help='Sample ID.')
    return parser.parse_args()

def check_fastq_format(filepath):
    try:
        with gzip.open(filepath, 'rt') as f:
            line_counter = 0
            for line in f:
                line_counter += 1
                if line_counter % 4 == 0:
                    # Quality score line
                    continue
                elif line_counter % 4 == 1:
                    # Header line
                    if not line.startswith('@'):
                        print(f"Invalid header line in {filepath} at line {line_counter}")
                        return False
                elif line_counter % 4 == 2:
                    # Sequence line
                    continue
                elif line_counter % 4 == 3:
                    # Separator line
                    if not line.startswith('+'):
                        print(f"Invalid separator line in {filepath} at line {line_counter}")
                        return False
            return True
    except Exception as e:
        print(f"Error checking FASTQ format for {filepath}: {e}")
        return False

def copy_valid_file(filepath, output_dir):
    filename = os.path.basename(filepath)
    new_filepath = os.path.join(output_dir, filename)
    shutil.copy2(filepath, new_filepath)

def main():
    args = parse_arguments()
    os.makedirs(args.output_dir, exist_ok=True)
    for filepath in args.input_files:
        if check_fastq_format(filepath):
            copy_valid_file(filepath, args.output_dir)
            print(f"File {filepath} is in valid FASTQ format.")
        else:
            print(f"File {filepath} is not in valid FASTQ format.")

if __name__ == '__main__':
    import shutil
    main()