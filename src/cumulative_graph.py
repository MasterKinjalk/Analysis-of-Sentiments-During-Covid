import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from worldmap import df_daily
from stacked_graph import emotion_colors


def preprocess_global_data(df):
    df["tweet_date"] = pd.to_datetime(df["tweet_date"])
    df.sort_values("tweet_date", inplace=True)
    grouped_df = (
        df.drop(columns="country/region")
        .groupby("tweet_date")
        .mean()
        .sort_values("tweet_date")
    )

    return grouped_df


def preprocess_country_data(df):
    df["tweet_date"] = pd.to_datetime(df["tweet_date"])
    return df.set_index("tweet_date")


def preprocess_cum_global_data(df):
    df["tweet_date"] = pd.to_datetime(df["tweet_date"])
    df.sort_values("tweet_date", inplace=True)
    grouped_df = (
        df.drop(columns="country/region")
        .groupby("tweet_date", as_index=False)
        .mean()
        .sort_values("tweet_date")
    )

    return grouped_df


def plot_cumulative_global_emotions():
    global_df_cum = preprocess_cum_global_data(df_daily)
    df_cumulative = global_df_cum

    window_size = 6  # Define the window size for the rolling mean
    for col in df_cumulative.columns[1:]:  # Skip the timestamp column
        df_cumulative[col] = (
            df_cumulative[col].rolling(window=window_size, min_periods=1).mean()
        )

    for col in df_cumulative.columns[1:]:
        df_cumulative[col] = df_cumulative[col].cumsum(axis=0)
    fig_cumulative = go.Figure()

    for col in df_cumulative.columns[1:]:
        fig_cumulative.add_trace(
            go.Scatter(
                x=df_cumulative[df_cumulative.columns[0]],
                y=df_cumulative[col],
                mode="lines",
                name=col,
                stackgroup="one",
                line=dict(width=0.5),
                fill="tonexty",
                fillcolor=emotion_colors.get(col, "rgba(0,0,0,0.4)"),
            )
        )

    fig_cumulative.update_layout(
        title="Cumulative Emotional Intensity Over Time",
        xaxis_title="Time (Days)",
        yaxis_title="Cumulative Emotion Intensity",
        plot_bgcolor="white",
    )

    return fig_cumulative


def plot_cumulative_country_emotions(country):
    country_df = preprocess_country_data(df_daily)
    country_df_cum = country_df.reset_index(drop=False)
    selected_country_df = country_df_cum[
        country_df_cum["country/region"] == country
    ].drop(columns="country/region")
    title = "Emotional Intensity over Time for " + country

    fig_cumulative = go.Figure()

    for col in selected_country_df.columns[1:]:
        selected_country_df[col] = selected_country_df[col].cumsum()

    for col in selected_country_df.columns[1:]:
        fig_cumulative.add_trace(
            go.Scatter(
                x=selected_country_df[selected_country_df.columns[0]],
                y=selected_country_df[col],
                mode="lines",
                name=col,
                stackgroup="one",
                line=dict(width=0.5),
                fill="tonexty",
                fillcolor=emotion_colors.get(col, "rgba(0,0,0,0.4)"),
            )
        )

    fig_cumulative.update_layout(
        title=title,
        xaxis_title="Time (Days)",
        yaxis_title="Cumulative Emotion Intensity",
        plot_bgcolor="white",
    )

    return fig_cumulative
