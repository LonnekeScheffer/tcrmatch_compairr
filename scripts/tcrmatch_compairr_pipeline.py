import sys
import argparse
import pandas as pd
from pathlib import Path
import os
import errno
import subprocess
import shutil

def build_path(path):
    path = Path(path)
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    return path

def check_parsed_params(parsed_args):
    parsed_args.user_file = Path(parsed_args.user_file)
    parsed_args.iedb_file = Path(parsed_args.iedb_file)
    parsed_args.output_file = Path(parsed_args.output_file)
    parsed_args.tmp_path = Path(parsed_args.tmp_path)
    parsed_args.compairr_path = Path(parsed_args.compairr_path)
    parsed_args.tcrmatch_path = Path(parsed_args.tcrmatch_path)
    parsed_args.pairs_file = parsed_args.tmp_path / "pairs.tsv"
    parsed_args.compairr_log = parsed_args.tmp_path / "compairr_log.txt"
    parsed_args.compairr_out = parsed_args.tmp_path / "compairr_out.txt"

    build_path(parsed_args.output_file.parent)
    build_path(parsed_args.tmp_path)

    assert parsed_args.user_file.is_file(), f"Missing user_file: {parsed_args.user_file}"
    assert parsed_args.iedb_file.is_file(), f"Missing iedb_file: {parsed_args.iedb_file}"

    assert parsed_args.differences >= 0, f"differences must be a positive integer >= 0, found the following instead: {parsed_args.differences}"
    assert parsed_args.threads >= 1, f"threads must be a positive integer >= 1, found the following instead: {parsed_args.threads}"
    assert 1 > parsed_args.threshold > 0, f"threshold must be between 0 and 1, found the following instead: {parsed_args.threshold}"
    assert parsed_args.indels is False or parsed_args.differences == 1, f"indels can only be true when differences is 1, found the following instead: indels = {parsed_args.indels}, differences = {parsed_args.differences}"
    assert parsed_args.chunk_size >= 1000, f"chunk_size must be a positive integer >= 1000, found the following instead: {parsed_args.chunk_size}"

    return parsed_args

def parse_args(args):
    parser = argparse.ArgumentParser()

    parser.add_argument("-u", "--user_file", type=str, required=True, help="User input file containing newline separated CDR3beta amino acid sequences")
    parser.add_argument("-e", "--iedb_file", type=str, required=True, help="IEDB file, tab-separated file which should contain the following columns: cdr3_aa\toriginal_seq\treceptor_group\tepitopes\tsource_organisms\tsource_antigens")
    parser.add_argument("-o", "--output_file", type=str, required=True, help="Output filename for the TCRMatch results")
    parser.add_argument("-d", "--differences", type=int, default=1, help="CompAIRR setting: number of differences (default = 1)")
    parser.add_argument("-t", "--threads", type=int, default=1, help="CompAIRR setting: number of threads")
    parser.add_argument("-i", "--indels", action="store_true", help="CompAIRR setting: flag for enabling indels (default = no indels)")
    parser.add_argument("-s", "--threshold", type=float, default=0.97, help="TCRMatch setting: parameter to specify the threshold (default = 0.97)")
    parser.add_argument("-c", "--compairr_path", type=str, default="compairr", help="CompAIRR path (default = compairr)")
    parser.add_argument("-m", "--tcrmatch_path", type=str, default="tcrmatch", help="TCRMatch path (default = tcrmatch)")
    parser.add_argument("-l", "--tmp_path", type=str, default="./tmp", help="Temporary directory for storing log files and intermediate results (default = ./tmp)")
    parser.add_argument("-k", "--keep_intermediate", action="store_true", help="Flag for keeping intermediate results, useful for debugging (default = do not keep intermediate results)")
    parser.add_argument("-z", "--chunk_size", type=int, default=100000, help="Chunk size for processing intermediate results (default = 100000)")

    return check_parsed_params(parser.parse_args(args))

def create_pairs_file_with_compairr(args):
    cmd_args = [str(args.compairr_path), str(args.iedb_file), str(args.user_file), "--matrix",
                "--differences", str(args.differences), "--ignore-counts", "--ignore-genes",
                "--cdr3", "--pairs", str(args.pairs_file), "--threads", str(args.threads),
                "--log", str(args.compairr_log), "--output", str(args.compairr_out),
                "--keep-columns", "original_seq,receptor_group,epitopes,source_organisms,source_antigens"]

    indels_args = ["--indels"] if args.indels else []
    cmd_args += indels_args

    subprocess_result = subprocess.run(cmd_args, capture_output=True, text=True, check=True)

    if not args.pairs_file.is_file():
        err_str = f": {subprocess_result.stderr}" if subprocess_result.stderr else ""

        raise RuntimeError(f"An error occurred while running CompAIRR{err_str}\n"
                           f"See the log file for more information: {args.compairr_log}")

    if os.path.getsize(args.pairs_file) == 0:
        raise RuntimeError("An error occurred while running CompAIRR: output pairs file is empty.\n"
                           f"See the log file for more information: {args.compairr_log}")

    return args.pairs_file

def export_cdr3(export_cdr3, output_file):
    with open(output_file, "w") as file:
        file.write(f"{export_cdr3}\n")

def make_tcrmatch_input_files(pairs_file, output_folder, chunk_size):
    IEDB_COLUMNS = ["trimmed_seq", "original_seq", "receptor_group", "epitopes", "source_organisms", "source_antigens"]
    COLUMN_ORDER = ["cdr3_aa_1", "original_seq_1", "receptor_group_1", "epitopes_1", "source_organisms_1", "source_antigens_1"]

    df = pd.read_csv(pairs_file, sep="\t", usecols=["cdr3_aa_1", "cdr3_aa_2", "original_seq_1", "receptor_group_1", "epitopes_1", "source_organisms_1", "source_antigens_1"], iterator=True, chunksize=chunk_size)

    existing_files = {}
    counter = 0

    for chunk in df:
        for user_cdr3, cdr3_chunk in chunk.groupby("cdr3_aa_2"):
            if user_cdr3 in existing_files:
                id = existing_files[user_cdr3]
                cdr3_chunk[COLUMN_ORDER].to_csv(f"{output_folder}/prefiltered_IEDB_{id}.tsv", sep="\t", mode="a", index=False, header=False)

            else:
                counter += 1
                existing_files[user_cdr3] = counter
                id = counter

                cdr3_chunk[COLUMN_ORDER].to_csv(f"{output_folder}/prefiltered_IEDB_{id}.tsv", sep="\t", index=False, header=IEDB_COLUMNS)
                export_cdr3(user_cdr3, f"{output_folder}/user_cdr3_{id}.tsv")

def run_tcrmatch_on_each_file(tcrmatch_input_path, tcrmatch_path, threshold, output_file_path):
    TCRMATCH_HEADER = "input_sequence\tmatch_sequence\tscore\treceptor_group\tepitope\tantigen\torganism\t"

    with open(output_file_path, "w") as output_file:
        output_file.write(TCRMATCH_HEADER + "\n")

        for iedb_file in tcrmatch_input_path.glob("prefiltered_IEDB_*.tsv"):
            id = iedb_file.stem.split("_")[-1]
            user_file = tcrmatch_input_path / f"user_cdr3_{id}.tsv"

            assert user_file.is_file(), f"Found iedb file {iedb_file} but not the matching user cdr3 file {user_file}."

            cmd_args = [str(tcrmatch_path), "-i", str(user_file), "-t", "1", "-d", str(iedb_file), "-s", str(threshold)]

            subprocess_result = subprocess.run(cmd_args, capture_output=True, text=True, check=True)

            if subprocess_result.stdout == "":
                err_str = f":{subprocess_result.stderr}"
                raise RuntimeError(f"An error occurred while running TCRMatch{err_str}\n"
                                   f"The following arguments were used: {' '.join(cmd_args)}")

            header, content = subprocess_result.stdout.split("\n", 1)

            assert header == TCRMATCH_HEADER, f"TCRMatch result does not contain the expected header.\n" \
                                                f"Expected header: {TCRMATCH_HEADER}\n" \
                                                f"Found instead: {header}\n" \
                                                f"The following arguments were used: {' '.join(cmd_args)}"

            output_file.write(content)

def main(args):
    pairs_file_path = create_pairs_file_with_compairr(args)

    tcrmatch_input_path = build_path(args.tmp_path / "tcrmatch_input")

    make_tcrmatch_input_files(pairs_file_path, tcrmatch_input_path, args.chunk_size)
    run_tcrmatch_on_each_file(tcrmatch_input_path, args.tcrmatch_path, args.threshold, args.output_file)

    if not args.keep_intermediate:
        shutil.rmtree(args.tmp_path)

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    main(args)