#!/usr/bin/env python

"""
Script to generate MD5 checksums for files.
"""

import argparse
import hashlib
import os

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate MD5 checksums for files.')
    parser.add_argument('--input_files', required=True, nargs='+', help='Input file paths.')
    parser.add_argument('--output_dir', required=True, help='Output directory for MD5 files.')
    parser.add_argument('--sample_id', required=True, help='Sample ID.')
    return parser.parse_args()

def generate_md5(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def main():
    args = parse_arguments()
    os.makedirs(args.output_dir, exist_ok=True)
    md5_file_path = os.path.join(args.output_dir, f"{args.sample_id}.md5")
    with open(md5_file_path, 'w') as md5_file:
        for filepath in args.input_files:
            md5sum = generate_md5(filepath)
            filename = os.path.basename(filepath)
            md5_file.write(f"{md5sum}  {filename}\n")
            print(f"Generated MD5 for {filepath}")
    print(f"MD5 checksums written to {md5_file_path}")

if __name__ == '__main__':
    main()