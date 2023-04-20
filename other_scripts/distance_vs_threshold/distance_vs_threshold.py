from pathlib import Path
import pandas as pd
import subprocess


def split_iedb_sequence_sets(iedb_file, out_folder):
    print("STEP: splitting iedb seq sets")
    iedb_sequences = pd.read_csv(iedb_file, usecols=["trimmed_seq"], sep="\t")
    iedb_sequences = iedb_sequences.drop_duplicates()
    iedb_sequences = iedb_sequences.sample(frac=1)
    iedb_sequences.rename(columns={"trimmed_seq": "cdr3_aa"}, inplace=True)

    half_idx = int(len(iedb_sequences) / 2)

    file1 = out_folder / "sequences1.tsv"
    file2 = out_folder / "sequences2.tsv"

    iedb_sequences[half_idx:].to_csv(str(file1), index=False)
    iedb_sequences[:half_idx].to_csv(str(file2), index=False)

    print("DONE: splitting iedb seq sets")
    return file1, file2

def match_with_compairr(seq_file1, seq_file2, out_folder, compairr_path="/storage/lonnekes/TCRMatch_CompAIRR/compairr/src/compairr"):
    print("STEP: match with compairr")

    pairs_path = out_folder / "pairs.txt"

    cmd_args = [str(compairr_path), str(seq_file1), str(seq_file2),
                "-m", "--pairs", str(pairs_path), "--cdr3", "-d", "5", "--distance",
                "--ignore-genes", "--ignore-counts"]

    subprocess_result = subprocess.run(cmd_args, capture_output=True, text=True, check=True)

    if not pairs_path.is_file():
        err_str = f": {subprocess_result.stderr}" if subprocess_result.stderr else ""
        raise RuntimeError(f"An error occurred while running CompAIRR{err_str}")

    print("DONE: match with compairr")

    return pairs_path

def single_pair_tcrmatch(seq1, seq2, tmp_folder, tcrmatch_path="/storage/lonnekes/TCRMatch_CompAIRR/TCRMatch/tcrmatch"):
    user_file = tmp_folder / "user_seq.tsv"
    iedb_file = tmp_folder / "iedb_seq.tsv"

    with open(user_file, "w") as file:
        file.write(f"{seq1}\n")

    with open(iedb_file, "w") as file:
        file.write(f"trimmed_seq\toriginal_seq\treceptor_group\tepitopes\tsource_organisms\tsource_antigens\n{seq2}\t\t\t\t\t\n")

    cmd_args = [str(tcrmatch_path), "-i", str(user_file), "-t", "1", "-d", str(iedb_file), "-s", "0"]

    subprocess_result = subprocess.run(cmd_args, capture_output=True, text=True, check=True)

    if subprocess_result.stdout == "":
        err_str = f":{subprocess_result.stderr}"
        raise RuntimeError(f"An error occurred while running TCRMatch{err_str}\n"
                           f"The following arguments were used: {' '.join(cmd_args)}")

    header, content = subprocess_result.stdout.split("\n", 1)

    TCRMATCH_HEADER = "input_sequence\tmatch_sequence\tscore\treceptor_group\tepitope\tantigen\torganism\t"
    assert header == TCRMATCH_HEADER, f"TCRMatch result does not contain the expected header.\n" \
                                      f"Expected header: {TCRMATCH_HEADER}\n" \
                                      f"Found instead: {header}\n" \
                                      f"The following arguments were used: {' '.join(cmd_args)}"

    return float(content.split("\t")[2])
def process_pairs_file(pairs_file, tmp_folder):
    print("STEP: process pairs file")

    df = pd.read_csv(pairs_file, sep="\t",
                     usecols=["cdr3_aa_1", "cdr3_aa_2", "distance"], chunksize=10000)

    max_count = 1000

    observed_pairs_of_given_dist = {i: 0 for i in range(1, 6)}

    rows = []

    for chunk in df:
        for index, row in chunk.iterrows():
            if observed_pairs_of_given_dist[row["distance"]] < max_count:
                row["val"] = single_pair_tcrmatch(row["cdr3_aa_1"], row["cdr3_aa_2"], tmp_folder, tcrmatch_path="/storage/lonnekes/TCRMatch_CompAIRR/TCRMatch/tcrmatch")
                rows.append(row)

                observed_pairs_of_given_dist[row["distance"]] += 1

        if all([val >= max_count for val in observed_pairs_of_given_dist.values()]):
            print("breaking outer chunk loop")
            break

    print("DONE: process pairs file")

    return pd.DataFrame(rows)



# iedb_file = Path("/Users/lonneke/PycharmProjects/tcrmatch_compairr/data/IEDB_data_small.tsv")
# folder = Path("/Users/lonneke/PycharmProjects/tcrmatch_compairr/other_scripts/distance_vs_threshold/working_dir")

iedb_file = Path("/storage/lonnekes/TCRMatch_CompAIRR/data/IEDB_data_small.tsv")
folder = Path("/storage/lonnekes/TCRMatch_CompAIRR/distance_vs_threshold/tmp")


seq_file1, seq_file2 = split_iedb_sequence_sets(iedb_file, folder)
pairs_file = match_with_compairr(seq_file1, seq_file2, folder)
distances_tcrmatch_df = process_pairs_file(pairs_file, folder)

distances_tcrmatch_df.to_csv(str(folder / "distances_tcrmatch_scores.tsv"), sep="\t", index=False)

