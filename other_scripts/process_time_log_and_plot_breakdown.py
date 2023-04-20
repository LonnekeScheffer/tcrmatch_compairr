from pathlib import Path

import pandas as pd

import plotly.express as px
pd.set_option('display.max_columns', None)

def breakdown_time(time_str):
    hours, minutes, seconds = time_str.split(":")

    time = float(seconds.replace(",", "."))
    time += int(minutes) * 60
    time += int(hours) * 60 * 60

    return time
def breakdown_line(line):
    date, time, info, stepdone, name = line.split(" ", maxsplit=4)

    return {"time": breakdown_time(time),
            "step_done": stepdone,
            "name": name.strip()}


def process_time_logfile(filename):
    # base_time = 0

    start_time_per_step = {}
    time_per_step = {}

    with open(filename, "r") as file:
        for line in file.readlines():
            line_info = breakdown_line(line)

            if line_info["step_done"] == "STEP:":
                start_time_per_step[line_info["name"]] = line_info["time"]
            elif line_info["step_done"] == "DONE:":
                time_per_step[line_info["name"]] = line_info["time"] - start_time_per_step[line_info["name"]]

    return time_per_step


def get_time_df_for_all_compairr_tcrmatch(compairr_tcrmatch_folder):
    data = {"r": [], "n": [], "p": [], "t": [], "d": [], "i": [], "step": [], "time": []}

    for logfile in compairr_tcrmatch_folder.glob("r1_n1e5_p1.0_*/log.txt"):
        r, n, p, t, d, i = logfile.parent.name.split("_")

        time_per_step = process_time_logfile(logfile)

        for _ in range(3):
            data["r"].append(r)
            data["n"].append(n)
            data["p"].append(p)
            data["t"].append(t)
            data["d"].append(d)
            data["i"].append(i)

        data["step"].extend(["CompAIRR", "file processing", "TCRMatch"])
        data["time"].extend([time_per_step["creating pairs file with CompAIRR"] / 60,
                             time_per_step["constructing TCRMatch input files"] / 60,
                             time_per_step["running TCRMatch on input files"] / 60])

    return pd.DataFrame(data)


def plot(df):
    groupby_cols = ["n", "p", "t", "d", "i", "step"]

    df = df.groupby(groupby_cols).agg({"time": ["mean", "min", "max"]}).reset_index()
    df.columns = ["".join(col) for col in df.columns]

    df["compairr_setting"] = df["d"].astype(str) + df["i"].astype(str)
    df["compairr_setting"] = df["compairr_setting"].replace({"d2i0": "<br>Differences: 2<br>indels: False",
                                                             "d1i1": "<br>Differences: 1<br>indels: True",
                                                             "d1i0": "<br>Differences: 1<br>indels: False"})
    df["t"] = df["t"].replace({"t1": 1, "t8": 8})

    fig = px.bar(df, x="n", y="timemean", color="step", barmode="group",
                 facet_col="compairr_setting", facet_row="t",
                 template="plotly_white",  # facet_col="compairr_setting",
                 # color_discrete_map=get_breakdown_color_map(),
                 category_orders={"step": ["CompAIRR", "file processing", "TCRMatch"]},
                 labels={"timemean": f"time (minutes)",
                         "n": "number of user-input CDR3s",
                         "t": "number of threads"})

    fig.update_layout(font=dict(size=20))

    fig.show()


compairr_tcrmatch_folder = Path("../benchmarking_results/benchmarking_v6/time/compairr_tcrmatch")
df = get_time_df_for_all_compairr_tcrmatch(compairr_tcrmatch_folder)
plot(df)
