import sys
import argparse
import pandas as pd
from pathlib import Path
import os
import errno
import io

def chunk_write(input_file, output_folder, chunk_size):
    df = pd.read_csv(input_file, sep="\t", usecols=["cdr3_aa_1", "cdr3_aa_2", "original_seq_1", "receptor_group_1", "epitopes_1", "source_organisms_1", "source_antigens_1"], iterator = True, chunksize=chunk_size)

    file_contents = {}
    for chunk in df:
        for i in range(len(chunk)):
            user_seq = chunk.iloc[i]["cdr3_aa_2"]
            if user_seq in file_contents:
                file_contents[user_seq].write("	".join(map(str, chunk.iloc[i].values[:-1])))
                file_contents[user_seq].write("\n")
            else:
                file_contents[user_seq] = io.StringIO()
                file_contents[user_seq].write("trimmed_seq	original_seq	receptor_group	epitopes	source_organisms	source_antigens\n")

                file_contents[user_seq].write("	".join(map(str, chunk.iloc[i].values[:-1])))
                file_contents[user_seq].write("\n")

    i = 1
    for user_cdr3, value in file_contents.items():
        with open(f"{output_folder}/prefiltered_IEDB_{user_cdr3}_{i}.tsv", "w") as f:
            f.write(value.getvalue())

        with open(f"{output_folder}/user_cdr3_{user_cdr3}_{i}.tsv", "w") as f:
            f.write(f"{user_cdr3}\n")

        i += 1

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs_file", default="/Users/lonneke/PycharmProjects/tcrmatch_compairr/scripts/file_processing_benchmark/pairs_small.tsv")
    parser.add_argument("--output_folder", default="/Users/lonneke/PycharmProjects/tcrmatch_compairr/scripts/file_processing_benchmark/pandas1")
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
