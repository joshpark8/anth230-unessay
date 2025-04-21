"""
Gender-based Income Inequality Dashboard
@author Josh Park
@class ANTH 23000 - Gender Across Cultures
@assignment UnEssay
@date Spring 2025
@school Purdue University
"""

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from scipy.stats import norm
import numpy as np

df = pd.read_csv("./data/clean/ILO_wide_ratio_no_outliers.csv")
df = df.dropna(subset=["F_usd", "M_usd"], how="all").copy()

df_latest = df.sort_values("year").groupby("ISO", as_index=False).last()

df2 = df_latest.rename(
    columns={
        "F_usd": "Female",
        "M_usd": "Male",
        "ratio_usd": "Income Ratio",
        "year": "Year",
    }
)

fig = px.choropleth(
    df2,
    locations="ISO",
    color="Income Ratio",
    hover_name="country",
    hover_data={"Income Ratio": ":.2f"},
    projection="natural earth",
    title="Global Sex-based Income Inequality Heatmap",
    color_continuous_scale=px.colors.sequential.Bluered,
)

fig.update_layout(
    margin=dict(l=0, r=0, t=30, b=0),
    coloraxis_colorbar=dict(
        # move to the left edge
        x=0.0,
        xanchor="left",
        # center vertically
        y=0.5,
        yanchor="middle",
        # sizing
        len=0.8,  # 80% of plot height
        thickness=12,  # bar width in px
        title="F/M Income Ratio",
        tickformat=".2f",
    ),
)
fig.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>F/M Average Income Ratio: %{z:.2f}<extra></extra>"
)

data = df["ratio_usd"].dropna()

mu, sigma = data.mean(), data.std()

x = np.linspace(data.min(), data.max(), 200)

y = norm.pdf(x, loc=mu, scale=sigma)

hist_vals, hist_edges = np.histogram(data, bins=30, density=True)

fig_norm = go.Figure()

fig_norm.add_trace(
    go.Bar(
        x=hist_edges[:-1],
        y=hist_vals,
        width=hist_edges[1] - hist_edges[0],
        name="Empirical density",
        opacity=0.6,
    )
)

fig_norm.add_trace(
    go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(color="red", width=2),
        name=f"Normal fit (μ={mu:.2f}, σ={sigma:.2f})",
    )
)
fig_norm.update_layout(
    title="Distribution of F/M Ratios with Normal Fit",
    xaxis_title="Ratio (USD)",
    yaxis_title="Density",
    legend=dict(
        title="", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
    ),
    margin=dict(l=40, r=20, t=40, b=40),
)

# Application
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        html.Div(
            style={"display": "flex", "width": "100%", "height": "80vh"},
            children=[
                # Map on the left
                html.Div(
                    dcc.Graph(
                        id="world-map",
                        figure=fig,
                        style={"height": "100%", "margin": 0, "padding": 0},
                        config={"responsive": True},
                    ),
                    style={"flex": 2, "margin": 0, "padding": 0},
                ),
                # Detail panel on the right
                html.Div(
                    style={
                        "flex": 1,
                        "display": "flex",
                        "flexDirection": "column",
                        "marginLeft": "1rem",
                    },
                    children=[
                        # Single shared country title
                        html.H2(
                            id="country-title",
                            children="Select a country",
                            style={"textAlign": "center", "margin": "0.5rem 0"},
                        ),
                        # Stacked vertically
                        dcc.Graph(
                            id="ratio-bar",
                            style={"width": "100%", "height": "80vh"},
                            config={"responsive": True},
                        ),
                        dcc.Graph(
                            id="time-series",
                            style={"width": "100%", "height": "80vh"},
                            config={"responsive": True},
                        ),
                        dcc.Graph(
                            id="labor-dist",
                            style={"width": "100%", "height": "80vh"},
                            config={"responsive": True},
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            dcc.Graph(
                id="ratio-dist",
                figure=fig_norm,
                style={
                    "width": "100%",
                    "height": "30vh",
                    "margin": "0",
                    "padding": "0",
                },
                config={"responsive": True},
            ),
            style={"width": "100%", "display": "block", "margin": "0", "padding": "0"},
        ),
    ]
)


@app.callback(
    Output("country-title", "children"),
    Output("time-series", "figure"),
    Output("ratio-bar", "figure"),
    Output("labor-dist", "figure"),
    Input("world-map", "clickData"),
)
def update_all_visuals(click_data):
    if not click_data:
        empty = go.Figure()
        return "Select a country", empty, empty, empty

    iso = click_data["points"][0]["location"]

    dff = df[df["ISO"] == iso].sort_values("year")
    country_name = dff["country"].iloc[0]

    dff2 = dff.rename(
        columns={
            "F_usd": "Female",
            "M_usd": "Male",
            "ratio_usd": "Income Ratio",
            "year": "Year",
        }
    )

    # ratio time series
    fig_ts = px.line(
        dff2,
        x="Year",
        y="Income Ratio",
        markers=True,
        title="F/M Income Ratio Over Time",
    )
    breaks_ = dff2[dff2["break"]]
    fig_ts.add_trace(
        go.Scatter(
            x=breaks_["Year"],
            y=breaks_["Income Ratio"],
            mode="markers",
            marker=dict(symbol="x", size=12, color="red"),
            name="Break in series",
        )
    )
    fig_ts.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title="Year",
        yaxis_title="F/M Wage Ratio",
        title_font_size=14,
        legend=dict(
            orientation="v",  # vertical legend
            x=0.98,  # near the right edge
            y=1.3,  # near the top edge
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.6)",
            borderwidth=0,
        ),
    )
    fig_ts.update_yaxes(fixedrange=True, title_font_size=12)

    # raw wage bar (USD)
    fig_bar = px.bar(
        dff2,
        x="Year",
        y=["Female", "Male"],
        barmode="group",
        title="Average Monthly Income by Sex Over Time (USD)",
    )
    fig_bar.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=dff2["Year"].astype(str).tolist(),
    )
    fig_bar.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title="Year",
        yaxis_title="Average Monthly Earnings",
        title_font_size=14,
        legend=dict(
            orientation="v",
            x=0.25,
            y=0.98,
            font={"size": 10},
            itemwidth=30,
            title="",
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.6)",
            borderwidth=0,
        ),
    )
    fig_bar.update_yaxes(fixedrange=True, title_font_size=12)

    # labor distribution pie chart
    latest = dff2["Year"].max()
    df_latest_ = dff2[dff2["Year"] == latest].iloc[0]

    fig_pie = px.pie(
        names=["Female", "Male"],
        values=[
            np.trunc(df_latest_["female_share"] * 10000) / 100,
            np.trunc(df_latest_["male_share"] * 10000) / 100,
        ],
        title=f"Labor distribution by sex ({latest})",
    )

    fig_pie.update_traces(textposition="inside", textinfo="label+percent")
    fig_pie.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        title_font_size=14,
        legend=dict(
            orientation="v",
            x=0.02,
            y=0.98,
            xanchor="left",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.6)",
        ),
    )
    fig_pie.update_yaxes(title_font_size=12)

    return country_name, fig_ts, fig_bar, fig_pie


if __name__ == "__main__":
    app.run(debug=True)
