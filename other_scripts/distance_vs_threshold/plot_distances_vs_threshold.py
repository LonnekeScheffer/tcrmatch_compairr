import pandas as pd
import plotly.express as px


df = pd.read_csv("/Users/lonneke/PycharmProjects/tcrmatch_compairr/other_scripts/distance_vs_threshold/results/distances_tcrmatch_scores.tsv", sep="\t")
df_indels = pd.read_csv("/Users/lonneke/PycharmProjects/tcrmatch_compairr/other_scripts/distance_vs_threshold/results/distances_tcrmatch_scores_indels.tsv", sep="\t")
df_indels["distance"] = "1 indel"

df_c = pd.concat([df, df_indels])

fig = px.violin(df_c, x="distance", y="val", box=True,
                category_orders={"distance": ["1", "1 indel", "2", "3", "4", "5"]},
                labels={"val": "TCRMatch score"},
                template="plotly_white")
fig.update_xaxes(type='category')

fig.add_hline(y=0.97, line_dash="dash", line_color="gray")

fig.update_layout(font=dict(size=30))
fig.show()
