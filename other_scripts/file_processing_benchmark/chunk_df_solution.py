import sys
import argparse
import pandas as pd
from pathlib import Path
import os
import errno

IEDB_COLUMNS = ["trimmed_seq", "original_seq", "receptor_group", "epitopes", "source_organisms", "source_antigens"]
COLUMN_ORDER = ["cdr3_aa_1", "original_seq_1", "receptor_group_1", "epitopes_1", "source_organisms_1", "source_antigens_1"]

def export_cdr3(export_cdr3, output_file):
    with open(output_file, "w") as file:
        file.write(f"{export_cdr3}\n")

def chunk_write(input_file, output_folder, chunk_size):
    df = pd.read_csv(input_file, sep="\t", usecols=["cdr3_aa_1", "cdr3_aa_2", "original_seq_1", "receptor_group_1", "epitopes_1", "source_organisms_1", "source_antigens_1"], iterator=True, chunksize=chunk_size)

    existing_files = {}

    counter = 0

    for chunk in df:
        for user_cdr3, cdr3_chunk in chunk.groupby("cdr3_aa_2"):
            if user_cdr3 in existing_files:
                id = existing_files[user_cdr3]
                cdr3_chunk[COLUMN_ORDER].to_csv(f"{output_folder}/prefiltered_IEDB_{user_cdr3}_{id}.tsv", mode="a", index=False, header=False, sep="\t")

            else:
                counter += 1
                existing_files[user_cdr3] = counter
                id = counter

                cdr3_chunk[COLUMN_ORDER].to_csv(f"{output_folder}/prefiltered_IEDB_{user_cdr3}_{id}.tsv", sep="\t", index=False, header=IEDB_COLUMNS)

                export_cdr3(user_cdr3, f"{output_folder}/user_cdr3_{user_cdr3}_{id}.tsv")


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs_file", default="/Users/lonneke/PycharmProjects/tcrmatch_compairr/scripts/file_processing_benchmark/pairs_small.tsv")
    parser.add_argument("--output_folder", default="/Users/lonneke/PycharmProjects/tcrmatch_compairr/scripts/file_processing_benchmark/pandas_chunky")
    parser.add_argument("--chunk_size", type=int, default=10000)

    parsed_args = parser.parse_args(args)

    return parsed_args

def build_path(path):
    path = Path(path)
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    return path


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    build_path(args.output_folder)
    chunk_write(args.pairs_file, args.output_folder, args.chunk_size)
