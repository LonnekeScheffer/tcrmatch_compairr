import sys
import argparse
from pathlib import Path
import pandas as pd
import plotly.express as px

pd.set_option('display.max_columns', None)

def parse_args(args):
    parser = argparse.ArgumentParser()
    # parser.add_argument("--time_folder", default="/Users/lonneke/PycharmProjects/tcrmatch_compairr/benchmarking_tcrmatchtrheads/benchmarking_v5_t1/time")
    parser.add_argument("--time_folder", default="../benchmarking_results/benchmarking_v6_failed/time/")
    # parser.add_argument("--time_folder", default="../comparing_pipelines/benchmarking_v1/time/")

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

            try:
                result_type, result_str = line.strip().split()
            except ValueError:
                raise ValueError(f"Found unexpected line: {line} in the file {time_file}")

            if result_type in keep:
                if result_type == "elapsed":
                    result = convert_elapsed_to_seconds(result_str)
                elif result_type == "maxrss":
                    result = int(result_str) / 1000
                else:
                    result = result_str

                output[f"{prefix}_{result_type}"] = result

    assert len(output) > 0, f"Error when processing time file {time_file} (could the file be empty?)"

    return output

def get_setting_cols(df):
    setting_cols = ["r", "n", "p", "t"]

    if "d" in df.columns:
        setting_cols.append("d")

    if "i" in df.columns:
        setting_cols.append("i")

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

    for folder in base_folder.glob("r*_n*_p*_t*"):
        experiment_data = get_info(folder.name)

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
    df["pipeline"] = base_folder.name

    return df


def merge_dfs_for_benchmarking_plot(comp_data, tcrm_data, to_benchmark="elapsed"):
    comp_data = comp_data.copy()
    comp_data["pipeline"] = comp_data["pipeline"] + "_d" + comp_data["d"] + "_i" + comp_data["i"]
    comp_data = comp_data.drop(columns=["d", "i"])

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

def update_pipeline_name(df):
    df["pipeline"] = df["pipeline"].replace({"compairr_tcrmatch_d1_i0": "CompAIRR with d=1, no indels + TCRMatch",
                                             "compairr_tcrmatch_d1_i1": "CompAIRR with d=1, with indels + TCRMatch",
                                             "compairr_tcrmatch_d2_i0": "CompAIRR with d=2, no indels + TCRMatch",
                                             "tcrmatch": "TCRMatch"})

def get_pipeline_color_map():
    return {"CompAIRR with d=1, no indels + TCRMatch": "#F7CD55",
            "CompAIRR with d=1, with indels + TCRMatch": "#FF9853",
            "CompAIRR with d=2, no indels + TCRMatch": "#F05452",
            "TCRMatch": "#58A7B7"}

def get_breakdown_color_map():
    return {"CompAIRR": "#F7CD55",
            "File processing": "#FF9853",
            "TCRMatch": "#58A7B7"}

def update_n_sequences(df):
    df["n"] = df["n"].replace({"1e2": "100", "1e3": "1.000", "1e4": "10.000", "1e5": "100.000", "1e6": "1.000.000"})

def update_percentage(df):
    df["p"] = df["p"].replace({"0.1": "0.1%", "1.0": "1%", "10.0": "10%", "100.0": "100%"})

def keep_selected(df, t=None, p=None, d=None, n=None):
    for value, name in [(t, "t"), (p, "p"), (d, "d"), (n, "n")]:
        if value is not None:
            assert value in set(df[name]), f"Tried to subset {name} to only value {value}, but found only the following values in the df: {set(df[name])}"
            df = df[df[name] == value]

    return df

def plot_elapsed_time_benchmarking(comp_data, tcrm_data, t=None, p="1.0", time_type="seconds",
                                   facet_col="t", facet_row=None, same_y=False):
    df = merge_dfs_for_benchmarking_plot(comp_data, tcrm_data, to_benchmark="elapsed")

    df = keep_selected(df, t=t, p=p)
    # df = df[df["t"] == t]
    # df = df[df["p"] == p]
    # df = df[df["n"] != "1e5"]

    format_time(df, time_type)
    add_error(df)
    update_pipeline_name(df)
    update_n_sequences(df)

    fig = px.line(df, x="n", y="result_valuemean", color="pipeline",
                  facet_col=facet_col, facet_row=facet_row,
                  error_y="e_plus", error_y_minus="e_minus", log_y=False,
                  template="plotly_white", #range_y=[0, 40],
                  color_discrete_map=get_pipeline_color_map(),
                  labels={"result_valuemean": f"time ({time_type})",
                          "n": "number of user-input CDR3s",
                          "t": "number of threads"})

    fig.update_layout(font=dict(size=18))

    if not same_y:
        fig.update_yaxes(matches=None)
        fig.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True))

    fig.show()


def plot_time_per_percentage(comp_data, tcrm_data, t=None, n="1e5", time_type="seconds",
                             facet_col="t"):
    df = merge_dfs_for_benchmarking_plot(comp_data, tcrm_data, to_benchmark="elapsed")
    df = keep_selected(df, t=t, n=n)

    format_time(df, time_type)
    add_error(df)
    update_pipeline_name(df)
    update_percentage(df)
    # update_n_sequences(df)

    fig = px.line(df, x="p", y="result_valuemean", color="pipeline",
                  error_y="e_plus", error_y_minus="e_minus", log_y=False,
                  template="plotly_white", facet_col=facet_col,
                  color_discrete_map=get_pipeline_color_map(),
                  labels={"result_valuemean": f"time ({time_type})",
                          "p": "Percentage of IEDB sequences",
                          "t": "number of threads"})

    fig.update_layout(font=dict(size=18))
    fig.update_yaxes(matches=None)
    fig.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True))

    fig.show()

def breakdown_elapsed_time_compairr_pipeline(comp_data, p="1.0", t=None, d=None, time_type="seconds",
                                             facet_col="compairr_setting", facet_row="t"):
    comp_data = keep_selected(comp_data, t=t, p=p, d=d)

    result_types_to_keep = [result_type for result_type in set(comp_data["result_type"]) if result_type.endswith("_elapsed") and result_type != "pipeline_elapsed"]
    comp_data = comp_data[comp_data["result_type"].isin(result_types_to_keep)]

    comp_data["compairr_setting"] = "d=" + comp_data["d"] + ", i=" + comp_data["i"]

    comp_data["result_type"] = comp_data["result_type"].replace({"compairr_elapsed": "CompAIRR",
                                                                 "tcrmatch_elapsed": "TCRMatch",
                                                                  "fileprocessing_elapsed": "File processing"})
    format_time(comp_data, time_type)
    update_n_sequences(comp_data)
    add_error(comp_data)

    fig = px.bar(comp_data, x="n", y="result_valuemean", color="result_type",  barmode="stack",
                 facet_col=facet_col, facet_row=facet_row,
                  template="plotly_white", #facet_col="compairr_setting",
                 color_discrete_map=get_breakdown_color_map(),
                  labels={"result_valuemean": f"time ({time_type})",
                          "n": "number of user-input CDR3s",
                          "t": "number of threads"})

    fig.update_layout(font=dict(size=18))
    fig.show()

def plot_max_rss_benchmarking(comp_data, tcrm_data, p="1.0", facet_col="t"):
    df = merge_dfs_for_benchmarking_plot(comp_data, tcrm_data, to_benchmark="maxrss")
    df = keep_selected(df, p=p)

    add_error(df)
    update_pipeline_name(df)
    update_n_sequences(df)

    fig = px.line(df, x="n", y="result_valuemean", color="pipeline", facet_col=facet_col,
                  error_y="e_plus", error_y_minus="e_minus", log_y=False,
                  color_discrete_map=get_pipeline_color_map(),
                  template="plotly_white",
                  labels={"result_valuemean": f"Max RSS (MB)",
                          "n": "number of user-input CDR3s",
                          "t": "number of threads"})

    fig.update_layout(font=dict(size=18),)

    fig.show()

def breakdown_maxrss_compairr_pipeline(comp_data, p="1.0", t=None, d=None,
                                       facet_col="compairr_setting", facet_row="t"):
    comp_data = keep_selected(comp_data, t=t, p=p, d=d)

    comp_data = comp_data[comp_data["result_type"].isin(["compairr_maxrss", "tcrmatch_maxrss", "fileprocessing_maxrss"])]

    comp_data["compairr_setting"] = "d=" + comp_data["d"] + ", i=" + comp_data["i"]

    comp_data["result_type"] = comp_data["result_type"].replace({"compairr_maxrss": "CompAIRR",
                                                                 "tcrmatch_maxrss": "TCRMatch",
                                                                  "fileprocessing_maxrss": "File processing"})
    update_n_sequences(comp_data)
    add_error(comp_data)

    fig = px.bar(comp_data, x="n", y="result_valuemean", color="result_type",  barmode="group",
                 facet_col=facet_col, facet_row=facet_row,
                 template="plotly_white",
                 color_discrete_map=get_breakdown_color_map(),
                 labels={"result_valuemean": f"Max RSS (MB)",
                          "n": "number of user-input CDR3s",
                          "t": "number of threads"})

    fig.update_layout(font=dict(size=18))
    fig.show()

def make_all_plots(args):
    # todo setting for deconstructed vs combined


    comp_data = process_benchmark_folder(args.time_folder / "compairr_tcrmatch")
    tcrm_data = process_benchmark_folder(args.time_folder / "tcrmatch")

    plot_elapsed_time_benchmarking(comp_data, tcrm_data, time_type="minutes")

    plot_time_per_percentage(comp_data, tcrm_data, n="1e2", time_type="minutes")
    # plot_time_per_percentage(comp_data, tcrm_data, n="1e5", time_type="minutes")

    breakdown_elapsed_time_compairr_pipeline(comp_data, time_type="minutes")
    breakdown_elapsed_time_compairr_pipeline(comp_data, time_type="minutes", d="2", facet_col="t", facet_row=None)

    plot_max_rss_benchmarking(comp_data, tcrm_data, p="1.0")

    breakdown_maxrss_compairr_pipeline(comp_data)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    make_all_plots(args)