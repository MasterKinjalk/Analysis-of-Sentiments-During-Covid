import pandas as pd
import plotly.express as px


def preprocess_global_data(df):
    df['tweet_date'] = pd.to_datetime(df['tweet_date'])
    df.sort_values('tweet_date', inplace=True)
    grouped_df = df.drop(columns='country/region').groupby('tweet_date').mean().sort_values('tweet_date')
    #print(grouped_df.head())
    #grouped_df['tweet_date'] = pd.to_datetime(grouped_df['tweet_date'])
    return grouped_df

def preprocess_country_data(df):
    return df.groupby(['tweet_date', 'country/region']).mean().reset_index().set_index('tweet_date')
    

df = pd.read_csv('processedData/sampled_cleaned_covid_twitter_data.csv', usecols=['tweet_date', 'fear_intensity', 'anger_intensity', 'happiness_intensity', 'sadness_intensity', 'country/region'])

global_df = preprocess_global_data(df)
country_df = preprocess_country_data(df)

def plot_global_emotions(selected_date):

    title = 'Global Emotional Intensity over Time'
    labels = {'tweet_date': 'Date', 'anger_intensity': 'Anger Intensity', 'fear_intensity': 'Fear Intensity', 'happiness_intensity': 'Happiness Intensity', 'sadness_intensity': 'Sadness Intensity'}
    fig = px.line(global_df, x=global_df.index, y=global_df.columns, title=title, labels=labels, render_mode='svg')
    fig.add_scatter(x=pd.to_datetime([selected_date, selected_date, selected_date, selected_date]), y=global_df.loc[pd.to_datetime(selected_date)], name='Current Day', mode='lines+markers',marker=dict(size=10), )
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

#plot_global_emotions(pd.to_datetime('2020-01-27')).show()
