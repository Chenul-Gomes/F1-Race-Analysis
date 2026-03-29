import webbrowser
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
        consistency (pd.Series): Series mapping driver codes to their lap time consistency (standard deviation of lap times).
    """
    clean_laps = session.laps.pick_quicklaps()
    clean_laps['LapTimeSec'] = clean_laps['LapTime'].dt.total_seconds()
    consistency = clean_laps.groupby('Driver')['LapTimeSec'].std()

    return consistency

def plot_consistency(session):
    """
    Build and display a box plot of lap time consistency for each driver in the session.

    Args:
        session: FastF1 session object.

    Returns:
        None
    """
    clean_laps = session.laps.pick_quicklaps()
    clean_laps['LapTimeSec'] = clean_laps['LapTime'].dt.total_seconds()

    fig = go.Figure()

    # sort drivers by median lap time so fastest appear first
    driver_order = clean_laps.groupby('Driver')['LapTimeSec'].median().sort_values().index

    for driver in driver_order:
        driver_laps = clean_laps[clean_laps['Driver'] == driver]
        color = '#' + session.get_driver(driver)['TeamColor']
        fig.add_trace(go.Box(y=driver_laps['LapTimeSec'], marker_color=color))

    fig.update_layout(
        title='Lap Time Consistency by Driver',
        xaxis_title = 'Driver',
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
    Degradation is estimated by performing a linear regression of lap time against tyre life for each driver
    and taking the slope as the degradation rate (in seconds per lap).

    Args:
        session: FastF1 session object.

    Returns:
        degradation (dict): Dictionary mapping driver codes to their degradation stats, including slope, intercept,
                            r_value, p_value, and std_err.
    """

    clean_laps  = session.laps.pick_quicklaps()
    clean_laps['LapTimeSec'] = clean_laps['LapTime'].dt.total_seconds()

    results = {}

    for driver in clean_laps['Driver'].unique():
        driver_laps = clean_laps[clean_laps['Driver'] == driver].sort_values('TyreLife')
        slope, intercept, r_value, p_value, std_err = linregress(driver_laps['TyreLife'], driver_laps['LapTimeSec'])
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
    Build and display a horizontal bar chart of tyre degradation rates for each driver in the session.
    
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
            marker_color=color,
            name=driver
        ))

    fig.update_layout(
        title='Tyre Degradation Analysis',
        xaxis_title ='Degradation Rate (s/lap)',
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