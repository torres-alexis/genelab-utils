#! /usr/bin/env python

import sys
import os
import csv
import glob
import io
import zipfile

import argparse

def find_new_filenames(sample, num_reads, fastq_dir):
    new_names = []
    for i in range(1, num_reads+1):
        pattern1 = os.path.join(fastq_dir, f"{sample}_R{i}_raw.fastq.gz")
        pattern2 = os.path.join(fastq_dir, f"{sample}_R{i}_HRremoved_raw.fastq.gz")
        matches = glob.glob(pattern1) + glob.glob(pattern2)
        if matches:
            new_names.append(os.path.basename(matches[0]))
        else:
            new_names.append('')
    return new_names

def load_md5s(md5_file):
    md5_map = {}
    with open(md5_file) as f:
        for line in f:
            parts = line.strip().split()  # split on any whitespace
            if len(parts) == 2:
                md5, fname = parts
                md5_map[os.path.basename(fname)] = md5
    return md5_map

def get_gzip_check(new_filenames, gzip_dir):
    results = []
    for nf in new_filenames:
        if nf:
            check_file = os.path.join(gzip_dir, f"{nf}.gzip_check")
            if os.path.exists(check_file):
                with open(check_file) as f:
                    results.append(f.read().strip())
            else:
                results.append('')
        else:
            results.append('')
    return results

def get_fastq_checks(sample, new_filenames, fastq_info_dir):
    results = []
    for nf in new_filenames:
        if nf:
            check_file = os.path.join(fastq_info_dir, f"{nf}.fastq_info")
            if os.path.exists(check_file):
                with open(check_file) as f:
                    results.append(f.read().strip())
            else:
                results.append('')
        else:
            results.append('')
    return results

def get_paired_fastq_check(sample, fastq_info_dir, atacseq=False, single_cell=False, files_per_sample=0):
    if atacseq:
        check_file = os.path.join(fastq_info_dir, f"{sample}_paired_R1_R3.fastq_info")
    elif single_cell:
        if files_per_sample == 3:
            check_file = os.path.join(fastq_info_dir, f"{sample}_paired_R1_R3.fastq_info")
        else:
            # No paired check for 4-file single-cell
            return ''
    else:
        check_file = os.path.join(fastq_info_dir, f"{sample}_paired.fastq_info")
    if os.path.exists(check_file):
        with open(check_file) as f:
            return f.read().strip()
    return ''

def extract_num_reads_from_multiqc(multiqc_zip_path, sample_ids, num_reads):
    """Return a dict: sample -> [R1_num_reads, R2_num_reads, ...] from multiqc_fastqc.txt in the zip."""
    num_reads_dict = {sid: ['']*num_reads for sid in sample_ids}
    with zipfile.ZipFile(multiqc_zip_path) as z:
        fastqc_file = [f for f in z.namelist() if f.endswith('multiqc_fastqc.txt')][0]
        with z.open(fastqc_file) as f:
            lines = [l.decode('utf-8').rstrip('\n') for l in f]
    header = lines[0].split('\t')
    sample_col = header.index('Sample')
    total_seq_col = header.index('Total Sequences')
    for line in lines[1:]:
        parts = line.split('\t')
        if len(parts) <= max(sample_col, total_seq_col):
            continue
        sample = parts[sample_col]
        total_seqs = parts[total_seq_col]
        # Match sample name and read number
        for sid in sample_ids:
            for i in range(1, num_reads+1):
                if sample == f"{sid}_R{i}":
                    num_reads_dict[sid][i-1] = total_seqs
    return num_reads_dict

def extract_read_length_ranges_from_multiqc(multiqc_zip_path, sample_ids, num_reads):
    """Return a dict: sample -> [R1_read_length_range, R2_read_length_range, ...] from multiqc_fastqc.txt in the zip."""
    length_range_dict = {sid: ['']*num_reads for sid in sample_ids}
    with zipfile.ZipFile(multiqc_zip_path) as z:
        fastqc_file = [f for f in z.namelist() if f.endswith('multiqc_fastqc.txt')][0]
        with z.open(fastqc_file) as f:
            lines = [l.decode('utf-8').rstrip('\n') for l in f]
    header = lines[0].split('\t')
    sample_col = header.index('Sample')
    length_range_col = header.index('Sequence length')
    for line in lines[1:]:
        parts = line.split('\t')
        if len(parts) <= max(sample_col, length_range_col):
            continue
        sample = parts[sample_col]
        length_range = parts[length_range_col]
        for sid in sample_ids:
            for i in range(1, num_reads+1):
                if sample == f"{sid}_R{i}":
                    length_range_dict[sid][i-1] = length_range
    return length_range_dict

def extract_avg_read_lengths_from_multiqc(multiqc_zip_path, sample_ids, num_reads):
    """Return a dict: sample -> [R1_avg_read_length, R2_avg_read_length, ...] from multiqc_fastqc.txt in the zip."""
    avg_length_dict = {sid: ['']*num_reads for sid in sample_ids}
    with zipfile.ZipFile(multiqc_zip_path) as z:
        fastqc_file = [f for f in z.namelist() if f.endswith('multiqc_fastqc.txt')][0]
        with z.open(fastqc_file) as f:
            lines = [l.decode('utf-8').rstrip('\n') for l in f]
    header = lines[0].split('\t')
    sample_col = header.index('Sample')
    avg_length_col = header.index('avg_sequence_length')
    for line in lines[1:]:
        parts = line.split('\t')
        if len(parts) <= max(sample_col, avg_length_col):
            continue
        sample = parts[sample_col]
        avg_length = parts[avg_length_col]
        for sid in sample_ids:
            for i in range(1, num_reads+1):
                if sample == f"{sid}_R{i}":
                    avg_length_dict[sid][i-1] = avg_length
    return avg_length_dict

def extract_num_fastqc_reports_from_multiqc(multiqc_zip_path, sample_ids, num_reads):
    """Return a dict: sample -> count of RX present in multiqc_fastqc.txt Sample column."""
    report_count = {sid: 0 for sid in sample_ids}
    with zipfile.ZipFile(multiqc_zip_path) as z:
        fastqc_file = [f for f in z.namelist() if f.endswith('multiqc_fastqc.txt')][0]
        with z.open(fastqc_file) as f:
            lines = [l.decode('utf-8').rstrip('\n') for l in f]
    header = lines[0].split('\t')
    sample_col = header.index('Sample')
    fastqc_samples = set(line.split('\t')[sample_col] for line in lines[1:] if line)
    for sid in sample_ids:
        count = 0
        for i in range(1, num_reads+1):
            if f"{sid}_R{i}" in fastqc_samples:
                count += 1
        report_count[sid] = count
    return report_count

def load_reference_md5s(reference_md5_file):
    ref_md5_map = {}
    with open(reference_md5_file) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                md5, fname = parts
                ref_md5_map[os.path.basename(fname)] = md5
    return ref_md5_map

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample_sheet', required=True)
    parser.add_argument('--accession', required=True)
    parser.add_argument('--read_dir', required=True)
    parser.add_argument('--gzip_dir', required=True)
    parser.add_argument('--fastq_info_dir', required=True)
    parser.add_argument('--md5', required=True)
    parser.add_argument('--multiqc_data_zip', required=True)
    parser.add_argument('--reference_md5', required=False)
    parser.add_argument('--atacseq', action='store_true', default=False)
    parser.add_argument('--single_cell', action='store_true', default=False)
    parser.add_argument('--files_per_sample', type=int, default=0)
    args = parser.parse_args()

    out_file = f"{args.accession}-raw-validation-summary.tsv"
    md5_map = load_md5s(args.md5)

    ref_md5_map = None
    if args.reference_md5 and os.path.exists(args.reference_md5):
        ref_md5_map = load_reference_md5s(args.reference_md5)

    with open(args.sample_sheet, newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        rows = list(reader)

    # Find all read columns
    read_cols = [col for col in reader.fieldnames if col.startswith('read') and col.endswith('_path')]
    read_cols.sort()  # Ensure order: read1_path, read2_path, ...

    # Prepare header dynamically for 1-4 reads, then add stubs
    out_header = ['unique_ID', 'num_read_files']
    for i, col in enumerate(read_cols, 1):
        out_header.append(f'orig_R{i}_filename')
    for i, col in enumerate(read_cols, 1):
        out_header.append(f'new_R{i}_filename')
    for i, col in enumerate(read_cols, 1):
        out_header.append(f'R{i}_md5')
    for i, col in enumerate(read_cols, 1):
        out_header.append(f'R{i}_gzip_test')
    for i, col in enumerate(read_cols, 1):
        out_header.append(f'R{i}_fastq_format_check')
    out_header.append('paired_fastq_format_check')
    for i, col in enumerate(read_cols, 1):
        out_header.append(f'R{i}_num_reads')
    if len(read_cols) == 2:
        out_header.append('R1_and_R2_num_reads_equal')
    elif len(read_cols) == 3:
        out_header.append('R1_R2_and_R3_num_reads_equal')
    elif len(read_cols) == 4:
        out_header.append('R1_R2_R3_and_R4_num_reads_equal')
    for i, col in enumerate(read_cols, 1):
        out_header.append(f'R{i}_read_length_range')
    for i, col in enumerate(read_cols, 1):
        out_header.append(f'R{i}_avg_read_length')
    # Add read_lengths_equal col dynamically
    if len(read_cols) == 2:
        out_header.append('R1_and_R2_read_lengths_equal')
    elif len(read_cols) == 3:
        out_header.append('R1_R2_and_R3_read_lengths_equal')
    elif len(read_cols) == 4:
        out_header.append('R1_R2_R3_and_R4_read_lengths_equal')
    out_header.append('num_fastqc_reports_in_multiqc_report')
    # Only add md5_check columns if reference md5 is provided
    if ref_md5_map:
        if len(read_cols) == 2:
            out_header += ['R1_md5_check', 'R2_md5_check']
        elif len(read_cols) == 3:
            out_header += ['R1_md5_check', 'R2_md5_check', 'R3_md5_check']
        elif len(read_cols) == 4:
            out_header += ['R1_md5_check', 'R2_md5_check', 'R3_md5_check', 'R4_md5_check']

    # Extract num_reads, read_length_ranges, avg_read_lengths, num_fastqc_reports from multiqc zip
    sample_ids = [row['Sample Name'] for row in rows]
    num_reads_dict = extract_num_reads_from_multiqc(args.multiqc_data_zip, sample_ids, len(read_cols))
    length_range_dict = extract_read_length_ranges_from_multiqc(args.multiqc_data_zip, sample_ids, len(read_cols))
    avg_length_dict = extract_avg_read_lengths_from_multiqc(args.multiqc_data_zip, sample_ids, len(read_cols))
    fastqc_report_count = extract_num_fastqc_reports_from_multiqc(args.multiqc_data_zip, sample_ids, len(read_cols))

    with open(out_file, 'w', newline='') as out_f:
        writer = csv.writer(out_f, delimiter='\t', lineterminator='\n')
        writer.writerow(out_header)

        for row in rows:
            unique_id = row['Sample Name']
            num_reads = len(read_cols)
            orig_filenames = [os.path.basename(row[col]) if row[col] else '' for col in read_cols]
            new_filenames = find_new_filenames(unique_id, num_reads, args.read_dir)
            R_md5s = [md5_map.get(nf, '') if nf else '' for nf in new_filenames]
            R_gzip_tests = get_gzip_check(new_filenames, args.gzip_dir)
            R_fastq_checks = get_fastq_checks(unique_id, new_filenames, args.fastq_info_dir)
            paired_fastq_check = get_paired_fastq_check(
                unique_id,
                args.fastq_info_dir,
                atacseq=args.atacseq,
                single_cell=args.single_cell,
                files_per_sample=args.files_per_sample
            )
            RX_num_reads = num_reads_dict.get(unique_id, ['']*num_reads)
            RX_length_ranges = length_range_dict.get(unique_id, ['']*num_reads)
            RX_avg_lengths = avg_length_dict.get(unique_id, ['']*num_reads)
            row_data = [unique_id, num_reads]
            row_data += orig_filenames
            row_data += new_filenames
            row_data += R_md5s
            row_data += R_gzip_tests
            row_data += R_fastq_checks
            row_data.append(paired_fastq_check)
            row_data += RX_num_reads
            if num_reads == 2:
                num_reads_equal = "YES" if RX_num_reads[0] == RX_num_reads[1] and RX_num_reads[0] != '' else "NO"
                row_data.append(num_reads_equal)
            elif num_reads == 3:
                num_reads_equal = "YES" if RX_num_reads[0] == RX_num_reads[1] == RX_num_reads[2] and RX_num_reads[0] != '' else "NO"
                row_data.append(num_reads_equal)
            elif num_reads == 4:
                num_reads_equal = "YES" if RX_num_reads[0] == RX_num_reads[1] == RX_num_reads[2] == RX_num_reads[3] and RX_num_reads[0] != '' else "NO"
                row_data.append(num_reads_equal)
            row_data += RX_length_ranges
            row_data += RX_avg_lengths
            # Add read_lengths_equal col dynamically
            if num_reads == 2:
                lengths_equal = "YES" if RX_length_ranges[0] == RX_length_ranges[1] and RX_avg_lengths[0] == RX_avg_lengths[1] and RX_length_ranges[0] != '' else "NO"
                row_data.append(lengths_equal)
            elif num_reads == 3:
                lengths_equal = "YES" if RX_length_ranges[0] == RX_length_ranges[1] == RX_length_ranges[2] and RX_avg_lengths[0] == RX_avg_lengths[1] == RX_avg_lengths[2] and RX_length_ranges[0] != '' else "NO"
                row_data.append(lengths_equal)
            elif num_reads == 4:
                lengths_equal = "YES" if RX_length_ranges[0] == RX_length_ranges[1] == RX_length_ranges[2] == RX_length_ranges[3] and RX_avg_lengths[0] == RX_avg_lengths[1] == RX_avg_lengths[2] == RX_avg_lengths[3] and RX_length_ranges[0] != '' else "NO"
                row_data.append(lengths_equal)
            row_data.append(fastqc_report_count.get(unique_id, 0))
            # Add md5_vs_reference columns if reference_md5 is provided
            R_md5_checks = []
            if ref_md5_map:
                for i, orig_filename in enumerate(orig_filenames):
                    ref_md5 = ref_md5_map.get(orig_filename, '')
                    actual_md5 = R_md5s[i]
                    if not orig_filename or not ref_md5 or not actual_md5:
                        R_md5_checks.append('')
                    elif actual_md5 == ref_md5:
                        R_md5_checks.append('PASS')
                    else:
                        R_md5_checks.append('FAIL')
            else:
                # If no reference, just fill with empty or whatever you want
                R_md5_checks = [''] * len(orig_filenames)
            row_data += R_md5_checks

            # Replace new filenames with "not-renamed" if they match original filenames
            orig_start = 2  # index of first orig_R{i}_filename
            new_start = orig_start + len(orig_filenames)  # index of first new_R{i}_filename

            for i in range(len(orig_filenames)):
                if orig_filenames[i] == new_filenames[i]:
                    row_data[new_start + i] = "not-renamed"

            writer.writerow(row_data)

if __name__ == '__main__':
    main() 