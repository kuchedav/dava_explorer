import plotly.express as px
import polars as pl
from dash import callback
from dash import Dash
from dash import dcc
from dash import html
from dash import Input
from dash import Output


def analyze_table(df):

    external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

    app = Dash(__name__, external_stylesheets=external_stylesheets)

    df = df.to_pandas()

    app.layout = html.Div(
        [
            ############################################################################
            # Example from https://dash.plotly.com/interactive-graphing
            ############################################################################
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Dropdown(
                                df["Indicator Name"].unique(),
                                "Fertility rate, total (births per woman)",
                                id="crossfilter-xaxis-column",
                            ),
                            dcc.RadioItems(
                                ["Linear", "Log"],
                                "Linear",
                                id="crossfilter-xaxis-type",
                                labelStyle={
                                    "display": "inline-block",
                                    "marginTop": "5px",
                                },
                            ),
                        ],
                        style={"width": "49%", "display": "inline-block"},
                    ),
                    html.Div(
                        [
                            dcc.Dropdown(
                                df["Indicator Name"].unique(),
                                "Life expectancy at birth, total (years)",
                                id="crossfilter-yaxis-column",
                            ),
                            dcc.RadioItems(
                                ["Linear", "Log"],
                                "Linear",
                                id="crossfilter-yaxis-type",
                                labelStyle={
                                    "display": "inline-block",
                                    "marginTop": "5px",
                                },
                            ),
                        ],
                        style={
                            "width": "49%",
                            "float": "right",
                            "display": "inline-block",
                        },
                    ),
                ],
                style={"padding": "10px 5px"},
            ),
            html.Div(
                [
                    dcc.Graph(
                        id="crossfilter-indicator-scatter",
                        hoverData={"points": [{"customdata": "Japan"}]},
                    )
                ],
                style={"width": "49%", "display": "inline-block", "padding": "0 20"},
            ),
            html.Div(
                [
                    dcc.Graph(id="x-time-series"),
                    dcc.Graph(id="y-time-series"),
                ],
                style={"display": "inline-block", "width": "49%"},
            ),
            html.Div(
                dcc.Slider(
                    df["Year"].min(),
                    df["Year"].max(),
                    step=None,
                    id="crossfilter-year--slider",
                    value=df["Year"].max(),
                    marks={str(year): str(year) for year in df["Year"].unique()},
                ),
                style={"width": "49%", "padding": "0px 20px 20px 20px"},
            ),
            ############################################################################
            html.Div(dcc.Graph(id="Value-histogram")),
            html.Div(dcc.Graph(id="Year-histogram")),
        ]
    )

    @callback(
        Output("crossfilter-indicator-scatter", "figure"),
        Input("crossfilter-xaxis-column", "value"),
        Input("crossfilter-yaxis-column", "value"),
        Input("crossfilter-xaxis-type", "value"),
        Input("crossfilter-yaxis-type", "value"),
        Input("crossfilter-year--slider", "value"),
    )
    def update_graph(
        xaxis_column_name, yaxis_column_name, xaxis_type, yaxis_type, year_value
    ):
        dff = df[df["Year"] == year_value]

        fig = px.scatter(
            x=dff[dff["Indicator Name"] == xaxis_column_name]["Value"],
            y=dff[dff["Indicator Name"] == yaxis_column_name]["Value"],
            hover_name=dff[dff["Indicator Name"] == yaxis_column_name]["Country Name"],
        )

        fig.update_traces(
            customdata=dff[dff["Indicator Name"] == yaxis_column_name]["Country Name"]
        )

        fig.update_xaxes(
            title=xaxis_column_name, type="linear" if xaxis_type == "Linear" else "log"
        )

        fig.update_yaxes(
            title=yaxis_column_name, type="linear" if yaxis_type == "Linear" else "log"
        )

        fig.update_layout(
            margin={"l": 40, "b": 40, "t": 10, "r": 0}, hovermode="closest"
        )

        return fig

    def create_time_series(dff, axis_type, title):

        fig = px.scatter(dff, x="Year", y="Value")

        fig.update_traces(mode="lines+markers")

        fig.update_xaxes(showgrid=False)

        fig.update_yaxes(type="linear" if axis_type == "Linear" else "log")

        fig.add_annotation(
            x=0,
            y=0.85,
            xanchor="left",
            yanchor="bottom",
            xref="paper",
            yref="paper",
            showarrow=False,
            align="left",
            text=title,
        )

        fig.update_layout(height=225, margin={"l": 20, "b": 30, "r": 10, "t": 10})

        return fig

    @callback(
        Output("x-time-series", "figure"),
        Input("crossfilter-indicator-scatter", "hoverData"),
        Input("crossfilter-xaxis-column", "value"),
        Input("crossfilter-xaxis-type", "value"),
    )
    def update_x_timeseries(hoverData, xaxis_column_name, axis_type):
        country_name = hoverData["points"][0]["customdata"]
        dff = df[df["Country Name"] == country_name]
        dff = dff[dff["Indicator Name"] == xaxis_column_name]
        title = f"<b>{country_name}</b><br>{xaxis_column_name}"
        return create_time_series(dff, axis_type, title)

    @callback(
        Output("y-time-series", "figure"),
        Input("crossfilter-indicator-scatter", "hoverData"),
        Input("crossfilter-yaxis-column", "value"),
        Input("crossfilter-yaxis-type", "value"),
    )
    def update_y_timeseries(hoverData, yaxis_column_name, axis_type):
        dff = df[df["Country Name"] == hoverData["points"][0]["customdata"]]
        dff = dff[dff["Indicator Name"] == yaxis_column_name]
        return create_time_series(dff, axis_type, yaxis_column_name)

    @callback(
        Output("Value-histogram", "figure"),
        Input("Year-histogram", "figure"),
    )
    def numeric_chart_1():
        nbins = 10
        fig = px.histogram(df, x="Value", nbins=nbins, title="Histogram of Value")
        fig.update_layout(bargap=0.1)
        return dcc.Graph(figure=fig)

    @callback(
        Output("Year-histogram", "figure"),
        Input("Value-histogram", "figure"),
    )
    def numeric_chart_2():
        nbins = 10
        fig = px.histogram(df, x="Year", nbins=nbins, title="Histogram of Year")
        fig.update_layout(bargap=0.1)
        return dcc.Graph(figure=fig)

    app.run(debug=True)


if __name__ == "__main__":

    df = pl.read_csv("./src/dava_explorer/country_indicators.csv")

    analyze_table(df)
