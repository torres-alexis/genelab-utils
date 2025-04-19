#!/usr/bin/env python
import sys
import subprocess
import os

def run_fastq_check(file1, file2=None):
    if file2 is None:
        check_out = subprocess.run(['fastq_info', file1], capture_output=True, text=True)
    else:
        check_out = subprocess.run(['fastq_info', file1, file2], capture_output=True, text=True)
    if check_out.returncode == 0:
        return 'PASS'
    else:
        for line in check_out.stderr.splitlines():
            if line.startswith('ERROR'):
                return f'FAIL - {line}'
        return 'FAIL - Fastq check had non-zero exit, but no error reported. Needs a closer look.'

def main():
    files = sys.argv[1:]
    n = len(files)
    if n == 0:
        print("No input files provided.")
        sys.exit(1)
    # Single-end or multi-read: check each file
    for f in files:
        result = run_fastq_check(f)
        with open(f + '.fastq_info', 'w') as out:
            out.write(result + '\n')
    # Paired check for 2 files
    if n == 2:
        result = run_fastq_check(files[0], files[1])
        with open('paired.fastq_info', 'w') as out:
            out.write(result + '\n')
    # ATACseq/single-cell 3-reads: paired R1/R3 check
    if n == 3:
        result = run_fastq_check(files[0], files[2])
        with open('paired_R1_R3.fastq_info', 'w') as out:
            out.write(result + '\n')
    # For 4 files: only individual checks (already done above)

if __name__ == "__main__":
    main() 