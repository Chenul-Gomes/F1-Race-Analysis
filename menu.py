"""
Menu module for selecting F1 session parameters interactively.
Presents dropdown menus for year, Grand Prix, and session type.
"""

import logging

import fastf1
import questionary as q

logging.getLogger('fastf1').setLevel(logging.ERROR)


def get_user_selection():
    """
    Prompt the user to select a year, Grand Prix, and session type.

    Returns:
        tuple: A tuple of (year (int), grand_prix (str),
            session_type (str), run_analysis (bool))
    """
    year = q.select(
        "Select a year:",
        choices=['2018', '2019', '2020', '2021', '2022',
                 '2023', '2024', '2025', '2026']
    ).ask()

    schedule = fastf1.get_event_schedule(int(year), include_testing=False)
    gps = schedule['EventName'].tolist()
    grand_prix = q.select("Select a Grand Prix:", choices=gps).ask()

    session_type = q.select(
        "Select a session:",
        choices=['Race', 'Qualifying', 'FP1', 'FP2', 'FP3']
    ).ask()

    run_analysis = q.confirm(
        "Calculate driver consistency scores? (Warning: this may take a few minutes)"
    ).ask()

    run_lap_time_prediction = q.confirm(
        "Train a machine learning model to predict lap times?"
    ).ask()

    return int(year), grand_prix, session_type, run_analysis, run_lap_time_prediction