"""
F1 Race Simulation
Loads FastF1 session data and builds an interactive race simulation
showing all driver positions on track in real time.
"""

import fastf1

from track import get_track_data
from simulation import get_simulation_data
from visualisation import build_and_show
from driver_analysis import plot_overall_consistency
from menu import get_user_selection


# Load session data
year, gp, session_type, run_analysis = get_user_selection()
session = fastf1.get_session(year, gp, session_type)
session.load()

x_cords, y_cords, min_x, min_y, scale, track_angle = get_track_data(session)

frames, driver_colors = get_simulation_data(
    session, track_angle, min_x, min_y, scale
)

if run_analysis:
    plot_overall_consistency(session)

build_and_show(x_cords, y_cords, frames)