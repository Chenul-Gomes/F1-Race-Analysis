"""
This module contains functions to prepare features, train a machine learning
model, and visualize predictions for F1 lap times based on session data.
The model uses a Random Forest Regressor to predict lap times based on various
features such as tyre life, air temperature, track temperature, fuel load,
compound type, and driver identity. The predictions are visualized using
Plotly, showing the relationship between actual and predicted lap times.
"""

import os
import webbrowser

import pandas as pd
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split


def prepare_features(session):
    """
    Prepare features for machine learning model training.
    Combines lap data with weather data, calculates fuel load,
    and encodes categorical variables.

    Args:
        session: A FastF1 session object containing lap and weather data.

    Returns:
        A DataFrame with features and target variable (LapTimeSec)
        for model training.
    """
    laps = session.laps.copy()
    weather = session.weather_data.copy()

    # merge weather data onto laps by nearest timestamp
    laps_with_weather = pd.merge_asof(
        laps.sort_values('LapStartTime'),
        weather.sort_values('Time'),
        left_on='LapStartTime',
        right_on='Time'
    )

    # estimate fuel load — cars start with ~110kg, burning ~1.5kg per lap
    laps_with_weather['FuelLoad'] = (
        110 - (laps_with_weather['LapNumber'] * 1.5)
    )
    laps_with_weather['LapTimeSec'] = (
        laps_with_weather['LapTime'].dt.total_seconds()
    )
    laps_with_weather = laps_with_weather.dropna(
        subset=['LapTimeSec', 'TyreLife', 'AirTemp']
    )

    # one-hot encode categorical variables for the ML model
    laps_with_weather = pd.get_dummies(
        laps_with_weather,
        columns=['Compound', 'Driver']
    )

    feature_cols = (
        ['TyreLife', 'AirTemp', 'TrackTemp', 'FuelLoad']
        + [col for col in laps_with_weather.columns
           if col.startswith('Compound_')]
        + [col for col in laps_with_weather.columns
           if col.startswith('Driver_')]
    )

    return laps_with_weather[feature_cols + ['LapTimeSec']]


def train_model(session):
    """
    Train a machine learning model to predict lap times based on
    session data.

    Args:
        session: A FastF1 session object containing lap and weather data.

    Returns:
        model: The trained Random Forest Regressor model.
        X_test: The test set features.
        y_test: The test set target variable (actual lap times).
        y_pred: The predicted lap times from the model.
        mae: Mean Absolute Error of the model predictions.
        r2: R² score of the model predictions.
    """
    df = prepare_features(session)

    X = df.drop(columns=['LapTimeSec'])
    y = df['LapTimeSec']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    return model, X_test, y_test, y_pred, mae, r2, df


def plot_predictions(session, y_test, y_pred, mae, r2, df, X_test):
    """
    Plot actual vs predicted lap times using Plotly, and display
    the plot in a web browser.

    Args:
        session: A FastF1 session object.
        y_test: The actual lap times from the test set.
        y_pred: The predicted lap times from the model.
        mae: Mean Absolute Error of the model predictions.
        r2: R² score of the model predictions.
        df: The DataFrame containing the prepared features.
        X_test: The test set features.

    Returns:
        None
    """
    # recover driver names from one-hot encoded columns
    driver_cols = [col for col in df.columns if col.startswith('Driver_')]
    drivers = df.loc[X_test.index, driver_cols].idxmax(axis=1).str.replace('Driver_', '')

    colors = [
        '#' + session.get_driver(driver)['TeamColor']
        for driver in drivers
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[y_test.min(), y_test.max()],
        y=[y_test.min(), y_test.max()],
        mode='lines',
        line=dict(color='white', dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=y_test,
        y=y_pred,
        mode='markers',
        marker=dict(color=colors, size=5),
        customdata=list(zip(abs(y_test.values - y_pred), drivers)),
        hovertemplate=(
            'Actual: %{x:.3f} sec<br>'
            'Predicted: %{y:.3f} sec<br>'
            'Error: %{customdata[0]:.3f} sec<br>'
            'Driver: %{customdata[1]}<extra></extra>'
        )
    ))

    fig.update_layout(
        title=(
            f'Predicted vs Actual Lap Times'
            f'<br>MAE: {mae:.3f} sec, R²: {r2:.3f}'
        ),
        xaxis_title='Actual Lap Time (sec)',
        yaxis_title='Predicted Lap Time (sec)',
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        showlegend=False
    )

    os.makedirs('output', exist_ok=True)
    html = fig.to_html(include_plotlyjs='cdn', full_html=True)
    with open('output/plot_predictions.html', 'w') as f:
        f.write(html)

    filepath = os.path.abspath('output/plot_predictions.html')
    webbrowser.open(filepath)