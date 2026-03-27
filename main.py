import fastf1
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#Load Session data
YEAR = 2023
GP = 'Silverstone'
SESSION = 'R' # R = Race | Q = Qualifying | FP1 = Free Practice 1 | FP2 = Free Practice 2 | FP3 = Free Practice 3

session = fastf1.get_session(YEAR, GP, SESSION)
session.load()

lap = session.laps.pick_fastest()
pos = lap.get_pos_data()

circuit_info = session.get_circuit_info()

def rotate(xy, *, angle):
    rot_matrix = np.array([[np.cos(angle), np.sin(angle)],
                           [-np.sin(angle), np.cos(angle)]])
    return xy @ rot_matrix

track = pos.loc[:, ['X', 'Y']].to_numpy()
track_angle = circuit_info.rotation / 180 * np.pi
rotated_track = rotate(track, angle=track_angle)

W, H = 1000, 800
MARGIN = 40

min_x, min_y = rotated_track.min(axis=0)
max_x, max_y = rotated_track.max(axis=0)

span_x = max_x - min_x
span_y = max_y - min_y
scale = min((W - 2*MARGIN) / span_x, (H - 2*MARGIN) / span_y)

pts = []
for x, y in rotated_track:
    sx = MARGIN + (x - min_x) * scale
    sy = MARGIN + (y - min_y) * scale
    pts.append((sx, sy))

x_cords, y_cords = zip(*pts)

# Interpolating the position data to have a common time axis for all drivers
start = session.laps['LapStartTime'].min()
end = max(data['SessionTime'].max() for data in session.pos_data.values())

time_axis = pd.timedelta_range(start=start, end=end, freq='200ms')

x_interp = {}
y_interp = {}

for driver, data in session.pos_data.items():
    driver_data = data.set_index('SessionTime')

    x = driver_data['X'].interpolate(method='index')
    y = driver_data['Y'].interpolate(method='index')

    x_interp[driver] = np.interp(time_axis.total_seconds(), driver_data.index.total_seconds(), x)
    y_interp[driver] = np.interp(time_axis.total_seconds(), driver_data.index.total_seconds(), y)

x_scaled = {}
y_scaled = {}

for driver in session.pos_data.keys():
    xy = np.column_stack([x_interp[driver], y_interp[driver]])
    rotated = rotate(xy, angle=track_angle)
    x_scaled[driver] = MARGIN + (rotated[:, 0] - min_x) * scale
    y_scaled[driver] = MARGIN + (rotated[:, 1] - min_y) * scale

frames = []

for i in range(len(time_axis)):
    x_pos = []
    y_pos = []

    for driver in session.pos_data.keys():
        x_pos.append(x_scaled[driver][i])
        y_pos.append(y_scaled[driver][i])

    frames.append(go.Frame
                  (data=[go.Scatter(x=x_pos, y=y_pos, mode='markers')],
                   traces=[1]
                   ))

fig = go.Figure(
    data=[go.Scatter(x=x_cords, y=y_cords, mode='lines', line=dict(color='white', width=3)),
          go.Scatter(x=frames[0].data[0].x, y=frames[0].data[0].y, mode='markers')
          ],
    frames=frames
)

fig.update_layout(
    paper_bgcolor='black',
    plot_bgcolor='black',
    showlegend=False,
    xaxis=dict(visible=False, range=[0, W]),
    yaxis=dict(visible=False, range=[0, H]),
    updatemenus=[dict(
        type="buttons",
        buttons=[dict(
            label="Play",
            method="animate",
            args=[None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}]
        )]
    )]
)

fig.show()

print(session.laps['LapStartTime'].min())