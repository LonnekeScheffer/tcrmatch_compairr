import sys
import argparse
import pandas as pd
from pathlib import Path

IEDB_COLUMNS = ["trimmed_seq", "original_seq", "receptor_group", "epitopes", "source_organisms", "source_antigens"]


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--iedb_file", default="../data/IEDB_for_compairr.tsv")
    parser.add_argument("--pairs_file", default="../output/tmp/pairs.tsv")
    parser.add_argument("--output_file", default="../output/tmp/prefiltered_IEDB.tsv")
    parser.add_argument("--split_output", action='store_true', default=False)
    parser.add_argument("--output_folder", default="../output/tmp/")

    parsed_args = parser.parse_args(args)

    return parsed_args


def add_cols(iedb_file, pairs_file):
    iedb = pd.read_csv(iedb_file, sep="\t", usecols=['sequence_id', 'repertoire_id', 'cdr3_aa', 'original_seq', 'receptor_group', 'epitopes', 'source_organisms', 'source_antigens'])
    iedb.rename(columns={"cdr3_aa": "trimmed_seq"}, inplace=True)

    filtered = pd.read_csv(pairs_file, sep="\t", usecols=["sequence_id_1", "cdr3_aa_1", "cdr3_aa_2"])
    filtered.rename(columns={"sequence_id_1": "sequence_id", "cdr3_aa_1": "trimmed_seq", "cdr3_aa_2": "user_seq"}, inplace=True)
    filtered.drop_duplicates(inplace=True)

    return pd.merge(iedb, filtered, how="right", on=["sequence_id", "trimmed_seq"])

def export_split_results(result_df, output_folder):
    idx = 1
    for user_cdr3, filtered_iedb in result_df.groupby("user_seq"):
        export_results_df(filtered_iedb, str(Path(output_folder) / f"prefiltered_IEDB_{idx}.tsv"))
        export_cdr3(user_cdr3, str(Path(output_folder) / f"user_cdr3_{idx}.txt"))

        idx += 1

def export_results_df(result_df, output_file):
    result = result_df[IEDB_COLUMNS]
    result.to_csv(output_file, sep="\t", index=False)

def export_cdr3(export_cdr3, output_file):
    with open(output_file, "w") as file:
        file.writelines(["cdr3_aa\n", export_cdr3])

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    result_df = add_cols(args.iedb_file, args.pairs_file)

    if args.split_output:
        export_split_results(result_df, args.output_folder)
    else:
        export_results_df(result_df, args.output_file)