import plotly.express as px
from other_scripts.plot_benchmarking_results import convert_elapsed_to_seconds


df = {"solution": ["chunking + df export", "stringio", "chunking + write", "pandas no chunk", "awk"],
      "maxrss": [147000 / 1000, 463432 / 1000, 144236 / 1000, 342948 / 1000, 18804 / 1000],
      "minutes": [convert_elapsed_to_seconds("3:50.13") / 60,
               convert_elapsed_to_seconds("4:36.28") / 60,
               convert_elapsed_to_seconds("5:25.16") / 60,
               convert_elapsed_to_seconds("0:56.28") / 60,
               convert_elapsed_to_seconds("18:16.71") / 60]}

tcrmatch_maxrss = 190.87



fig = px.bar(df, x="solution", y="minutes",
             labels={"minutes": f"time (minutes)"})
fig.update_layout(font=dict(size=18))
fig.show()

fig = px.bar(df, x="solution", y="maxrss",
             labels={"maxrss": f"Max RSS (MB)"})
fig.add_hline(y=tcrmatch_maxrss)
fig.update_layout(font=dict(size=18))
fig.show()



df = {"chunksize": ["1.000", "10.000", "100.000", "1.000.000", "10.000.000", "no chunk"],
      "maxrss": [92228 / 1000, 103416 / 1000, 146148 / 1000, 337936 / 1000, 345868 / 1000, 342032 / 1000],
      "minutes": [convert_elapsed_to_seconds("14:18.64") / 60,
                  convert_elapsed_to_seconds("9:35.37") / 60,
                  convert_elapsed_to_seconds("3:46.94") / 60,
                  convert_elapsed_to_seconds("1:19.03") / 60,
                  convert_elapsed_to_seconds("0:55.21") / 60,
                  convert_elapsed_to_seconds("0:57.21") / 60]}

fig = px.bar(df, x="chunksize", y="minutes",
             labels={"minutes": f"time (minutes)"})
fig.update_layout(font=dict(size=18))
fig.show()

fig = px.bar(df, x="chunksize", y="maxrss",
             labels={"maxrss": f"Max RSS (MB)"})
fig.add_hline(y=tcrmatch_maxrss)
fig.update_layout(font=dict(size=18))

fig.show()