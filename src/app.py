from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from worldmap import create_choropleth_map, dates
import dash
from playback_slider_aio import PlaybackSliderAIO
from line_plot import plot_global_emotions, plot_country_emotions
import dash_bootstrap_components as dbc
import calendar
import json
import pandas as pd
from stacked_graph import plot_stacked_country_emotions, plot_stacked_global_emotions
from cumulative_graph import plot_cumulative_country_emotions, plot_cumulative_global_emotions
app = dash.Dash(__name__, external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME
    ])

server = app.server

# Create marks for the slider without displaying labels (empty strings)
# but the tooltip will display the actual date
# Create marks for the slider with actual dates in the tooltip
#date_marks = {i: {'label': '', 'style': {'display': 'none'}, 'tooltip': date} for i, date in enumerate(dates)}
date_marks = {}
for i, date in enumerate(dates):
    #print(date.day)
    curr_label = calendar.month_name[date.month] if date.day == 1 else ''
    curr_style = {'display': 'block'} if date.day == 1 else {'display': 'none'}
    #curr_tooltip = {'placement': 'bottom'}
    date_marks[i] = {'label': curr_label, 'style': curr_style}

# date_marks[0]['label'] = 'January'
# date_marks[0]['style'] = {'display': 'block'}

# Initialize the slider
app.layout = html.Div([
    dbc.Modal(
        [
            dbc.ModalHeader("Disclaimer"),
            dbc.ModalBody('''No personally identifiable information (PII):
            This visualization does not store or display any personally identifiable information. Our aim is to respect privacy and maintain the confidentiality of all individuals. 
            \n
            Purpose of the Visualization:
            The visualization is intended solely for informational purposes. It is not designed to foster or encourage prejudice against any residents of specific countries or regions. Our goal is to provide clear, unbiased information to help users understand trends and patterns, not to facilitate dgments or biases. 
            \n
            Data Representation and Bias:
            Please be aware that the data presented may reflect inherent biases due to varying levels of Twitter usage across different countries or regions. Consequently, regions with higher Twitter activity may appear disproportionately represented. This does not necessarily indicate actual levels of COVID-19 activity but rather the volume of discussion surrounding it on this platform.
            \n
            Ethical Use of Data:
            We are committed to the ethical use of data. It is crucial that this visualization is used in a manner that does not contribute to misinformation or stigmatize any countries or regions. We urge all users to consider the context and limitations of the data when interpreting this visualization. Misinterpretations that could lead to misinformation or discrimination are strongly discouraged.
            \nLimitations of Data:
            Users should be aware of the limitations inherent in this data, which is sourced from publicly available Twitter posts. The insights derived are not definitive medical or scientific data and should be viewed as indicative rather than conclusive.
            \n
            Changes and Updates:
            The information in this visualization is subject to change and may be updated periodically to reflect new data or corrections. We encourage users to check back regularly for the most current information.
            \n
            By using this visualization, you acknowledge your understanding and agreement to these terms.
            '''),
            dbc.ModalFooter(
                dbc.Button("I acknowledge.", id="consent-button", color="primary", className="ml-auto")
            ),
        ],
        id="modal",
        centered=True,
        is_open=True,
    ),
    html.Div([
        html.H1('Visualizing Global Emotions for 2020 Through Covid-19 Tweets', id='page-title', style={'color': '#89a2cc', 'font-size': '50px'})
    ],
    style={'display': 'flex', 'justify-content': 'center'}),
    html.Div([html.Hr(style={'border-top': '1px solid #ccc', 'margin': '20px 0px', 'background-color': '#1d3a69', 'height': '40px', 'width': '100%'}),
            #   html.Hr(style={'height':'20px'}),
]),
    PlaybackSliderAIO(
        aio_id='date-slider',
        slider_props={'min': 0, 'max': len(dates)-1, 'value': 0, 'step': 1, 'marks': date_marks},
        button_props={'className': 'float-left'}
    ),
    html.Pre(id='click-data'),
    
    html.Div([
        html.Div([dcc.Graph(id='fear-map')], style={'display': 'inline-block', 'width': '50%'}),
        html.Div([dcc.Graph(id='anger-map')], style={'display': 'inline-block', 'width': '50%'}),
    ]),
    html.Div([
        html.Div([dcc.Graph(id='happiness-map')], style={'display': 'inline-block', 'width': '50%'}),
        html.Div([dcc.Graph(id='sadness-map')], style={'display': 'inline-block', 'width': '50%'}),
    ]),
    html.Button('Reset to Global', id='reset-button', n_clicks=0, disabled=True, style ={'background-color': '#fadfaa', 'color':'black', 'font-size':'20px'}),
    dcc.Graph(id='emotion-lines'),
    # Interval component for triggering updates
    dcc.Interval(id='interval-component', interval=500, n_intervals=1),  # Update interval could be adjusted based on your needs
    html.Br(),
    html.Div(id='file-name-output'),
    dcc.Graph(id='stacked-emotions'),
    dcc.Graph(id='cumulative-emotions')
], style={'text-align': 'center'})
#{0: 'January', 48856: 'February', 304854: 'March', 3349990: 'April', 'May': 6501119, 8832159:'June', 10353251: 'July', 11394992: 'August', 12229689: 'September', 13012033: 'October', 14043435: 'November'}
from dash.exceptions import PreventUpdate
from dash import callback_context

@app.callback(
    [
        Output('fear-map', 'figure'),
        Output('anger-map', 'figure'),
        Output('happiness-map', 'figure'),
        Output('sadness-map', 'figure'),
        Output('emotion-lines', 'figure'),
        Output('stacked-emotions', 'figure'),
        Output('cumulative-emotions', 'figure'),
        Output('reset-button', 'disabled'),
        Output('reset-button', 'n_clicks'),
    ],
    [
        Input(PlaybackSliderAIO.ids.slider('date-slider'), 'value'),
        Input('fear-map', 'clickData'),
        Input('anger-map', 'clickData'),
        Input('happiness-map', 'clickData'),
        Input('sadness-map', 'clickData'),
        Input('reset-button', 'n_clicks'),
    ],
    [State('reset-button', 'disabled')]
)
def update_maps_and_lines(selected_date_index, fear_clickData, anger_clickData, happiness_clickData, sadness_clickData, n_clicks, button_disabled):
    selected_date = dates[selected_date_index]
    # Identify which input triggered the callback
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    country = None

    # Check which map was clicked based on the triggered input
    if triggered_id == 'fear-map' and fear_clickData:
        country = fear_clickData['points'][0]['location']
    elif triggered_id == 'anger-map' and anger_clickData:
        country = anger_clickData['points'][0]['location']
    elif triggered_id == 'happiness-map' and happiness_clickData:
        country = happiness_clickData['points'][0]['location']
    elif triggered_id == 'sadness-map' and sadness_clickData:
        country = sadness_clickData['points'][0]['location']

    # Update the line plot based on the selected country or global data
    fig_lines = plot_global_emotions(selected_date) if country is None else plot_country_emotions(selected_date, country)
    fig_stacked = plot_stacked_global_emotions() if country is None else plot_stacked_country_emotions(country)
    fig_cumulative = plot_cumulative_global_emotions() if country is None else plot_cumulative_country_emotions(country)
    # Always create choropleth maps with global data
    fear_fig = create_choropleth_map(selected_date, 'fear_intensity')
    anger_fig = create_choropleth_map(selected_date, 'anger_intensity')
    happiness_fig = create_choropleth_map(selected_date, 'happiness_intensity')
    sadness_fig = create_choropleth_map(selected_date, 'sadness_intensity')


    # Determine the disabled state of the reset button
    reset_disabled = False if country is not None else (True if n_clicks > 0 else button_disabled)

    print("reset disabled - ", reset_disabled)
    # Reset the button clicks to 0 after processing to avoid repeated reset triggers
    reset_n_clicks = 0 if n_clicks > 0 else n_clicks

    return fear_fig, anger_fig, happiness_fig, sadness_fig, fig_lines, fig_stacked,fig_cumulative, reset_disabled, reset_n_clicks

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

if __name__ == '__main__':
    app.run_server(debug=True)
