# Emotional Intensity Visualization

This project utilizes a dataset located in the `/processedData` folder. The dataset comprises several columns that capture various aspects of emotional intensity derived from tweets. Here's a breakdown of the dataset columns:

- `tweet_timestamp`: The timestamp of the tweet.
- `country/region`: The country or region from which the tweet was posted.
- `fear_intensity`: Numeric value representing the intensity of fear expressed in the tweet.
- `anger_intensity`: Numeric value representing the intensity of anger expressed in the tweet.
- `happiness_intensity`: Numeric value representing the intensity of happiness expressed in the tweet.
- `sadness_intensity`: Numeric value representing the intensity of sadness expressed in the tweet.
- `tweet_date`: The date the tweet was posted.

## Visualization with Plotly and Dash

The project leverages Plotly to create chloropleth maps and Dash to build an interactive data app. It consists of two main Python scripts:

1. **worldMap.py**
   - Preprocesses the data for visualization.
   - Creates the chloropleth maps to represent the data geographically.

2. **dashApp.py**
   - Initializes and runs the Dash application.
   - Constructs web components and integrates a slider for dynamic user interaction.
   - Updates the visualizations based on user interactions.

## Getting Started

To set up the project, follow these steps:

### Install Dependencies

First, install the required Python libraries by running:

```
pip install -r requirements.txt
```
```
python dashApp.py
```

After running the command, please allow a couple of minutes for the application to load in the browser. Given the dataset's size (approximately 1GB), it takes some time to process and render the visualizations.