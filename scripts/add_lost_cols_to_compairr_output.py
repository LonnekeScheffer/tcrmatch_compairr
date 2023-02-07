import sys
import argparse
import pandas as pd

def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--iedb_file", default="../data/IEDB_for_compairr.tsv")
    parser.add_argument("--pairs_file", default="../output/pairs.tsv")
    parser.add_argument("--output_file", default="../output/prefiltered_IEDB2.tsv")

    parsed_args = parser.parse_args(args)

    return parsed_args


def add_cols(iedb_file, pairs_file, output_file):
    iedb = pd.read_csv(iedb_file, sep="\t", usecols=['sequence_id', 'repertoire_id', 'cdr3_aa', 'original_seq', 'receptor_group', 'epitopes', 'source_organisms', 'source_antigens'])
    iedb.rename(columns={"cdr3_aa": "trimmed_seq"}, inplace=True)

    filtered = pd.read_csv(pairs_file, sep="\t", usecols=["sequence_id_1", "cdr3_aa_1"])
    filtered.rename(columns={"sequence_id_1": "sequence_id", "cdr3_aa_1": "trimmed_seq"}, inplace=True)
    filtered.drop_duplicates(inplace=True)

    iedb_cols = ["trimmed_seq", "original_seq", "receptor_group", "epitopes", "source_organisms", "source_antigens"]

    result = pd.merge(iedb, filtered, how="right", on=["sequence_id", "trimmed_seq"])
    result = result[iedb_cols]
    result.to_csv(output_file, sep="\t", index=False)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    add_cols(args.iedb_file, args.pairs_file, args.output_file)