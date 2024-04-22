
from dash import dcc, html

from dash.dependencies import Input, Output, State

import plotly.graph_objects as go

from worldmap import create_choropleth_map, dates

import dash

from playback_slider_aio import PlaybackSliderAIO

from line_plot import plot_global_emotions, plot_country_emotions, important_dates_dict

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


#important_dates_dict = {'January10': 'Novel coronavirus announced', 'March11': 'WHO announces Pandemic', 'September23': 'New strain of Covid', 'October2': 'Trump infected'}
#important_dates_dict = {'2020-02-11': 'WHO names Covid-19','2020-03-11': 'WHO declares pandemic', '2020-04-02': 'Worldwide cases at 1 million', '2020-04-08': 'Wuhan reopens', '2020-04-13': 'US ceases WHO funding','2020-04-17': 'First Moderna trials', '2020-04-24': 'ACT-A announced',  '2020-09-23': 'New strain of Covid', '2020-09-28': 'Global deaths at 1 million', '2020-10-02': 'Trump infected'}

print(type(dates[0]))

for i, date in enumerate(dates):

    # Timeline:
    # Jan 10: Novel coronavirus announced by WHO
    # March 11, 2020
    #After more than 118,000 cases in 114 countries and 4,291 deaths, the WHO declares COVID-19 a pandemic.
    #
    #July 27 — Moderna Vaccine Begins Phase 3 Trial,
    #
    #September 8 — AstraZeneca Halts Phase 3 Vaccine Trial
    #
    #September 14 — Pfizer, BioNTech Expand Phase 3 Trial
    #
    #September 21 — Johnson & Johnson Begins Phase 3 Vaccine Trial
    #
    #September 23 — A New, More Contagious Strain of COVID-19 Is Discovered


    #date_str = calendar.month_name[date.month] + str(date.day)
    #print(date.day)
    curr_label = ''
    curr_style = {'display': 'none'}
    if (date.day == 1):
        curr_label = calendar.month_name[date.month]
        curr_style = {'display': 'block'}

    elif (date.strftime('%Y-%m-%d') in important_dates_dict):
        curr_label = important_dates_dict[date.strftime('%Y-%m-%d')]
        curr_style = {'display': 'block', 'transform': 'rotate(-45deg) translateY(-3rem)'}

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

    html.Div([html.Hr(style={'border-top': '1px solid #ccc', 'margin': '20px 0px', 'background-color': '#1d3a69', 'height': '75px', 'width': '100%'}),

            #   html.Hr(style={'height':'20px'}),

]),

    PlaybackSliderAIO(

        aio_id='date-slider',

        slider_props={'min': 0, 'max': len(dates)-1, 'value': 0, 'step': 1, 'marks': date_marks},

        button_props={'className': 'float-left'}

    ),

    
    html.Pre(id='click-data'),

    html.Div([
            
            dcc.Input(id='country-input', type='text', placeholder='Enter desired country...', style={'font-size': '20px'}),
            html.Button('Search country', id='country-button', n_clicks=0, style={'background-color': '#445570', 'color': 'white','font-size': '15px'}) 
    ]),

    

    html.Div([

        html.Div([dcc.Graph(id='fear-map')], style={'display': 'inline-block', 'width': '50%'}),

        html.Div([dcc.Graph(id='anger-map')], style={'display': 'inline-block', 'width': '50%'}),

    ]),

    html.Div([

        html.Div([dcc.Graph(id='happiness-map')], style={'display': 'inline-block', 'width': '50%'}),

        html.Div([dcc.Graph(id='sadness-map')], style={'display': 'inline-block', 'width': '50%'}),

    ]),

    html.Div([

        html.Button('Fear', id='fear-button', n_clicks=0, style ={'background-color': '#dbe2ff', 'color':'black', 'font-size':'30px'}),

        html.Button('Anger', id='anger-button', n_clicks=0, style ={'background-color': '#f5b8b8', 'color':'black', 'font-size':'30px'}),

        html.Button('Happiness', id='happiness-button', n_clicks=0,  style ={'background-color': '#e8f7da', 'color':'black', 'font-size':'30px'}),

        html.Button('Sadness', id='sadness-button', n_clicks=0,  style ={'background-color': '#eed9fc', 'color':'black', 'font-size':'30px'})



    ]),

    dcc.Graph(id='big-map'),



    html.Button('Reset to Global', id='reset-button', n_clicks=0, disabled=True, style ={'background-color': '#fadfaa', 'color':'black', 'font-size':'20px'}),

    dcc.Graph(id='emotion-lines')

], style={'text-align': 'center'})

#{0: 'January', 48856: 'February', 304854: 'March', 3349990: 'April', 'May': 6501119, 8832159:'June', 10353251: 'July', 11394992: 'August', 12229689: 'September', 13012033: 'October', 14043435: 'November'}

from dash.exceptions import PreventUpdate

from dash import callback_context

def zoom_country(fig, country, geo_path):
    geo_df = pd.read_csv(geo_path)
    coord_row = geo_df[(geo_df['COUNTRY'].str.lower() == country.lower()) | (geo_df['ISO'].str.lower() == country.lower())]
    if (coord_row.empty):
        return

    #TODO: Maybe make an animation when transitioning from country to country


    fig.update_geos(
        center={'lon': coord_row.iloc[0]['longitude'], 'lat': coord_row.iloc[0]['latitude']},
        projection_scale=4,
    )
    #return fig

@app.callback(
[Output('fear-map', 'figure', allow_duplicate=True),
        Output('anger-map', 'figure', allow_duplicate=True),
        Output('happiness-map', 'figure', allow_duplicate=True),
        Output('sadness-map', 'figure', allow_duplicate=True),],
[Input('country-button', 'n_clicks')],
[State('country-input', 'value'), State('fear-map', 'figure'),
        State('anger-map', 'figure'),
        State('happiness-map', 'figure'),
        State('sadness-map', 'figure'),], prevent_initial_call=True)
def search_country(n_clicks, country, fear_dict, anger_dict, happiness_dict, sadness_dict):
    print('Hi')
    fear_fig = go.Figure(fear_dict)
    anger_fig = go.Figure(anger_dict)
    happiness_fig = go.Figure(happiness_dict)
    sadness_fig = go.Figure(sadness_dict)
    # print(type(fear_fig))
    print(fear_dict['layout']['geo'])
    zoom_country(fear_fig, country, 'countries.csv')
    zoom_country(anger_fig, country, 'countries.csv')
    zoom_country(happiness_fig, country, 'countries.csv')
    zoom_country(sadness_fig, country, 'countries.csv')


    return fear_fig, anger_fig, happiness_fig, sadness_fig


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

    ],

    [State('reset-button', 'disabled'),
        State('fear-map', 'figure'),
        State('anger-map', 'figure'),
        State('happiness-map', 'figure'),
        State('sadness-map', 'figure'),]
)
def update_maps_and_lines(selected_date_index, fear_clickData, anger_clickData, happiness_clickData, sadness_clickData, n_clicks, button_disabled, fear_dict, anger_dict, happiness_dict, sadness_dict):

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



    # Always create choropleth maps with global data

    fear_fig = create_choropleth_map(selected_date, 'fear_intensity')

    anger_fig = create_choropleth_map(selected_date, 'anger_intensity')

    happiness_fig = create_choropleth_map(selected_date, 'happiness_intensity')

    sadness_fig = create_choropleth_map(selected_date, 'sadness_intensity')

    if (fear_dict and anger_dict and happiness_dict and sadness_dict):
        fear_geos = fear_dict['layout']['geo']
        anger_geos = anger_dict['layout']['geo']
        happiness_geos = happiness_dict['layout']['geo']
        sadness_geos = sadness_dict['layout']['geo']

        fear_fig.update_geos(fear_geos)
        anger_fig.update_geos(anger_geos)
        happiness_fig.update_geos(happiness_geos)
        sadness_fig.update_geos(sadness_geos)






    # Determine the disabled state of the reset button

    reset_disabled = False if country is not None else (True if n_clicks > 0 else button_disabled)



    # Reset the button clicks to 0 after processing to avoid repeated reset triggers

    reset_n_clicks = 0 if n_clicks > 0 else n_clicks



    return fear_fig, anger_fig, happiness_fig, sadness_fig, fig_lines, reset_disabled, reset_n_clicks



@app.callback(

    Output('big-map', 'figure'),

    Output('fear-button', 'n_clicks'),

    Output('anger-button', 'n_clicks'),

    Output('happiness-button', 'n_clicks'),

    Output('sadness-button', 'n_clicks'),

    [

        Input(PlaybackSliderAIO.ids.slider('date-slider'), 'value'),

        Input('fear-button', 'n_clicks'),

        Input('anger-button', 'n_clicks'),

        Input('happiness-button', 'n_clicks'),

        Input('sadness-button', 'n_clicks'),

    ]

)

def update_big_map(selected_date_index, fear_clicks, anger_clicks, happiness_clicks, sadness_clicks):

    selected_date = dates[selected_date_index]

    ctx = dash.callback_context

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None



    emotion = None

    reset_fear_clicks = fear_clicks

    reset_anger_clicks = anger_clicks

    reset_happiness_clicks = happiness_clicks

    reset_sadness_clicks = sadness_clicks



    if fear_clicks > 0:

        emotion = 'fear_intensity'

        print("fear is clicked!!!")

        fig = create_choropleth_map(selected_date, emotion)

        reset_fear_clicks = 0 

    elif anger_clicks > 0:

        emotion = 'anger_intensity'

        fig = create_choropleth_map(selected_date, emotion)

        reset_anger_clicks = 0 

    elif happiness_clicks > 0:

        emotion = 'happiness_intensity'

        fig = create_choropleth_map(selected_date, emotion)

        reset_happiness_clicks = 0 

    elif sadness_clicks > 0:

        emotion = 'sadness_intensity'

        fig = create_choropleth_map(selected_date, emotion)

        reset_sadness_clicks = 0 





    # if emotion:

    #     fig = create_choropleth_map(selected_date, emotion)

    else:

        fig = go.Figure()



    return fig, reset_fear_clicks, reset_anger_clicks, reset_happiness_clicks, reset_sadness_clicks



if __name__ == '__main__':

    app.run_server(debug=True)
