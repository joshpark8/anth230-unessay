""" plot file """

import pandas as pd
import plotly.express as px

# example: country, iso_alpha, value, population
df = pd.DataFrame([
    ["United States", "USA", 123, 331002651],
    ["France",        "FRA",  45, 65273511],
    ["Japan",         "JPN",  78, 125960000],
    # … fill in your real data …
], columns=["country", "iso_alpha", "stat", "population"])

fig = px.choropleth(
    df,
    locations="iso_alpha",       # column with ISO‑A3 codes
    color="stat",                # which column to color‐scale
    hover_name="country",        # what shows up as the main hover title
    hover_data={
        "stat": True,            # show your “stat” value
        "population": ":,f",     # formatted population with commas
        "iso_alpha": False       # don’t show the iso code itself
    },
    projection="natural earth",  # or "mercator", etc.
    title="My World Data Map"
)

# render in notebook or browser
fig.show()