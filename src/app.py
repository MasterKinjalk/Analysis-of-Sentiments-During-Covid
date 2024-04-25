from dash import callback_context
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from worldmap import create_choropleth_map, dates
import dash
from playback_slider_aio import PlaybackSliderAIO
from line_plot import plot_global_emotions, plot_country_emotions, important_dates_dict
import dash_bootstrap_components as dbc
import calendar
import pandas as pd

from stacked_graph import plot_stacked_country_emotions, plot_stacked_global_emotions
from cumulative_graph import (
    plot_cumulative_country_emotions,
    plot_cumulative_global_emotions,
)
from datetime import datetime


app = dash.Dash(
    __name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME]
)


server = app.server


# Create marks for the slider without displaying labels (empty strings)

# but the tooltip will display the actual date

# Create marks for the slider with actual dates in the tooltip

# date_marks = {i: {'label': '', 'style': {'display': 'none'}, 'tooltip': date} for i, date in enumerate(dates)}

date_marks = {}


# important_dates_dict = {'January10': 'Novel coronavirus announced', 'March11': 'WHO announces Pandemic', 'September23': 'New strain of Covid', 'October2': 'Trump infected'}
# important_dates_dict = {'2020-02-11': 'WHO names Covid-19','2020-03-11': 'WHO declares pandemic', '2020-04-02': 'Worldwide cases at 1 million', '2020-04-08': 'Wuhan reopens', '2020-04-13': 'US ceases WHO funding','2020-04-17': 'First Moderna trials', '2020-04-24': 'ACT-A announced',  '2020-09-23': 'New strain of Covid', '2020-09-28': 'Global deaths at 1 million', '2020-10-02': 'Trump infected'}

print(type(dates[0]))

for i, date in enumerate(dates):

    curr_label = ""
    curr_style = {"display": "none"}
    if date.day == 1:
        curr_label = calendar.month_name[date.month]
        curr_style = {"display": "block"}

    elif date.strftime("%Y-%m-%d") in important_dates_dict:
        curr_label = important_dates_dict[date.strftime("%Y-%m-%d")]
        curr_style = {
            "display": "block",
            "transform": "rotate(-45deg) translateY(-3rem)",
        }

    date_marks[i] = {"label": curr_label, "style": curr_style}


# Initialize the slider

app.layout = html.Div(
    [
        html.Div(
            [
                dbc.Modal(
                    [
                        dbc.ModalHeader(html.H4("Disclaimer")),
                        dbc.ModalBody(
                            [
                                html.H5(
                                    "No personally identifiable information (PII):"
                                ),
                                html.P(
                                    "This visualization does not store or display any personally identifiable information. Our aim is to respect privacy and maintain the confidentiality of all individuals."
                                ),
                                html.H5("Purpose of the Visualization:"),
                                html.P(
                                    "The visualization is intended solely for informational purposes. It is not designed to foster or encourage prejudice against any residents of specific countries or regions. Our goal is to provide clear, unbiased information to help users understand trends and patterns, not to facilitate judgments or biases."
                                ),
                                html.H5("Data Representation and Bias:"),
                                html.P(
                                    "Please be aware that the data presented may reflect inherent biases due to varying levels of Twitter usage across different countries or regions. Consequently, regions with higher Twitter activity may appear disproportionately represented. This does not necessarily indicate actual levels of COVID-19 activity but rather the volume of discussion surrounding it on this platform."
                                ),
                                html.H5("Ethical Use of Data:"),
                                html.P(
                                    "We are committed to the ethical use of data. It is crucial that this visualization is used in a manner that does not contribute to misinformation or stigmatize any countries or regions. We urge all users to consider the context and limitations of the data when interpreting this visualization. Misinterpretations that could lead to misinformation or discrimination are strongly discouraged."
                                ),
                                html.H5("Limitations of Data:"),
                                html.P(
                                    "Users should be aware of the limitations inherent in this data, which is sourced from publicly available Twitter posts. The insights derived are not definitive medical or scientific data and should be viewed as indicative rather than conclusive."
                                ),
                                html.H5("Changes and Updates:"),
                                html.P(
                                    "The information in this visualization is subject to change and may be updated periodically to reflect new data or corrections. We encourage users to check back regularly for the most current information."
                                ),
                                html.B(
                                    "By using this visualization, you acknowledge your understanding and agreement to these terms."
                                ),
                            ]
                        ),
                        dbc.ModalFooter(
                            dbc.Button(
                                "I acknowledge.",
                                id="consent-button",
                                color="primary",
                                className="ml-auto",
                            )
                        ),
                    ],
                    id="modal",
                    size="xl",
                    centered=True,
                    is_open=True,
                ),
                html.H1(
                    "Visualizing Global Emotions for 2020 Through Covid-19 Tweets",
                    id="page-title",
                    style={"color": "#89a2cc", "font-size": "50px"},
                ),
            ],
            style={"display": "flex", "justify-content": "center"},
        ),
        html.Div(
            [
                html.Hr(
                    style={
                        "border-top": "1px solid #ccc",
                        "margin": "20px 0px",
                        "background-color": "#1d3a69",
                        "height": "75px",
                        "width": "100%",
                    }
                ),
                #   html.Hr(style={'height':'20px'}),
            ]
        ),
        PlaybackSliderAIO(
            aio_id="date-slider",
            slider_props={
                "min": 0,
                "max": len(dates) - 1,
                "value": 0,
                "step": 1,
                "marks": date_marks,
            },
            button_props={"className": "float-left"},
        ),
        html.Pre(id="click-data"),
        dcc.Store(id="map-relayout-data"),
        html.Div(
            [
                dcc.Input(
                    id="country-input",
                    type="text",
                    placeholder="Enter desired country...",
                    style={"font-size": "20px"},
                ),
                html.Button(
                    "Search country",
                    id="country-button",
                    n_clicks=0,
                    style={
                        "background-color": "#445570",
                        "color": "white",
                        "font-size": "15px",
                    },
                ),
            ]
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="fear-map")],
                    style={"display": "inline-block", "width": "50%"},
                ),
                html.Div(
                    [dcc.Graph(id="anger-map")],
                    style={"display": "inline-block", "width": "50%"},
                ),
            ]
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="happiness-map")],
                    style={"display": "inline-block", "width": "50%"},
                ),
                html.Div(
                    [dcc.Graph(id="sadness-map")],
                    style={"display": "inline-block", "width": "50%"},
                ),
            ]
        ),
        dcc.Store(id="updated-date"),
        html.Div(
            [
                html.Button(
                    "Fear",
                    id="fear-button",
                    n_clicks=0,
                    style={
                        "background-color": "#dbe2ff",
                        "color": "black",
                        "font-size": "30px",
                    },
                ),
                html.Button(
                    "Anger",
                    id="anger-button",
                    n_clicks=0,
                    style={
                        "background-color": "#f5b8b8",
                        "color": "black",
                        "font-size": "30px",
                    },
                ),
                html.Button(
                    "Happiness",
                    id="happiness-button",
                    n_clicks=0,
                    style={
                        "background-color": "#e8f7da",
                        "color": "black",
                        "font-size": "30px",
                    },
                ),
                html.Button(
                    "Sadness",
                    id="sadness-button",
                    n_clicks=0,
                    style={
                        "background-color": "#eed9fc",
                        "color": "black",
                        "font-size": "30px",
                    },
                ),
            ]
        ),
        dcc.Graph(id="big-map", style={"height": "800px", "width": "100%"}),
        html.Button(
            "Reset to Global",
            id="reset-button",
            n_clicks=0,
            disabled=True,
            style={
                "background-color": "#fadfaa",
                "color": "black",
                "font-size": "20px",
            },
        ),
        dcc.Graph(id="emotion-lines"),
        # html.Button('Reset to Global Summarizaton', id='reset-button-sum', n_clicks=0, disabled=True, style ={'background-color': '#fadfaa', 'color':'black', 'font-size':'20px'}),
        html.Div(
            [
                dcc.Input(
                    id="country-name-input",
                    type="text",
                    placeholder="Enter country name...",
                ),
                html.Button(
                    "Enter",
                    id="enter-button",
                    n_clicks=0,
                    style={"margin-left": "10px"},
                ),
                html.Button(
                    "Reset to Global Summarization",
                    id="reset-summarization",
                    n_clicks=0,
                    style={"margin-left": "10px"},
                ),
            ]
        ),
        dcc.Graph(id="stacked-emotions"),
        dcc.Graph(id="cumulative-emotions"),
    ],
    style={"text-align": "center"},
)


def zoom_country(fig, country, geo_path):
    geo_df = pd.read_csv(geo_path)
    coord_row = geo_df[
        (geo_df["COUNTRY"].str.lower() == country.lower())
        | (geo_df["ISO"].str.lower() == country.lower())
    ]
    if coord_row.empty:
        return

    # TODO: Maybe make an animation when transitioning from country to country

    fig.update_geos(
        center={
            "lon": coord_row.iloc[0]["longitude"],
            "lat": coord_row.iloc[0]["latitude"],
        },
        projection_scale=4,
    )
    # return fig


@app.callback(
    [
        Output("fear-map", "figure", allow_duplicate=True),
        Output("anger-map", "figure", allow_duplicate=True),
        Output("happiness-map", "figure", allow_duplicate=True),
        Output("sadness-map", "figure", allow_duplicate=True),
    ],
    [Input("country-button", "n_clicks")],
    [
        State("country-input", "value"),
        State("fear-map", "figure"),
        State("anger-map", "figure"),
        State("happiness-map", "figure"),
        State("sadness-map", "figure"),
    ],
    prevent_initial_call=True,
)
def search_country(
    n_clicks, country, fear_dict, anger_dict, happiness_dict, sadness_dict
):
    print("Hi")
    fear_fig = go.Figure(fear_dict)
    anger_fig = go.Figure(anger_dict)
    happiness_fig = go.Figure(happiness_dict)
    sadness_fig = go.Figure(sadness_dict)
    # print(type(fear_fig))
    print(fear_dict["layout"]["geo"])
    zoom_country(fear_fig, country, "countries.csv")
    zoom_country(anger_fig, country, "countries.csv")
    zoom_country(happiness_fig, country, "countries.csv")
    zoom_country(sadness_fig, country, "countries.csv")

    return fear_fig, anger_fig, happiness_fig, sadness_fig


@app.callback(
    Output("map-relayout-data", "data"),  # Output to store relayoutData
    Input("fear-map", "relayoutData"),
    Input("anger-map", "relayoutData"),
    Input("happiness-map", "relayoutData"),
    Input("sadness-map", "relayoutData"),
    State("map-relayout-data", "data"),  # Current stored relayoutData
)
def store_relayout_data(
    fear_relayout, anger_relayout, happiness_relayout, sadness_relayout, existing_data
):
    ctx = dash.callback_context
    if not ctx.triggered:
        return existing_data
    new_relayout_data = ctx.triggered[0]["value"]
    if new_relayout_data:
        return new_relayout_data
    return existing_data


@app.callback(
    [
        Output("fear-map", "figure"),
        Output("anger-map", "figure"),
        Output("happiness-map", "figure"),
        Output("sadness-map", "figure"),
        Output("emotion-lines", "figure"),
        Output("reset-button", "disabled"),
        Output("reset-button", "n_clicks"),
    ],
    [
        Input(PlaybackSliderAIO.ids.slider("date-slider"), "value"),
        Input("fear-map", "clickData"),
        Input("anger-map", "clickData"),
        Input("happiness-map", "clickData"),
        Input("sadness-map", "clickData"),
        Input("fear-map", "relayoutData"),
        Input("anger-map", "relayoutData"),
        Input("happiness-map", "relayoutData"),
        Input("sadness-map", "relayoutData"),
        Input("map-relayout-data", "data"),
        Input("reset-button", "n_clicks"),
    ],
    [
        State("fear-map", "figure"),
        State("anger-map", "figure"),
        State("happiness-map", "figure"),
        State("sadness-map", "figure"),
        State("reset-button", "disabled"),
    ],
)
def update_maps_and_lines(
    selected_date_index,
    fear_clickData,
    anger_clickData,
    happiness_clickData,
    sadness_clickData,
    fear_relayoutData,
    anger_relayoutData,
    happiness_relayoutData,
    sadness_relayoutData,
    map_relayout,
    n_clicks,
    fear_dict,
    anger_dict,
    happiness_dict,
    sadness_dict,
    button_disabled,
):
    selected_date = dates[selected_date_index]
    print("first map data:")
    print(selected_date)
    # Identify which input triggered the callback

    ctx = callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
    country = None
    relayout_data = None
    triggered_input = ctx.triggered[0]["prop_id"]

    # Logic to check which map triggered the zoom and to extract that relayoutData
    # relayout_data = None
    if triggered_input.endswith("relayoutData"):

        triggered_map_data = eval(
            triggered_input.split(".")[0].replace("-map", "_relayoutData")
        )
        if triggered_map_data:
            relayout_data = triggered_map_data

    # Check which map was clicked based on the triggered input
    if triggered_id == "fear-map" and fear_clickData:
        country = fear_clickData["points"][0]["location"]
    elif triggered_id == "anger-map" and anger_clickData:
        country = anger_clickData["points"][0]["location"]
    elif triggered_id == "happiness-map" and happiness_clickData:
        country = happiness_clickData["points"][0]["location"]
    elif triggered_id == "sadness-map" and sadness_clickData:
        country = sadness_clickData["points"][0]["location"]

    # Update the line plot based on the selected country or global data
    fig_lines = (
        plot_global_emotions(selected_date)
        if country is None
        else plot_country_emotions(selected_date, country)
    )

    # Always create choropleth maps with global data
    fear_fig = create_choropleth_map(selected_date, "fear_intensity")
    anger_fig = create_choropleth_map(selected_date, "anger_intensity")
    happiness_fig = create_choropleth_map(selected_date, "happiness_intensity")
    sadness_fig = create_choropleth_map(selected_date, "sadness_intensity")

    # # If there's valid relayout data, update all figures with this layout
    if relayout_data:
        for fig in (fear_fig, anger_fig, happiness_fig, sadness_fig):
            fig.update_layout(relayout_data)
    elif map_relayout:
        for fig in (fear_fig, anger_fig, happiness_fig, sadness_fig):
            fig.update_layout(relayout_data)

    if fear_dict and anger_dict and happiness_dict and sadness_dict:
        fear_geos = fear_dict["layout"]["geo"]
        anger_geos = anger_dict["layout"]["geo"]
        happiness_geos = happiness_dict["layout"]["geo"]
        sadness_geos = sadness_dict["layout"]["geo"]

        fear_fig.update_geos(fear_geos)
        anger_fig.update_geos(anger_geos)
        happiness_fig.update_geos(happiness_geos)
        sadness_fig.update_geos(sadness_geos)

        for fig in (fear_fig, anger_fig, happiness_fig, sadness_fig):
            fig.update_layout(relayout_data)

    # Determine the disabled state of the reset button

    reset_disabled = (
        False if country is not None else (True if n_clicks > 0 else button_disabled)
    )

    # Reset the button clicks to 0 after processing to avoid repeated reset triggers

    reset_n_clicks = 0 if n_clicks > 2 else n_clicks

    return (
        fear_fig,
        anger_fig,
        happiness_fig,
        sadness_fig,
        fig_lines,
        reset_disabled,
        reset_n_clicks,
    )


@app.callback(
    Output("big-map", "figure"),
    Output("fear-button", "n_clicks"),
    Output("anger-button", "n_clicks"),
    Output("happiness-button", "n_clicks"),
    Output("sadness-button", "n_clicks"),
    [
        Input(PlaybackSliderAIO.ids.slider("date-slider"), "value"),
        # Input("updated-date", "data"),
        Input("fear-button", "n_clicks"),
        Input("anger-button", "n_clicks"),
        Input("happiness-button", "n_clicks"),
        Input("sadness-button", "n_clicks"),
    ],
)
def update_big_map(
    selected_date_index, fear_clicks, anger_clicks, happiness_clicks, sadness_clicks
):
    global selected_emotion

    selected_date = dates[selected_date_index]

    print("big map data:")
    print(selected_date)
    # selected_date = datetime.strptime(selected_date, "%Y-%m-%d %H:%M:%S")
    # print("updated data:")
    # print(selected_date)
    emotion = None
    reset_fear_clicks = fear_clicks
    reset_anger_clicks = anger_clicks
    reset_happiness_clicks = happiness_clicks
    reset_sadness_clicks = sadness_clicks

    if fear_clicks > 0:
        selected_emotion = "fear_intensity"
        print("fear is clicked!!!")
        # fig = create_choropleth_map(selected_date, emotion)
        reset_fear_clicks = 0
    elif anger_clicks > 0:
        selected_emotion = "anger_intensity"
        # fig = create_choropleth_map(selected_date, emotion)
        reset_anger_clicks = 0
    elif happiness_clicks > 0:
        selected_emotion = "happiness_intensity"
        # fig = create_choropleth_map(selected_date, emotion)
        reset_happiness_clicks = 0
    elif sadness_clicks > 0:
        selected_emotion = "sadness_intensity"
        # fig = create_choropleth_map(selected_date, emotion)
        reset_sadness_clicks = 0

    # if emotion:

    #     fig = create_choropleth_map(selected_date, emotion)

    else:
        selected_emotion = "fear_intensity"
    fig = create_choropleth_map(selected_date, selected_emotion)
    return (
        fig,
        reset_fear_clicks,
        reset_anger_clicks,
        reset_happiness_clicks,
        reset_sadness_clicks,
    )


@app.callback(
    [
        Output("stacked-emotions", "figure"),
        Output("cumulative-emotions", "figure"),
        Output("country-name-input", "value"),
        Output("reset-summarization", "disabled"),
        Output("reset-summarization", "n_clicks"),
    ],
    [Input("enter-button", "n_clicks"), Input("reset-summarization", "n_clicks")],
    [State("country-name-input", "value"), State("reset-summarization", "disabled")],
)
def update_summarization(n_clicks, n_clicks_sum, countryName, button_disabled):
    fig_stacked = go.Figure()
    fig_cumulative = go.Figure()
    if n_clicks_sum > 0:
        countryName = ""
        fig_stacked = plot_stacked_global_emotions()
        fig_cumulative = plot_cumulative_global_emotions()
        n_clicks_sum = 0
        button_disabled = False
        return fig_stacked, fig_cumulative, countryName, button_disabled, n_clicks_sum
    if n_clicks > 0 and len(countryName.strip()) > 0:
        countryName = countryName.strip()
        countryName = countryName[0].upper() + countryName[1:]

        fig_stacked = (
            plot_stacked_global_emotions()
            if countryName is None
            else plot_stacked_country_emotions(countryName)
        )
        fig_cumulative = (
            plot_cumulative_global_emotions()
            if countryName is None
            else plot_cumulative_country_emotions(countryName)
        )
        countryName = ""
        return fig_stacked, fig_cumulative, countryName, button_disabled, n_clicks_sum
    else:
        countryName = ""
        fig_stacked = plot_stacked_global_emotions()
        fig_cumulative = plot_cumulative_global_emotions()
        return fig_stacked, fig_cumulative, countryName, button_disabled, n_clicks_sum


# Define the callback to display the consent modal on page load
@app.callback(
    Output("modal", "is_open"),
    [Input("consent-button", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, is_open):
    if n1:
        return False
    return True if not n1 and is_open else False


if __name__ == "__main__":

    app.run_server(debug=True)
