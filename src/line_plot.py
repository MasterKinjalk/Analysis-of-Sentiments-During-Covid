import pandas as pd
import plotly.express as px
from worldmap import df_daily


def preprocess_global_data(df):
    df['tweet_date'] = pd.to_datetime(df['tweet_date'])
    df.sort_values('tweet_date', inplace=True)
    grouped_df = df.drop(columns='country/region').groupby('tweet_date').mean().sort_values('tweet_date')
    #print(grouped_df.head())
    #grouped_df['tweet_date'] = pd.to_datetime(grouped_df['tweet_date'])
    return grouped_df

def preprocess_country_data(df):
    return df_daily.set_index('tweet_date')
    

global_df = preprocess_global_data(df_daily)
country_df = preprocess_country_data(df_daily)

important_dates_dict = {'2020-02-11': 'WHO names Covid-19','2020-03-11': 'WHO declares pandemic', '2020-04-02': 'Worldwide cases at 1 million', '2020-04-13': 'US ceases WHO funding','2020-04-17': 'First Moderna trials', '2020-04-24': 'ACT-A announced', '2020-10-02': 'Trump infected'}

def add_annotations(fig):
    for i, date in enumerate(important_dates_dict):
        curr_date_row = global_df.loc[date]
        fear = curr_date_row['fear_intensity']
        angle = 20
        y_offset = -50
        if (i % 2 == 0):
            y_offset=75
            angle=-20
        fig.add_annotation(x=date, y=fear,
            ayref="pixel",
            text=important_dates_dict[date],
            showarrow=True,
            arrowhead=1,
            ay=y_offset,
            textangle=angle)

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

    #October 2 - Trump infected

    # fig.add_annotation(x=2, y=5,
    #         text="Text annotation with arrow",
    #         showarrow=True,
    #         arrowhead=1)
    fig.update_xaxes(ticklabelmode="period")

    add_annotations(fig)
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
    fig.add_scatter(x=pd.to_datetime([selected_date, selected_date, selected_date, selected_date]), y=selected_country_df.loc[pd.to_datetime(selected_date)], name='Current Day', mode='lines+markers',marker=dict(size=10))
    fig.update_layout(clickmode='event+select')
    fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    )

    fig.update_xaxes(ticklabelmode="period")
    
    add_annotations(fig)

    return fig



#plot_global_emotions(pd.to_datetime('2020-01-27')).show()
