# F1 Telemetry Visualizer

A Python script that fetches and animates Formula 1 race data. This project uses the `fastf1` library to pull real telemetry and position data, and `plotly` to render an interactive, animated playback of the cars moving around the circuit. 

Currently configured to visualize the 2021 Silverstone Grand Prix, but the variables can be easily modified to replay other years, tracks, and sessions.

## Tech Stack
* **Python**
* **FastF1:** For accessing F1 timing and telemetry data.
* **NumPy & Pandas:** For data manipulation, matrix rotations, and time-based interpolation.
* **Plotly:** For rendering the animated, interactive track visualization.

## Installation

1. Clone this repository to your local machine:
   ```bash
   git clone [https://github.com/Chenul-Gomes/F1-Race-Analysis]
   cd F1-Race-Analysis