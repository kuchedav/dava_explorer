import dash
import dash_table
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc
from dash import html
from dash import Input
from dash import Output
from dash import State

# Sample data
data = {
    "Category": ["A", "B", "A", "B", "A", "B", "A", "B"],
    "Value": [10, 20, 15, 20, 30, 40, 25, 20],
}
df = pd.DataFrame(data)

# Create Dash app
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H1("Interactive Histogram with Filtering"),
        # Histogram
        dcc.Graph(id="histogram"),
        # Data table
        dash_table.DataTable(
            id="data-table",
            columns=[{"name": col, "id": col} for col in df.columns],
            page_size=10,
        ),
        # Store for selected bins
        dcc.Store(id="selected-bins", data=[]),
    ]
)


@app.callback(
    Output("selected-bins", "data"),
    [Input("histogram", "clickData")],
    [State("selected-bins", "data")],
)
def update_selected_bins(clickData, selected_bins):
    if clickData and "points" in clickData and len(clickData["points"]) > 0:
        selected_bin_range = clickData["points"][0]["x"]
        if selected_bin_range not in selected_bins:
            selected_bins.append(selected_bin_range)
        else:
            selected_bins.remove(selected_bin_range)
    return selected_bins


@app.callback(
    [Output("histogram", "figure"), Output("data-table", "data")],
    [Input("selected-bins", "data")],
)
def update_graph_and_table(selected_bins):
    # Define bin edges
    bin_edges = np.histogram_bin_edges(df["Value"], bins=6)

    # Filter data based on selected bins
    if selected_bins:

        def filter_df(df, selected_bin):
            max_boudry = bin_edges[bin_edges >= selected_bin].min()
            min_boudry = bin_edges[bin_edges <= selected_bin].max()
            filtered_df = df[(df["Value"] < max_boudry) & (df["Value"] >= min_boudry)]
            return filtered_df

        filtered_df = pd.concat(
            [filter_df(df, selected_bin) for selected_bin in selected_bins]
        )
    else:
        filtered_df = df

    # Create base histogram (gray)
    base_hist = go.Histogram(
        x=df["Value"],
        xbins=dict(
            start=bin_edges[0], end=bin_edges[-1], size=(bin_edges[1] - bin_edges[0])
        ),
        marker_color="gray",
        opacity=0.5,
        name="All Data",
    )

    # Create filtered histogram (blue)
    filtered_hist = go.Histogram(
        x=filtered_df["Value"],
        xbins=dict(
            start=bin_edges[0], end=bin_edges[-1], size=(bin_edges[1] - bin_edges[0])
        ),
        marker_color="blue",
        opacity=0.7,
        name="Filtered Data",
    )

    # Combine histograms
    fig = go.Figure(data=[base_hist, filtered_hist])
    fig.update_layout(title="Value Distribution", barmode="overlay")

    return fig, filtered_df.to_dict("records")


if __name__ == "__main__":
    app.run_server()
