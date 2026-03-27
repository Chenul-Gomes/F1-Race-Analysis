# F1 Race Simulation

A Python project that fetches and animates Formula 1 race data. This project uses the `fastf1` library to pull real telemetry and position data, and `plotly` to render an interactive, animated playback of all 20 cars moving around the circuit in real time.

Currently configured to visualize the 2021 Silverstone Grand Prix, but can be easily modified to replay any year, track, or session via `config.py`.

## Features

- Animated race simulation with all 20 drivers
- Team colours for each driver using official F1 colour codes
- Interactive play button to control the animation
- Smooth position interpolation for realistic movement
- Supports any race, year, or session by editing `config.py`

## Tech Stack

- **Python**
- **FastF1** — for accessing F1 timing, telemetry, and position data
- **NumPy & Pandas** — for data manipulation, matrix rotations, and time-based interpolation
- **Plotly** — for rendering the animated, interactive track visualization

## Project Structure

```
├── main.py            # Entry point — ties all modules together
├── config.py          # Configuration settings (year, GP, session, window size)
├── track.py           # Track geometry loading, rotation, and scaling
├── simulation.py      # Driver position interpolation and Plotly frame building
├── visualisation.py   # Figure creation and HTML export
└── requirements.txt   # Python dependencies
```

## Installation

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/Chenul-Gomes/F1-Race-Analysis
   cd F1-Race-Analysis
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the simulation:
   ```bash
   python main.py
   ```

The simulation will open automatically in your default web browser.

## Configuration

To simulate a different race, edit the following variables in `config.py`:

```python
YEAR = 2021
GP = 'Silverstone'
SESSION = 'R'  # R = Race | Q = Qualifying | FP1/FP2/FP3 = Practice
```