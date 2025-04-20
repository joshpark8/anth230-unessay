"""
Gender-based Income Inequality Dashboard
@author Josh Park
@class ANTH 23000 - Gender Across Cultures
@assignment UnEssay
@date Spring 2025
@school Purdue University
"""

import dash
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

df = pd.read_csv("./anth230-unessay/data/clean/ILO_ratio.csv")
df_no_outliers = pd.read_csv("./anth230-unessay/data/clean/ILO_ratio_no_outliers.csv")
df_latest = df.sort_values("year").groupby("ISO", as_index=False).last()


fig_map = px.choropleth(
    df_latest,
    locations="ISO",
    color="ratio",
    hover_name="country",
    hover_data={"ratio": ":.2f"},
    projection="natural earth",
    title="Latest F/M Ratio",
)
fig_map.update_layout(margin=dict(l=0, r=0, t=30, b=0))
fig_map.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>Ratio %{z:.2f}<extra></extra>"
)
# fig_map.update_geos(showframe=True, framecolor="black", framewidth=1)

empty = go.Figure().update_layout(margin=dict(l=0, r=0, t=30, b=0))

app = Dash(__name__)
app.layout = html.Div(
    [
        html.Div(  # time series
            style={"display": "flex", "alignItems": "flex-start"},
            children=[
                html.Div(
                    id="country-stats",
                    style={
                        "width": "20%",
                        "padding": "10px",
                        "backgroundColor": "#f9f9f9",
                        "border": "1px solid #ccc",
                        "borderRadius": "4px",
                        "marginRight": "1rem",
                    },
                    children="Click a country → stats will appear here",
                ),
                html.Div(
                    dcc.Graph(id="world-map", figure=fig_map, style={"height": "60vh"}),
                    style={"flex": 1},
                ),
            ],
        ),
        html.Div(  # pie chart
            style={"display": "flex", "gap": "1rem", "marginTop": "1rem"},
            children=[
                html.Div(dcc.Graph(id="time-series", figure=empty), style={"flex": 1}),
                html.Div(dcc.Graph(id="ratio-bar", figure=empty), style={"flex": 1}),
                html.Div(
                    dcc.Graph(id="labor-distribution", figure=empty), style={"flex": 1}
                ),
            ],
        ),
    ]
)


# Application
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.Div(
            [
                html.Label("Data:"),
                dcc.RadioItems(
                    id="data-toggle",
                    options=[
                        {"label": "All data", "value": "all"},
                        {"label": "No outliers", "value": "clean"},
                    ],
                    value="all",
                    labelStyle={"display": "inline-block", "margin-right": "1rem"},
                ),
            ],
            style={"padding": "1rem"},
        ),
        # Map on top
        html.Div(
            dcc.Graph(
                id="world-map",
                figure=fig_map,
                style={"height": "80vh", "margin": "0", "padding": "0"},
            ),
            style={"width": "80%", "display": "block", "margin": "0", "padding": "0"},
        ),
        # Bottom row: two graphs side by side
        html.Div(
            [
                html.Div(
                    dcc.Graph(
                        id="ratio-bar",
                        style={"height": "40vh", "margin": "0", "padding": "0"},
                    ),
                    style={"flex": 1, "margin": "0", "padding": "0"},
                ),
                html.Div(
                    dcc.Graph(id="labor-dist", style={"height": "40vh"}),
                    style={"flex": 1},
                ),
            ],
            style={
                "display": "flex",  # use flexbox
                "gap": "0.5rem",  # gap between graphs
                "marginTop": "0",  # eliminate any extra space above
            },
        ),
    ]
)


# Callbacks
@app.callback(
    Output("time-series", "figure"),
    Output("ratio-bar", "figure"),
    Output("labor-distribution", "figure"),
    Input("world-map", "clickData"),
    Input("data-toggle", "value"),
)
def update_all_visuals(click_data, toggle):
    dset = df_no_outliers if toggle == "clean" else df

    if not click_data:
        empty = go.Figure()
        return empty, empty, empty

    iso = click_data["points"][0]["location"]
    dff = dset[dset["ISO"] == iso].sort_values("year")

    # ratio time series
    fig_ts = px.line(
        dff,
        x="year",
        y="ratio",
        markers=True,
        title=f"{dff['country'].iloc[0]} — F/M Wage Ratio Over Time",
    )
    breaks_ = dff[dff["break"]]
    fig_ts.add_trace(
        go.Scatter(
            x=breaks_["year"],
            y=breaks_["ratio"],
            mode="markers",
            marker=dict(symbol="x", size=12, color="red"),
            name="Break in series",
        )
    )
    fig_ts.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title="Year",
        yaxis_title="F/M Wage Ratio",
    )
    fig_ts.update_yaxes(fixedrange=True)

    # raw wage bar
    fig_bar = px.bar(
        dff,
        x="year",
        y=["F", "M"],
        barmode="group",
        title=f"{dff['country'].iloc[0]} — Earnings by Sex Over Time",
    )
    fig_bar.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title="Year",
        yaxis_title="Average Monthly Earnings",
    )
    fig_bar.update_xaxes(type="category", categoryorder="category ascending")
    fig_bar.update_yaxes(fixedrange=True)

    # labor distribution pie chart
    latest = dff["year"].max()
    df_latest_ = dff[dff["year"] == latest].iloc[0]

    fig_pie = px.pie(
        names=["Female", "Male"],
        values=[
            np.trunc(df_latest_["female_share"] * 1000000) / 100,
            np.trunc(df_latest_["male_share"] * 1000000) / 100,
        ],
        title=f"{df_latest_['country']} labor distribution by sex ({latest})",
    )
    fig_pie.update_traces(textposition="inside", textinfo="label+percent")
    fig_pie.update_layout(margin=dict(l=0, r=0, t=30, b=0))

    return fig_ts, fig_bar, fig_pie


if __name__ == "__main__":
    app.run(debug=True)
