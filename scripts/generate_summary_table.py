#!/usr/bin/env python

"""
Script to generate summary table of validation results.
"""

import argparse
import json
import pandas as pd

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate summary table of validation results.')
    parser.add_argument('--sample_data', required=True, help='JSON file containing sample data.')
    parser.add_argument('--output', required=True, help='Output TSV file for the summary table.')
    return parser.parse_args()

def generate_summary_table(sample_data):
    # sample_data is expected to be a dictionary with sample IDs as keys
    records = []
    for sample_id, data in sample_data.items():
        record = {
            'Sample ID': sample_id,
            'Total Reads': data.get('total_reads', 'NA'),
            'Average Read Length': data.get('avg_read_length', 'NA'),
            'Validation Status': data.get('status', 'NA'),
        }
        records.append(record)
    df = pd.DataFrame(records)
    return df

def main():
    args = parse_arguments()
    with open(args.sample_data, 'r') as f:
        sample_data = json.load(f)
    summary_df = generate_summary_table(sample_data)
    summary_df.to_csv(args.output, sep='\t', index=False)
    print(f"Summary table written to {args.output}")

if __name__ == '__main__':
    main()