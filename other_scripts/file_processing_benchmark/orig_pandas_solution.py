import sys
import argparse
import pandas as pd
from pathlib import Path
import os
import errno

IEDB_COLUMNS = ["trimmed_seq", "original_seq", "receptor_group", "epitopes", "source_organisms", "source_antigens"]


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs_file", default="/Users/lonneke/PycharmProjects/tcrmatch_compairr/scripts/file_processing_benchmark/pairs_small.tsv")
    parser.add_argument("--output_folder", default="/Users/lonneke/PycharmProjects/tcrmatch_compairr/scripts/file_processing_benchmark/pandas1")

    parsed_args = parser.parse_args(args)

    return parsed_args

def reformat_pairs_file(pairs_file):
    df = pd.read_csv(pairs_file, sep="\t", usecols=["cdr3_aa_1", "cdr3_aa_2", "original_seq_1", "receptor_group_1", "epitopes_1", "source_organisms_1", "source_antigens_1"])
    df.rename(columns={"cdr3_aa_1": "trimmed_seq", "cdr3_aa_2": "user_seq",
                       "original_seq_1": "original_seq",
                       "receptor_group_1": "receptor_group",
                       "epitopes_1": "epitopes",
                       "source_organisms_1": "source_organisms",
                       "source_antigens_1": "source_antigens"}, inplace=True)

    return df

def build_path(path):
    path = Path(path)
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    return path
def export_split_results(result_df, output_folder):
    idx = 1
    for user_cdr3, filtered_iedb in result_df.groupby("user_seq"):
        export_results_df(filtered_iedb, str(Path(output_folder) / f"prefiltered_IEDB_{user_cdr3}_{idx}.tsv"))
        export_cdr3(user_cdr3, str(Path(output_folder) / f"user_cdr3_{user_cdr3}_{idx}.txt"))

        idx += 1

def export_results_df(result_df, output_file):
    result = result_df[IEDB_COLUMNS] #.copy()
    #result = result.drop_duplicates()
    result.to_csv(output_file, sep="\t", index=False)

def export_cdr3(export_cdr3, output_file):
    with open(output_file, "w") as file:
        file.writelines([export_cdr3, "\n"])


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    result_df = reformat_pairs_file(args.pairs_file)
    build_path(args.output_folder)
    export_split_results(result_df, args.output_folder)
