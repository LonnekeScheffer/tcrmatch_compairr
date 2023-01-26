import sys
import argparse
import os
import errno
import random
import pandas as pd
from pathlib import Path

def build_path(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    return path
def parse_args(args):
    parser = argparse.ArgumentParser()

    parser.add_argument("--n_seqs_per_outfile", nargs='+', type=int, default=[10, 100, 1000, 10000])
    parser.add_argument("--iedb_file", default="../../data/IEDB_data.tsv")
    parser.add_argument("--output_folder", default="../../data/infiles")
    parser.add_argument("--random_seed", default=2023, type=int)

    parsed_args = parser.parse_args(args)

    return parsed_args

def get_legal_sequences(iedb_file):
    df = pd.read_csv(iedb_file, sep="\t", usecols=["trimmed_seq"])

    return list(df["trimmed_seq"])

def write_output_file(output_folder, n_seqs, sequences, random_seed):
    random.seed(random_seed)

    seqs = random.sample(sequences, n_seqs)
    df = pd.DataFrame({"cdr3_aa": seqs})

    outfile_path = Path(output_folder) / f"infile_{n_seqs}_seqs.txt"

    df.to_csv(outfile_path, sep="\t", index=False)




if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    sequences = get_legal_sequences(args.iedb_file)

    build_path(args.output_folder)

    for n_seqs in args.n_seqs_per_outfile:
        write_output_file(args.output_folder, n_seqs, sequences, args.random_seed)