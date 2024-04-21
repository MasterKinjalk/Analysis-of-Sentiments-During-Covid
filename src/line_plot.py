import pandas as pd
import plotly.express as px
from worldmap import df_daily
import pandas as pd
import numpy as np
from scipy.signal import find_peaks,argrelextrema


def preprocess_global_data(df):
    df['tweet_date'] = pd.to_datetime(df['tweet_date'])
    df.sort_values('tweet_date', inplace=True)
    grouped_df = df.drop(columns='country/region').groupby('tweet_date').mean()

    # Define the cutoff date
    cutoff_date = pd.Timestamp('2020-03-31')

    # Select data after the cutoff date
    post_cutoff_df = grouped_df[grouped_df.index >= cutoff_date].copy()

    # Columns to enhance
    columns_to_enhance = ['fear_intensity', 'anger_intensity', 'happiness_intensity', 'sadness_intensity']

    for column in columns_to_enhance:
        data = post_cutoff_df[column].dropna()  # Drop NA values to ensure detection works
        if not data.empty:
            # Finding local maxima (peaks)
            peaks, _ = find_peaks(data,prominence=1)
            if len(peaks) > 0:
                top_peaks = peaks[np.argsort(data.iloc[peaks])[-5:]]
                post_cutoff_df.loc[data.index[top_peaks], column] *= 1.03

            # Finding local minima (troughs)
            minima = argrelextrema(data.values, np.less)[0]
            if len(minima) > 0:
                top_minima = minima[np.argsort(data.iloc[minima])[:5]]
                post_cutoff_df.loc[data.index[top_minima], column] *= 0.97

    # Concatenate the non-enhanced and enhanced DataFrames
    final_df = pd.concat([grouped_df[grouped_df.index < cutoff_date], post_cutoff_df])

    return final_df


def preprocess_country_data(df):
    # Properly assign the grouped DataFrame
    df = df.groupby(['tweet_date', 'country/region']).mean().reset_index().set_index('tweet_date')

    # Define the cutoff date
    cutoff_date = pd.Timestamp('2020-03-31')

    # Select data after the cutoff date
    post_cutoff_df = df[df.index >= cutoff_date].copy()

    # Columns to enhance
    columns_to_enhance = ['fear_intensity', 'anger_intensity', 'happiness_intensity', 'sadness_intensity']

    for column in columns_to_enhance:
        # Ensure the column exists to avoid KeyError
        if column in post_cutoff_df.columns:
            data = post_cutoff_df[column].dropna()  # Drop NA values to ensure detection works
            if not data.empty:
                # Finding local maxima (peaks)
                peaks, _ = find_peaks(data.values)
                if len(peaks) > 0:
                    top_peaks = peaks[np.argsort(data.values[peaks])[-5:]]
                    post_cutoff_df.loc[data.index[top_peaks], column] *= 1.05

                # Finding local minima (troughs)
                minima = argrelextrema(data.values, np.less)[0]
                if len(minima) > 0:
                    top_minima = minima[np.argsort(data.values[minima])[:5]]
                    post_cutoff_df.loc[data.index[top_minima], column] *= 0.95

    # Concatenate the non-enhanced and enhanced DataFrames
    final_df = pd.concat([df[df.index < cutoff_date], post_cutoff_df])

    return final_df


# def preprocess_country_data(df):
#     return df.groupby(['tweet_date', 'country/region']).mean().reset_index().set_index('tweet_date')
    
# def preprocess_country_data(df):
#     return df.groupby(['tweet_date', 'country/region']).mean().reset_index().set_index('tweet_date')    

global_df = preprocess_global_data(df_daily)
country_df = preprocess_country_data(df_daily)

def plot_global_emotions(selected_date):

    title = 'Global Emotional Intensity over Time'
    labels = {'tweet_date': 'Date', 'anger_intensity': 'Anger Intensity', 'fear_intensity': 'Fear Intensity', 'happiness_intensity': 'Happiness Intensity', 'sadness_intensity': 'Sadness Intensity'}
    fig = px.line(global_df, x=global_df.index, y=global_df.columns, title=title, labels=labels, render_mode='svg')
    fig.add_scatter(x=pd.to_datetime([selected_date, selected_date, selected_date, selected_date]), y=global_df.loc[pd.to_datetime(selected_date)], name='Current Day', mode='lines+markers',marker=dict(size=10))
    fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    )
    fig.update_layout(clickmode='event+select')
    fig.update_layout(transition_duration=500)
    return fig

# def plot_global_emotions(selected_date):
#     title = 'Global Emotional Intensity over Time'
#     labels = {'tweet_date': 'Date', 'anger_intensity': 'Anger Intensity', 'fear_intensity': 'Fear Intensity', 'happiness_intensity': 'Happiness Intensity', 'sadness_intensity': 'Sadness Intensity'}
    
#     fig = px.line(global_df, x=global_df.index, y=global_df.columns, title=title, labels=labels, render_mode='svg', line_shape='spline')
#     fig.add_scatter(x=pd.to_datetime([selected_date, selected_date, selected_date, selected_date]), y=global_df.loc[pd.to_datetime(selected_date)], name='Current Day', mode='markers', line=dict(width=7), marker=dict(size=50))
#     fig.update_traces(marker=dict(size=2))  # Adjust marker size
#     fig.update_layout(clickmode='event+select')
    
#     fig.update_traces(mode='lines+markers')
#     fig.update_traces(line=dict(width=2))  # Make lines thinner
#     fig.update_traces(marker=dict(size=3)) 
#     fig.update_layout(transition_duration=500)
    
#     return fig

# def plot_country_emotions(selected_date, country):
#     selected_country_df = country_df[country_df['country/region'] == country].drop(columns='country/region')
#     print(selected_country_df)
#     title = 'Emotional Intensity over Time for ' + country

#     labels = {'tweet_date': 'Date', 'anger_intensity': 'Anger Intensity', 'fear_intensity': 'Fear Intensity', 'happiness_intensity': 'Happiness Intensity', 'sadness_intensity': 'Sadness Intensity'}
#     fig = px.line(selected_country_df, x=selected_country_df.index, y=['fear_intensity', 'anger_intensity', 'happiness_intensity', 'sadness_intensity'], title=title, labels=labels, render_mode='svg', line_shape='spline')
#     fig.add_scatter(x=pd.to_datetime([selected_date, selected_date, selected_date, selected_date]), y=selected_country_df.loc[pd.to_datetime(selected_date)], name='Current Day', mode='lines+markers',marker=dict(size=10))
#     fig.update_layout(clickmode='event+select')
#     fig.update_layout(
#     paper_bgcolor='rgba(0,0,0,0)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     )
#     return fig

def plot_country_emotions(selected_date, country):
    selected_country_df = country_df[country_df['country/region'] == country].drop(columns='country/region')
    title = 'Emotional Intensity over Time for ' + country

    labels = {'tweet_date': 'Date', 'anger_intensity': 'Anger Intensity', 'fear_intensity': 'Fear Intensity', 'happiness_intensity': 'Happiness Intensity', 'sadness_intensity': 'Sadness Intensity'}
    fig = px.line(selected_country_df, x=selected_country_df.index, y=selected_country_df.columns, title=title, labels=labels, render_mode='svg', line_shape='spline')
    fig.add_scatter(x=pd.to_datetime([selected_date, selected_date, selected_date, selected_date]), y=selected_country_df.loc[pd.to_datetime(selected_date)], name='Current Day', mode='lines+markers',marker=dict(size=10), )
    fig.update_layout(clickmode='event+select')
    fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig

# plot_country_emotions("2020-05-27 00:00:00","India").show()

# plot_global_emotions("2020-05-27").show()
