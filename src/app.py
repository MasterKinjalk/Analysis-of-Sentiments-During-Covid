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
    dcc.Graph(id='emotion-lines')
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
        Input('fear-map', 'relayoutData'),
        Input('anger-map', 'relayoutData'),
        Input('happiness-map', 'relayoutData'),
        Input('sadness-map', 'relayoutData'),

    ],
    [State('reset-button', 'disabled'),
     State('fear-map', 'figure'),
     State('anger-map', 'figure'),
     State('happiness-map', 'figure'),
     State('sadness-map', 'figure')
     ]
)

def update_maps_and_lines(selected_date_index, fear_clickData, anger_clickData, happiness_clickData, sadness_clickData, n_clicks, relayoutData1, relayoutData2, relayoutData3, relayoutData4, button_disabled, fig1, fig2, fig3, fig4):

    selected_date = dates[selected_date_index]
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    country = None

    # Check if triggered_id is not None and handle map clicks safely
    if triggered_id and triggered_id.endswith('-map'):
        clickData = ctx.triggered[0].get('value')
        if clickData and 'points' in clickData:
            country = clickData['points'][0]['location'] if clickData['points'] else None

    # Update the line plot based on the selected country or global data
    fig_lines = plot_global_emotions(selected_date) if country is None else plot_country_emotions(selected_date, country)

    # Conditionally update map figures based on interaction type
    if triggered_id and triggered_id == 'date-slider':
        fear_fig = create_choropleth_map(selected_date, 'fear_intensity')
        anger_fig = create_choropleth_map(selected_date, 'anger_intensity')
        happiness_fig = create_choropleth_map(selected_date, 'happiness_intensity')
        sadness_fig = create_choropleth_map(selected_date, 'sadness_intensity')
    else:
        # Handle relayout data and maintain the state
        if any(triggered_id == x and ctx.triggered[0].get('value') for x in ['fear-map', 'anger-map', 'happiness-map', 'sadness-map']):
            new_layout = ctx.triggered[0]['value']
            if new_layout and 'mapbox.zoom' in new_layout and 'mapbox.center' in new_layout:
                zoom = new_layout['mapbox.zoom']
                center = new_layout['mapbox.center']
                for fig in [fig1, fig2, fig3, fig4]:
                    fig['layout']['mapbox']['zoom'] = zoom
                    fig['layout']['mapbox']['center'] = center
        fear_fig, anger_fig, happiness_fig, sadness_fig = fig1, fig2, fig3, fig4

    reset_disabled = False if country is not None else (True if n_clicks > 0 else button_disabled)
    reset_n_clicks = 0 if n_clicks > 0 else n_clicks

    return fear_fig, anger_fig, happiness_fig, sadness_fig, fig_lines, reset_disabled, reset_n_clicks


  

if __name__ == '__main__':
    app.run_server(debug=True)
