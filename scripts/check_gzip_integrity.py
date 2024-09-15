#!/usr/bin/env python

"""
Script to check the integrity of gzip-compressed FASTQ files.
"""

import argparse
import gzip
import os
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(description='Check gzip integrity of compressed FASTQ files.')
    parser.add_argument('--input_files', required=True, nargs='+', help='Input file paths.')
    parser.add_argument('--output_dir', required=True, help='Output directory for verified files.')
    parser.add_argument('--sample_id', required=True, help='Sample ID.')
    return parser.parse_args()

def check_gzip_file(filepath):
    try:
        with gzip.open(filepath, 'rb') as f:
            while f.read(8192):
                pass
        return True
    except OSError as e:
        print(f"Error with file {filepath}: {e}")
        return False

def copy_valid_file(filepath, output_dir):
    filename = os.path.basename(filepath)
    new_filepath = os.path.join(output_dir, filename)
    shutil.copy2(filepath, new_filepath)

def main():
    args = parse_arguments()
    os.makedirs(args.output_dir, exist_ok=True)
    for filepath in args.input_files:
        if check_gzip_file(filepath):
            copy_valid_file(filepath, args.output_dir)
            print(f"File {filepath} passed gzip integrity check.")
        else:
            print(f"File {filepath} failed gzip integrity check.")

if __name__ == '__main__':
    import shutil
    main()