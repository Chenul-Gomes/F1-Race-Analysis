"""
This module contains functions for analyzing driver performance in a FastF1 session,
including lap time consistency, tyre degradation, and braking precision.
Each metric is visualized using Plotly and combined into an overall consistency score
to rank drivers from most to least consistent.
"""

import webbrowser

import pandas as pd
import plotly.graph_objects as go
from scipy.stats import linregress


def lap_time_consistency(session):
    """
    Calculate lap time consistency for each driver in the session.
    Consistency is defined as the standard deviation of lap times for each driver,
    with lower values indicating more consistent performance.

    Args:
        session: FastF1 session object.

    Returns:
        consistency (pd.Series): Series mapping driver codes to their
            lap time consistency (standard deviation of lap times).
    """
    clean_laps = session.laps.pick_quicklaps()
    clean_laps['LapTimeSec'] = clean_laps['LapTime'].dt.total_seconds()
    consistency = clean_laps.groupby('Driver')['LapTimeSec'].std()

    return consistency


def plot_consistency(session):
    """
    Build and display a box plot of lap time consistency for each driver
    in the session.

    Args:
        session: FastF1 session object.

    Returns:
        None
    """
    clean_laps = session.laps.pick_quicklaps()
    clean_laps['LapTimeSec'] = clean_laps['LapTime'].dt.total_seconds()

    fig = go.Figure()

    # sort drivers by median lap time so fastest appear first
    driver_order = (
        clean_laps.groupby('Driver')['LapTimeSec']
        .median()
        .sort_values()
        .index
    )

    for driver in driver_order:
        driver_laps = clean_laps[clean_laps['Driver'] == driver]
        color = '#' + session.get_driver(driver)['TeamColor']
        fig.add_trace(go.Box(y=driver_laps['LapTimeSec'], marker_color=color))

    fig.update_layout(
        title='Lap Time Consistency by Driver',
        xaxis_title='Driver',
        yaxis_title='Lap Time (seconds)',
        showlegend=False,
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='white')
    )

    html = fig.to_html(include_plotlyjs='cdn', full_html=True)
    with open('consistency.html', 'w') as f:
        f.write(html)

    webbrowser.open('consistency.html')


def tyre_degradation(session):
    """
    Calculate tyre degradation for each driver in the session.
    Degradation is estimated by performing a linear regression of lap time
    against tyre life for each driver and taking the slope as the degradation
    rate (in seconds per lap).

    Args:
        session: FastF1 session object.

    Returns:
        results (dict): Dictionary mapping driver codes to their degradation
            stats, including slope, intercept, r_value, p_value, and std_err.
    """
    clean_laps = session.laps.pick_quicklaps()
    clean_laps['LapTimeSec'] = clean_laps['LapTime'].dt.total_seconds()

    results = {}

    for driver in clean_laps['Driver'].unique():
        driver_laps = (
            clean_laps[clean_laps['Driver'] == driver]
            .sort_values('TyreLife')
        )
        slope, intercept, r_value, p_value, std_err = linregress(
            driver_laps['TyreLife'], driver_laps['LapTimeSec']
        )
        results[driver] = {
            'slope': slope,
            'intercept': intercept,
            'r_value': r_value,
            'p_value': p_value,
            'std_err': std_err
        }

    return results


def plot_tyre_degradation(session):
    """
    Build and display a horizontal bar chart of tyre degradation rates
    for each driver in the session.

    Args:
        session: FastF1 session object.

    Returns:
        None
    """
    results = tyre_degradation(session)

    fig = go.Figure()

    sorted_drivers = sorted(results.items(), key=lambda x: x[1]['slope'])

    for driver, stats in sorted_drivers:
        color = '#' + session.get_driver(driver)['TeamColor']
        fig.add_trace(go.Bar(
            x=[stats['slope']],
            y=[driver],
            orientation='h',
            marker_color=color
        ))

    fig.update_layout(
        title='Tyre Degradation Analysis',
        xaxis_title='Degradation Rate (s/lap)',
        yaxis_title='Driver',
        showlegend=False,
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='white')
    )

    html = fig.to_html(include_plotlyjs='cdn', full_html=True)
    with open('tyre_degradation.html', 'w') as f:
        f.write(html)

    webbrowser.open('tyre_degradation.html')


def braking_precision(session):
    """
    Calculate braking precision for each driver in the session.
    Braking precision is estimated by analyzing the variability of braking
    points across all laps for each driver. The standard deviation of braking
    points is calculated in distance bins along the track, and the average
    variability across bins is taken as the braking precision score
    (lower is better).

    Args:
        session: FastF1 session object.

    Returns:
        driver_scores (dict): Dictionary mapping driver codes to their braking
            precision scores (average variability in braking points).
    """
    driver_scores = {}

    for driver in session.laps['Driver'].unique():
        driver_laps = session.laps.pick_drivers(driver).pick_quicklaps()

        all_braking_points = []
        for _, lap in driver_laps.iterlaps():
            tel = lap.get_telemetry().add_distance()
            brake_start = tel['Brake'].diff() == True
            points = tel[brake_start]['Distance'].values
            all_braking_points.extend(points)

        if len(all_braking_points) == 0:
            continue

        braking_series = pd.Series(all_braking_points)
        bins = pd.cut(braking_series, bins=20)
        driver_scores[driver] = (
            braking_series.groupby(bins).std().dropna().mean()
        )

    return driver_scores


def plot_braking_precision(session):
    """
    Build and display a horizontal bar chart of braking precision scores
    for each driver in the session.

    Args:
        session: FastF1 session object.

    Returns:
        None
    """
    scores = braking_precision(session)

    fig = go.Figure()

    sorted_drivers = sorted(scores.items(), key=lambda x: x[1])

    for driver, score in sorted_drivers:
        color = '#' + session.get_driver(driver)['TeamColor']
        fig.add_trace(go.Bar(
            x=[score],
            y=[driver],
            orientation='h',
            marker_color=color
        ))

    fig.update_layout(
        title='Braking Precision Analysis',
        xaxis_title='Average Braking Variability (m)',
        yaxis_title='Driver',
        showlegend=False,
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='white')
    )

    html = fig.to_html(include_plotlyjs='cdn', full_html=True)
    with open('braking_precision.html', 'w') as f:
        f.write(html)

    webbrowser.open('braking_precision.html')


def normalize(value, all_values):
    """
    Normalize a value to a 0-1 scale based on the range of all values.
    For metrics where lower is better (like standard deviation or degradation
    slope), the formula is inverted so that higher normalized scores indicate
    better performance.

    Args:
        value (float): The value to normalize.
        all_values (iterable): All values in the dataset for this metric,
            used to determine the min and max for normalization.

    Returns:
        normalized (float): The normalized value on a 0-1 scale,
            where higher is better.
    """
    mn = min(all_values)
    mx = max(all_values)
    return 1 - (value - mn) / (mx - mn)


def overall_consistency_score(session):
    """
    Calculate an overall consistency score for each driver by combining
    lap time consistency, tyre degradation, and braking precision.
    Each metric is normalized to a 0-1 scale, and the overall score is the
    average of the three metrics multiplied by 100 to give a percentage
    (higher is better).

    Args:
        session: FastF1 session object.

    Returns:
        overall_score (dict): Dictionary mapping driver codes to their
            overall consistency scores (0-100%).
    """
    consistency = lap_time_consistency(session)
    degradation = tyre_degradation(session)
    braking = braking_precision(session)

    degradation_slopes = {
        driver: abs(stats['slope'])
        for driver, stats in degradation.items()
    }

    drivers = (
        set(consistency.index)
        & set(degradation_slopes.keys())
        & set(braking.keys())
    )

    overall_score = {}
    for driver in drivers:
        consistency_score = normalize(
            consistency[driver], consistency.values
        )
        degradation_score = normalize(
            degradation_slopes[driver], degradation_slopes.values()
        )
        braking_score = normalize(braking[driver], braking.values())
        overall_score[driver] = (
            (consistency_score + degradation_score + braking_score) / 3 * 100
        )

    return overall_score


def plot_overall_consistency(session):
    """
    Build and display a vertical bar chart of overall consistency scores
    for each driver in the session.

    Args:
        session: FastF1 session object.

    Returns:
        None
    """
    scores = overall_consistency_score(session)

    fig = go.Figure()

    sorted_drivers = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    for driver, score in sorted_drivers:
        color = '#' + session.get_driver(driver)['TeamColor']
        fig.add_trace(go.Bar(
            x=[driver],
            y=[score],
            marker_color=color,
            text=[f'{score:.1f}%'],
            textposition='outside'
        ))

    fig.update_layout(
        title='Overall Driver Consistency Score',
        xaxis_title='Driver',
        yaxis_title='Consistency Score (%)',
        showlegend=False,
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='white')
    )

    html = fig.to_html(include_plotlyjs='cdn', full_html=True)
    with open('overall_consistency.html', 'w') as f:
        f.write(html)

    webbrowser.open('overall_consistency.html')