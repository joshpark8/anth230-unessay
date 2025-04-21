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
        "ratio": "Income Ratio",
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

data = df["ratio"].dropna()

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
            style={"display": "flex", "width": "95%", "height": "80vh"},
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
                        # "marginLeft": "1rem",
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
            "ratio": "Income Ratio",
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

    # raw wage bar (USD) with width scaled to year gaps
    years = dff2["Year"].tolist()
    female_vals = dff2["Female"].tolist()
    male_vals = dff2["Male"].tolist()

    # cap each bar to a maximum half-width (years)
    max_half_width = 0.5
    # compute bar widths: half the gap to neighboring data-year
    widths = []
    n = len(years)
    for i, y_ in enumerate(years):
        if n == 1:
            gap = 1
        elif i == 0:
            gap = (years[1] - y_) / 2
        elif i == n - 1:
            gap = (y_ - years[-2]) / 2
        else:
            gap = min(y_ - years[i - 1], years[i + 1] - y_) / 2
        widths.append(min(gap, max_half_width))

    # compute x-offsets so female and male bars sit side by side
    female_x = [y - w / 2 for y, w in zip(years, widths)]
    male_x = [y + w / 2 for y, w in zip(years, widths)]
    # build the bar chart
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(x=female_x, y=female_vals, width=widths, name="Female"))
    fig_bar.add_trace(go.Bar(x=male_x, y=male_vals, width=widths, name="Male"))

    # determine axis labels
    min_year = int(dff2["Year"].min())
    max_year = int(dff2["Year"].max())
    full_years = list(range(min_year, max_year + 1))
    # reduce tick density if too many years
    num_years = len(full_years)
    max_ticks = 10
    interval = max(1, num_years // max_ticks)
    tick_years = full_years[::interval]

    # numeric x-axis with gaps
    fig_bar.update_xaxes(
        type="linear",
        tickmode="array",
        tickvals=tick_years,
        ticktext=[str(y) for y in tick_years],
        tickangle=45,
        range=[min_year - 0.5, max_year + 0.5],
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

    # add vertical lines at break years, shifted halfway
    for yr in dff2.loc[dff2["break"], "Year"]:
        fig_bar.add_vline(
            x=yr + 0.5,
            line_width=1,
            line_dash="dash",
            line_color="red",
            annotation_text="Break",
            annotation_position="top right",
            annotation_font_size=10,
        )

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
