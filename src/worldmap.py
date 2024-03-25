import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np
# ray.init(num_cpus=4, ignore_reinit_error=True)

# Read the CSV file and drop columns within the function
df = pd.read_csv('grouped_sampled_cleaned_covid_twitter_data.csv')

# Convert timestamps to datetime, extract date, and sort
df['tweet_date'] = pd.to_datetime(df['tweet_date'], format='%Y-%m-%d')
df.sort_values('tweet_date', inplace=True)

# # Aggregate data by date and country/region to get daily averages
# df_daily = df.groupby(['tweet_date', 'country/region']).mean().reset_index()

df_daily = df 
# Unique dates for the slider
dates = df_daily['tweet_date'].unique()

import plotly.graph_objs as go

# This function may not be needed if we are focusing on individual maps with create_choropleth_map
def create_subplot(df_filtered, emotion,title):
    # Define color scales for each emotion
    color_scales = {
        'fear_intensity': 'Blues',
        'anger_intensity': 'Reds',
        'happiness_intensity': 'Greens',
        'sadness_intensity': 'Purples'
    }

    # Adjusting min and max intensity values for the specific emotion
    zmin = df_filtered[emotion].min()
    zmax = df_filtered[emotion].max()

    fig = go.Choropleth(
        locations=df_filtered["country/region"],
        locationmode="country names",
        z=df_filtered[emotion],
        zmin=zmin,
        zmax=zmax,
        text=df_filtered["country/region"],
        colorscale=color_scales.get(emotion, 'Viridis'),  # Default to 'Viridis' if emotion key is not found
        autocolorscale=False,
        colorbar_title=title
    )
    return fig

def handle_click_map(trace, points, selector):
    print(trace)
    print(points)
    print(selector)

def create_choropleth_map(date, emotion):
    df_filtered = df_daily[df_daily['tweet_date'] == date]
    
    # Define color scales for each emotion
    color_scales = {
        'fear_intensity': 'Blues',
        'anger_intensity': 'Reds',
        'happiness_intensity': 'Greens',
        'sadness_intensity': 'Purples'
    }

    # Calculate min and max intensity values for the specific emotion from the filtered data
    min_val = df_filtered[emotion].min()
    max_val = df_filtered[emotion].max()

    fig = go.Figure(go.Choropleth(
        locations=df_filtered["country/region"], 
        locationmode="country names",
        z=df_filtered[emotion], 
        zmin=min_val,  # Use the calculated min value
        zmax=max_val,  # Use the calculated max value
        text=df_filtered["country/region"],
        colorscale=color_scales[emotion],
        autocolorscale=False
    ))
    
    fig.update_layout(
        title_text=f'{emotion.replace("_", " ").capitalize()} for {str(date)}',
        geo=dict(
            showframe=True,
            showcoastlines=False,
            projection_type='equirectangular'
        ),
    autosize = True
    )
    
    return fig

