import sys
import argparse
from pathlib import Path
import pandas as pd
import plotly.express as px

pd.set_option('display.max_columns', None)
def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--time_folder", default="../benchmark_results/time/")

    parsed_args = parser.parse_args(args)
    parsed_args.time_folder = Path(parsed_args.time_folder)

    return parsed_args

def get_info(folder_str):
    return {sub_str[0]: sub_str[1:] for sub_str in folder_str.split("_")}

def time_str_to_seconds(time_str):
    minutes, seconds = time_str.split("m")
    return int(minutes) * 60 + float(seconds[:-1])
def process_time_file(time_file, prefix, keep=("real")):
    output = {}

    with open(time_file, "r") as file:
        for line in file:
            if line == "\n":
                continue
            time_type, time_str = line.strip().split("\t")

            if time_type in keep:
                output[f"{prefix}_{time_type}"] = time_str_to_seconds(time_str)

    return output

def get_setting_cols(df):
    setting_cols = ["r", "n", "t"]

    if "d" in df.columns:
        setting_cols.append("d")

    return setting_cols



def df_to_long(df):
    return pd.melt(df, id_vars=get_setting_cols(df), var_name="time_type", value_name="time_duration")

def collapse_repetitions(df):
    # keep min, max, average

    groupby_cols = get_setting_cols(df) + ["time_type"]
    groupby_cols.remove("r")

    df = df.groupby(groupby_cols).agg({"time_duration": ["mean", "min", "max"]}).reset_index()
    df.columns = ["".join(col) for col in df.columns]

    return df

def format_df(data):
    return collapse_repetitions(df_to_long(pd.DataFrame(data)))
def process_benchmark_folder(base_folder):
    data = []

    for folder in base_folder.glob("r*_n*_t*"):
        experiment_data = get_info(folder.stem)

        realtime_total = 0
        for time_file in folder.glob("*_time.txt"):
            prefix = time_file.stem.replace("_time", "")
            time_result = process_time_file(time_file, prefix=prefix)
            experiment_data.update(time_result)

            if prefix != "fileprocessing":
                realtime_total += time_result[f"{prefix}_real"]

        experiment_data["pipeline_real"] = realtime_total

        data.append(experiment_data)

    df = format_df(data)
    df["pipeline"] = base_folder.stem

    return df


def merge_dfs_for_benchmarking_plot(comp_data, tcrm_data):
    comp_data = comp_data.copy()
    comp_data["pipeline"] = comp_data["pipeline"] + "_d" + comp_data["d"]
    comp_data = comp_data.drop(columns=["d"])

    merged_data = pd.concat([comp_data, tcrm_data])

    return merged_data[merged_data["time_type"] == "pipeline_real"]

def format_time(df, time_type):
    assert time_type in ("seconds", "minutes")
    if time_type == "minutes":
        df["time_durationmax"] = df["time_durationmax"] / 60
        df["time_durationmean"] = df["time_durationmean"] / 60
        df["time_durationmin"] = df["time_durationmin"] / 60

def add_error(df):
    df["e_plus"] = df["time_durationmax"] - df["time_durationmean"]
    df["e_minus"] = df["time_durationmean"] - df["time_durationmin"]

def plot_benchmarking(comp_data, tcrm_data, t="1", time_type="seconds"):
    df = merge_dfs_for_benchmarking_plot(comp_data, tcrm_data)
    df = df[df["t"] == t]

    format_time(df, time_type)
    add_error(df)

    df["pipeline"] = df["pipeline"].replace({"compairr_tcrmatch_d1": "CompAIRR with d=1 + TCRMatch",
                                             "compairr_tcrmatch_d2": "CompAIRR with d=2 + TCRMatch",
                                             "tcrmatch": "TCRMatch"})

    fig = px.line(df, x="n", y="time_durationmean", color="pipeline",
                  error_y="e_plus", error_y_minus="e_minus", log_y=False,
                  template="plotly_white",
                  labels={"time_durationmean": f"time ({time_type})",
                          "n": "number of user-input CDR3s"})

    fig.update_layout(font=dict(size=18))

    fig.show()


def breakdown_compairr_pipeline(comp_data, t="1", time_type="seconds"):
    comp_data = comp_data[comp_data["t"] == t]
    comp_data = comp_data[comp_data["time_type"] != "pipeline_real"]

    comp_data["time_type"] = comp_data["time_type"].replace({"compairr_real": "CompAIRR",
                                                             "tcrmatch_real": "TCRMatch",
                                                             "fileprocessing_real": "File processing"})

    format_time(comp_data, time_type)
    add_error(comp_data)

    print(comp_data)

    fig = px.bar(comp_data, x="n", y="time_durationmean", color="time_type",  barmode="stack",
                  template="plotly_white", facet_col="d",
                  labels={"time_durationmean": f"time ({time_type})",
                          "n": "number of user-input CDR3s"})

    fig.update_layout(font=dict(size=18))
    fig.show()


def do(args):
    comp_data = process_benchmark_folder(args.time_folder / "compairr_tcrmatch")
    tcrm_data = process_benchmark_folder(args.time_folder / "tcrmatch")


    plot_benchmarking(comp_data, tcrm_data, t="1", time_type="minutes")
    plot_benchmarking(comp_data, tcrm_data, t="8", time_type="minutes")
    breakdown_compairr_pipeline(comp_data, time_type="minutes")




if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    do(args)