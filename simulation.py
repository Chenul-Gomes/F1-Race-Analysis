"""
Simulation module for interpolating driver positions and building
Plotly animation frames for the F1 race simulation.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from config import MARGIN
from track import rotate


def get_simulation_data(session, track_angle, min_x, min_y, scale):
    """
    Get interpolated and scaled position data for all drivers in the session.

    Args:
        session: FastF1 session object.
        track_angle (float): Rotation angle of the track in radians.
        min_x (float): Minimum X value of the track.
        min_y (float): Minimum Y value of the track.
        scale (float): Scaling factor for the track.

    Returns:
        frames (list): List of Plotly frames for the simulation.
        driver_colors (dict): Dictionary mapping drivers to their colors.
    """
    # use race start time to skip installation laps and pre-race wait
    start = session.laps['LapStartTime'].min()
    end = max(data['SessionTime'].max() for data in session.pos_data.values())

    # sample every 500ms to balance smoothness and performance
    time_axis = pd.timedelta_range(start=start, end=end, freq='500ms')

    # interpolate each driver's position onto the common time axis
    x_interp = {}
    y_interp = {}
    for driver, data in session.pos_data.items():
        driver_data = data.set_index('SessionTime')

        x = driver_data['X'].interpolate(method='index')
        y = driver_data['Y'].interpolate(method='index')

        time_seconds = time_axis.total_seconds()
        data_seconds = driver_data.index.total_seconds()
        x_interp[driver] = np.interp(time_seconds, data_seconds, x)
        y_interp[driver] = np.interp(time_seconds, data_seconds, y)

    # rotate and scale driver positions to match the track coordinate system
    x_scaled = {}
    y_scaled = {}
    for driver in session.pos_data.keys():
        xy = np.column_stack([x_interp[driver], y_interp[driver]])
        rotated = rotate(xy, angle=track_angle)
        x_scaled[driver] = MARGIN + (rotated[:, 0] - min_x) * scale
        y_scaled[driver] = MARGIN + (rotated[:, 1] - min_y) * scale

    # fetch official team colours from FastF1
    driver_colors = {}
    for driver in session.pos_data.keys():
        info = session.get_driver(driver)
        driver_colors[driver] = '#' + info['TeamColor']

    frames = []
    for i in range(len(time_axis)):
        x_pos = []
        y_pos = []
        colors = []

        for driver in session.pos_data.keys():
            x_pos.append(x_scaled[driver][i])
            y_pos.append(y_scaled[driver][i])
            colors.append(driver_colors[driver])

        frames.append(go.Frame(
            data=[go.Scattergl(
                x=x_pos,
                y=y_pos,
                mode='markers',
                marker=dict(color=colors, size=10)
            )],
            traces=[1]
        ))

    return frames, driver_colors