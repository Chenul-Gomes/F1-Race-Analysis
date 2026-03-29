"""
F1 Race Simulation
Loads FastF1 session data and builds an interactive race simulation
showing all driver positions on track in real time.
"""

import fastf1

from config import YEAR, GP, SESSION
from track import get_track_data
from simulation import get_simulation_data
from visualisation import build_and_show
from driver_analysis import lap_time_consistency, plot_consistency, tyre_degradation, plot_tyre_degradation

#Load Session data
session = fastf1.get_session(YEAR, GP, SESSION)
session.load()

x_cords, y_cords, min_x, min_y, scale, track_angle = get_track_data(session)

frames, driver_colors = get_simulation_data(session, track_angle, min_x, min_y, scale)

build_and_show(x_cords, y_cords, frames)

plot_consistency(session)

plot_tyre_degradation(session)