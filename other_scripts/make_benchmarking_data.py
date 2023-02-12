import sys
import argparse
from pathlib import Path
import pandas as pd
import random

pd.set_option('display.max_columns', None)

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--olga_sequences", default="../data/olga/olga_sequences.tsv")
    parser.add_argument("--iedb_sequences", default="../data/IEDB_data.tsv")
    parser.add_argument("--output_folder", default="../data/benchmarking_data")
    parser.add_argument("--n_sequences", default=[10000, 100000, 1000000])
    parser.add_argument("--iedb_implant_rate", default=[0.1, 0.01, 0.001])

    parsed_args = parser.parse_args(args)
    parsed_args.olga_sequences = Path(parsed_args.olga_sequences)
    parsed_args.iedb_sequences = Path(parsed_args.iedb_sequences)
    parsed_args.output_folder = Path(parsed_args.output_folder)

    return parsed_args

def get_olga_cdr3s(olga_file):
    olga_sequences = pd.read_csv(olga_file, sep="\t", header=None)[1]

    return [seq[1:-1] for seq in olga_sequences]

def get_iedb_cdr3s(iedb_file):
    return list(pd.read_csv(iedb_file, sep="\t")["trimmed_seq"])

def make_bemchmarking_dataset(olga_sequences, iedb_sequences, n_sequences, iedb_implant_rate):
    n_iedb_sequences = int(n_sequences * iedb_implant_rate)
    n_olga_sequences = n_sequences - n_iedb_sequences

    return olga_sequences[:n_olga_sequences] + iedb_sequences[:n_iedb_sequences]

def export_benchmarking_dataset(output_file, sequences):
    lines = ["cdr3_aa"] + sequences
    lines = [f"{line}\n" for line in lines]

    with open(output_file, "w") as file:
        file.writelines(lines)

def main(args):
    olga_cdr3s = get_olga_cdr3s(args.olga_sequences)
    iedb_cdr3s = get_iedb_cdr3s(args.iedb_sequences)

    for n_sequences in args.n_sequences:
        for iedb_implant_rate in args.iedb_implant_rate:
            random.shuffle(olga_cdr3s)
            random.shuffle(iedb_cdr3s)
            sequences = make_bemchmarking_dataset(olga_cdr3s, iedb_cdr3s, n_sequences, iedb_implant_rate)
            output_file = args.output_folder / f"1e{len(str(n_sequences)) - 1}_{iedb_implant_rate*100}.tsv"
            export_benchmarking_dataset(output_file, sequences)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    main(args)


