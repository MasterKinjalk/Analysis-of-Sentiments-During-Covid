import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from worldmap import df_daily

# Defining specific colors for each emotion
emotion_colors = {
    "fear_intensity": "#309AD6",  # Blue
    "anger_intensity": "#ff8686",  # Red
    "happiness_intensity": "#66B266",  # Green
    "sadness_intensity": "#dbc6ff",  # Purple
}


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


global_df = preprocess_global_data(df_daily)
country_df = preprocess_country_data(df_daily)


def plot_stacked_global_emotions():
    fig_stacked = go.Figure()
    # with normalization
    # df_cumulative = global_df.cumsum(axis=1)
    df_cumulative = global_df.iloc[:, -4:]

    # without normalization
    # df_cumulative = global_df.iloc[:, -4:]
    # print(df_cumulative.head())

    for i, emotion in enumerate(global_df.columns):
        fig_stacked.add_trace(
            go.Scatter(
                x=global_df.index,  # Use the dataframe index as the x-axis
                y=df_cumulative[emotion] if i > 0 else global_df[emotion],
                mode="lines",
                name=emotion,
                stackgroup="one",
                line=dict(width=0.5, color=emotion_colors.get(emotion, "#000")),
                fill="tonexty" if i > 0 else "tozeroy",
                fillcolor=emotion_colors.get(emotion, "#000"),
                hoverinfo="x+y",
                hoveron="points+fills",
            )
        )

    # Enhance the layout
    fig_stacked.update_layout(
        title="Summary of Emotion Flow",
        xaxis=dict(
            title="Time (Days)",
            mirror=True,
            ticks="outside",
            showline=True,
            linecolor="#000",
        ),
        yaxis=dict(
            title="Emotional Intensity",
            mirror=True,
            ticks="outside",
            showline=True,
            linecolor="#000",
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        hovermode="x unified",
        legend=dict(
            title="Emotions",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    return fig_stacked


def plot_stacked_country_emotions(country):
    selected_country_df = country_df[country_df["country/region"] == country].drop(
        columns="country/region"
    )
    title = "Emotional Intensity over Time for " + country

    # Assume data is already in the correct format
    df_cumulative = selected_country_df

    fig_stacked = go.Figure()

    for i, emotion in enumerate(df_cumulative.columns):
        fig_stacked.add_trace(
            go.Scatter(
                x=df_cumulative.index,  # Use the dataframe index as the x-axis
                y=df_cumulative[emotion],
                mode="lines",
                name=emotion,
                stackgroup="one",
                line=dict(width=0.5),
                fill="tonexty" if i > 0 else "tozeroy",
                fillcolor=emotion_colors.get(emotion, "#000"),
                hoverinfo="x+y",
                hoveron="points+fills",
            )
        )

    # Enhance the layout
    fig_stacked.update_layout(
        title=title,
        xaxis=dict(
            title="Time (Days)",
            mirror=True,
            ticks="outside",
            showline=True,
            linecolor="#000",
        ),
        yaxis=dict(
            title="Emotional Intensity",
            mirror=True,
            ticks="outside",
            showline=True,
            linecolor="#000",
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        hovermode="x unified",
        legend=dict(
            title="Emotions",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    return fig_stacked
