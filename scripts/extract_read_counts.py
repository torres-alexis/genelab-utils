#!/usr/bin/env python

"""
Script to extract read counts and lengths from FASTQ files.
"""

import argparse
import gzip

def parse_arguments():
    parser = argparse.ArgumentParser(description='Extract read counts and lengths from FASTQ files.')
    parser.add_argument('--input_files', required=True, nargs='+', help='Input FASTQ file paths.')
    return parser.parse_args()

def extract_read_counts_and_lengths(filepaths):
    total_reads = 0
    read_lengths = []
    for filepath in filepaths:
        with gzip.open(filepath, 'rt') as f:
            line_counter = 0
            for line in f:
                line_counter += 1
                if line_counter % 4 == 2:
                    seq_length = len(line.strip())
                    read_lengths.append(seq_length)
            reads_in_file = line_counter // 4
            print(f"Found {reads_in_file} reads in {filepath}")
            total_reads += reads_in_file
    average_read_length = sum(read_lengths) / len(read_lengths) if read_lengths else 0
    return total_reads, average_read_length

def main():
    args = parse_arguments()
    total_reads, avg_read_length = extract_read_counts_and_lengths(args.input_files)
    print(f"Total Reads: {total_reads}")
    print(f"Average Read Length: {avg_read_length:.2f}")
    # Output can be formatted as needed for downstream processes

if __name__ == '__main__':
    main()