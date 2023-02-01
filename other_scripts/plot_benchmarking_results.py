import sys
import argparse
from pathlib import Path
import pandas as pd
import plotly.express as px

pd.set_option('display.max_columns', None)
def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--time_folder", default="../benchmarking/time/")

    parsed_args = parser.parse_args(args)
    parsed_args.time_folder = Path(parsed_args.time_folder)

    return parsed_args

def get_info(folder_str):
    return {sub_str[0]: sub_str[1:] for sub_str in folder_str.split("_")}

def convert_elapsed_to_seconds(elapsed_str):
    time = 0

    split_time = elapsed_str.split(":")

    time += float(split_time[-1])

    if len(split_time) > 1:
        time += float(split_time[-2]) * 60
    if len(split_time) > 2:
        time += float(split_time[-3]) * 60 * 60
    if len(split_time) > 3:
        raise ValueError(f"Invalid: {elapsed_str}")

    return time

def process_time_file(time_file, prefix, keep=("elapsed", "maxrss")):
    output = {}

    with open(time_file, "r") as file:
        for line in file:
            if line == "\n":
                continue
            result_type, result_str = line.strip().split()

            if result_type in keep:
                if result_type == "elapsed":
                    result = convert_elapsed_to_seconds(result_str)
                elif result_type == "maxrss":
                    result = int(result_str)
                else:
                    result = result_str

                output[f"{prefix}_{result_type}"] = result

    return output

def get_setting_cols(df):
    setting_cols = ["r", "n", "t"]

    if "d" in df.columns:
        setting_cols.append("d")

    return setting_cols


def df_to_long(df):
    return pd.melt(df, id_vars=get_setting_cols(df), var_name="result_type", value_name="result_value")

def collapse_repetitions(df):
    # keep min, max, average

    groupby_cols = get_setting_cols(df) + ["result_type"]
    groupby_cols.remove("r")

    df = df.groupby(groupby_cols).agg({"result_value": ["mean", "min", "max"]}).reset_index()
    df.columns = ["".join(col) for col in df.columns]

    return df

def format_df(data):
    return collapse_repetitions(df_to_long(pd.DataFrame(data)))
def process_benchmark_folder(base_folder, keep=("elapsed", "maxrss")):
    data = []

    for folder in base_folder.glob("r*_n*_t*"):
        experiment_data = get_info(folder.stem)

        elapsed_total = 0
        maxrss_max = 0

        for time_file in folder.glob("*_time.txt"):
            prefix = time_file.stem.replace("_time", "")
            time_result = process_time_file(time_file, prefix=prefix, keep=keep)
            experiment_data.update(time_result)

            if f"elapsed" in keep:
                elapsed_total += time_result[f"{prefix}_elapsed"]

            if f"maxrss" in keep:
                maxrss_max = max(maxrss_max, time_result[f"{prefix}_maxrss"])

        experiment_data["pipeline_elapsed"] = elapsed_total
        experiment_data["pipeline_maxrss"] = maxrss_max

        data.append(experiment_data)

    df = format_df(data)
    df["pipeline"] = base_folder.stem

    return df


def merge_dfs_for_benchmarking_plot(comp_data, tcrm_data, to_benchmark="elapsed"):
    comp_data = comp_data.copy()
    comp_data["pipeline"] = comp_data["pipeline"] + "_d" + comp_data["d"]
    comp_data = comp_data.drop(columns=["d"])

    merged_data = pd.concat([comp_data, tcrm_data])

    return merged_data[merged_data["result_type"] == f"pipeline_{to_benchmark}"]

def format_time(df, time_type):
    assert time_type in ("seconds", "minutes")
    if time_type == "minutes":

        for col in ["result_valuemax", "result_valuemean", "result_valuemin"]:
            df[col] = df[col] / 60

def add_error(df):
    df["e_plus"] = df["result_valuemax"] - df["result_valuemean"]
    df["e_minus"] = df["result_valuemean"] - df["result_valuemin"]

def plot_elapsed_time_benchmarking(comp_data, tcrm_data, t="1", time_type="seconds"):
    df = merge_dfs_for_benchmarking_plot(comp_data, tcrm_data, to_benchmark="elapsed")
    df = df[df["t"] == t]

    format_time(df, time_type)
    add_error(df)

    df["pipeline"] = df["pipeline"].replace({"compairr_tcrmatch_d1": "CompAIRR with d=1 + TCRMatch",
                                             "compairr_tcrmatch_d2": "CompAIRR with d=2 + TCRMatch",
                                             "tcrmatch": "TCRMatch"})

    fig = px.line(df, x="n", y="result_valuemean", color="pipeline",
                  error_y="e_plus", error_y_minus="e_minus", log_y=False,
                  template="plotly_white",
                  labels={"result_valuemean": f"time ({time_type})",
                          "n": "number of user-input CDR3s"})

    fig.update_layout(font=dict(size=18))

    fig.show()


def breakdown_elapsed_time_compairr_pipeline(comp_data, t="1", time_type="seconds"):
    comp_data = comp_data[comp_data["t"] == t]
    comp_data = comp_data[comp_data["result_type"].isin(["compairr_elapsed", "tcrmatch_elapsed", "fileprocessing_elapsed"])]



    comp_data["result_type"] = comp_data["result_type"].replace({"compairr_elapsed": "CompAIRR",
                                                                 "tcrmatch_elapsed": "TCRMatch",
                                                                  "fileprocessing_elapsed": "File processing"})
    format_time(comp_data, time_type)
    add_error(comp_data)

    fig = px.bar(comp_data, x="n", y="result_valuemean", color="result_type",  barmode="stack",
                  template="plotly_white", facet_col="d",
                  labels={"time_durationmean": f"time ({time_type})",
                          "n": "number of user-input CDR3s"})

    fig.update_layout(font=dict(size=18))
    fig.show()


def make_all_plots(args):
    comp_data = process_benchmark_folder(args.time_folder / "compairr_tcrmatch")
    tcrm_data = process_benchmark_folder(args.time_folder / "tcrmatch")


    plot_elapsed_time_benchmarking(comp_data, tcrm_data, t="1", time_type="minutes")
    plot_elapsed_time_benchmarking(comp_data, tcrm_data, t="8", time_type="minutes")
    breakdown_elapsed_time_compairr_pipeline(comp_data, time_type="minutes")



if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    make_all_plots(args)