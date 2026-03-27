import numpy as np

from config import W, H, MARGIN

def rotate(xy, *, angle):
    """
    Rotate 2D points by a given angle in radians.
    The rotation is counter-clockwise for positive angles.

    Args:
        xy (np.ndarray): Array of shape (N, 2) containing X and Y coordinates.
        angle (float): Rotation angle in radians.

    Returns:
        np.ndarray: Rotated array of shape (N, 2).
    """
    rot_matrix = np.array([[np.cos(angle), np.sin(angle)],
                           [-np.sin(angle), np.cos(angle)]])
    
    return xy @ rot_matrix

def get_track_data(session):
    """
    Get track coordinates and transformation parameters for plotting.

    Args:
        session: FastF1 session object.
        
    Returns:
        x_cords (list): List of X coordinates for the track.
        y_cords (list): List of Y coordinates for the track.
        min_x (float): Minimum X value of the track.
        min_y (float): Minimum Y value of the track.
        scale (float): Scaling factor for the track.
        track_angle (float): Rotation angle of the track in radians.
    """

    # use fastest lap for the most complete and clean track outline
    lap = session.laps.pick_fastest()
    pos = lap.get_pos_data()

    circuit_info = session.get_circuit_info()

    track = pos.loc[:, ['X', 'Y']].to_numpy()
    # rotate track to match circuit's real-world orientation
    track_angle = circuit_info.rotation / 180 * np.pi
    rotated_track = rotate(track, angle=track_angle)

    min_x, min_y = rotated_track.min(axis=0)
    max_x, max_y = rotated_track.max(axis=0)

    span_x = max_x - min_x
    span_y = max_y - min_y
    # scale track to fit within the window dimensions while preserving aspect ratio
    scale = min((W - 2*MARGIN) / span_x, (H - 2*MARGIN) / span_y)

    pts = []
    for x, y in rotated_track:
        sx = MARGIN + (x - min_x) * scale
        sy = MARGIN + (y - min_y) * scale
        pts.append((sx, sy))

    x_cords, y_cords = zip(*pts)

    return x_cords, y_cords, min_x, min_y, scale, track_angle