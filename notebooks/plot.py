""" plot file """

import pandas as pd
import plotly.express as px

# example: country, iso_alpha, value, population
df = pd.read_csv('/Users/joshpark/Documents/purdue/spring 2025/anth230/anth230-unessay/data/clean/ILO ratio.csv')

fig = px.choropleth(
    df,
    locations="ISO",
    color="ratio",
    hover_name="country",
    hover_data={
        "ratio": True,
        "ISO": False
    },
    projection="natural earth",  # or "mercator", etc.
    title="Women:men salary ratio"
)

# render in notebook or browser
fig.show()