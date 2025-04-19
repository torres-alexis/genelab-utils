#!/usr/bin/env python3
import os
import glob
import re
import sys
import csv
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
        # Try to match _R1_, _R2_, _R3_, _R4_ (or .R1., -R1-, etc)
        m = re.match(r"(.+?)(_R[1234]|\.R[1234]|-[Rr][1234]|_[1234])[_\.-]", os.path.basename(f))
        if m:
            sid = m.group(1)
        else:
            # Fallback: use everything before first underscore
            sid = os.path.basename(f).split('_')[0]
        sample_map[sid].append(f)
    # Sort file lists for each sample for reproducibility
    for sid in sample_map:
        sample_map[sid] = sorted(sample_map[sid])
    return sample_map

def main(input_dir):
    files = find_fastq_files(input_dir)
    if not files:
        print(f"No FASTQ files found in {input_dir}", file=sys.stderr)
        sys.exit(1)
    sample_map = group_by_sample(files)
    max_reads = max(len(files) for files in sample_map.values()) if sample_map else 0
    if max_reads > 4:
        print("Warning: More than 4 read files found for at least one sample. Only the first 4 will be included.", file=sys.stderr)
    header = ['Sample Name'] + [f'read{i+1}_path' for i in range(max_reads if max_reads <= 4 else 4)]
    with open('sample_sheet.tsv', 'w', newline='') as out:
        writer = csv.writer(out, delimiter='\t')
        writer.writerow(header)
        for sid, flist in sample_map.items():
            row = [sid] + flist[:4] + [''] * (max_reads - len(flist))
            writer.writerow(row)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: create_sample_sheet.py <input_dir>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
