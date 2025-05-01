#!/usr/bin/env python3
import os
import glob
import re
import sys
import csv
import argparse
from collections import defaultdict

def find_fastq_files(input_dir):
    # Find all .fastq.gz and .fq.gz files
    patterns = ["*.fastq.gz", "*.fq.gz"]
    files = []
    for pat in patterns:
        files.extend(glob.glob(os.path.join(input_dir, pat)))
    return sorted(files)

def group_by_sample(files):
    sample_map = defaultdict(list)
    for f in files:
        # Try to match _R1_, _R2_, _R3_, _R4_ (or .R1., -R1-, etc) \ must be right before the extension
        m = re.match(r"(.+?)[_\.-]([Rr][1234]|[1234])[_\.-].*?raw\.(?:fastq|fq)\.gz$", os.path.basename(f))
        if m:
            sid = m.group(1)
        else:
            # Fallback: use everything before '_raw.fastq.gz'
            sid = os.path.basename(f).split('_raw.fastq.gz')[0]
        sample_map[sid].append(f)
    # Sort file lists for each sample
    for sid in sample_map:
        sample_map[sid] = sorted(sample_map[sid])
    return sample_map

def main(input_dir, files_per_sample):
    files = find_fastq_files(input_dir)
    if not files:
        print(f"No FASTQ files found in {input_dir}", file=sys.stderr)
        sys.exit(1)

    sample_map = group_by_sample(files)
    mismatched_samples = []
    for sid, flist in sample_map.items():
        if len(flist) != files_per_sample:
            mismatched_samples.append((sid, len(flist)))

    if mismatched_samples:
        print(f"Error: Expected {files_per_sample} read files per sample, but found mismatches:", file=sys.stderr)
        for sid, count in mismatched_samples:
            print(f"  Sample '{sid}': Found {count} files", file=sys.stderr)
        sys.exit(1)

    header = ['Sample Name'] + [f'read{i+1}_path' for i in range(files_per_sample)]
    with open('sample_sheet.tsv', 'w', newline='') as out:
        writer = csv.writer(out, delimiter='\t')
        writer.writerow(header)
        # Sort by sample ID for consistent output order
        for sid in sorted(sample_map.keys()):
            row = [sid] + sample_map[sid] # Already sorted and correct length enforced
            writer.writerow(row)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a sample sheet TSV from FASTQ files in a directory.')
    parser.add_argument('--input_dir', required=True, help='Directory containing FASTQ files.')
    parser.add_argument('--files_per_sample', required=True, type=int, help='Expected number of read files per sample.')
    args = parser.parse_args()

    main(args.input_dir, args.files_per_sample)
