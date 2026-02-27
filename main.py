import fastf1
import arcade
import numpy as np

session = fastf1.get_session(2023, 'Monaco', 'R')
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

class TrackWindow(arcade.Window):
    def __init__(self):
        super().__init__(W, H, "FastF1 Track - Arcade")
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        arcade.draw_polygon_outline(pts, arcade.color.WHITE, 2)

TrackWindow().run()
