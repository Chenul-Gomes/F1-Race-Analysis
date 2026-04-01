"""
Visualisation module for building and displaying the F1 race simulation.
Exports the simulation as an HTML file and opens it in the default web browser.
"""

import glob
import os
import webbrowser

import plotly.graph_objects as go

from config import H, W


def build_and_show(x_cords, y_cords, frames):
    """
    Build the Plotly figure with the track and simulation data,
    and display it in a web browser.

    Args:
        x_cords (list): List of X coordinates for the track.
        y_cords (list): List of Y coordinates for the track.
        frames (list): List of Plotly frames for the simulation.

    Returns:
        None
    """
    # trace 0 = track outline, trace 1 = driver positions at t=0
    track_trace = go.Scattergl(
        x=x_cords, y=y_cords,
        mode='lines',
        line=dict(color='white', width=3)
    )
    driver_trace = go.Scattergl(
        x=frames[0].data[0].x,
        y=frames[0].data[0].y,
        mode='markers'
    )

    fig = go.Figure(data=[track_trace, driver_trace], frames=frames)

    fig.update_layout(
        width=W,
        height=H,
        autosize=False,
        margin=dict(l=50, r=50, t=50, b=50),
        paper_bgcolor='black',
        plot_bgcolor='black',
        showlegend=False,
        xaxis=dict(visible=False, range=[0, W]),
        yaxis=dict(visible=False, range=[0, H]),
        updatemenus=[dict(
            type="buttons",
            active=-1,
            buttons=[dict(
                label="Play",
                method="animate",
                args=[None, {
                    "frame": {"duration": 100, "redraw": True},
                    "fromcurrent": True
                }]
            )]
        )]
    )

    html = fig.to_html(include_plotlyjs='cdn', full_html=True)

    # inject CSS to make entire page black
    html = html.replace(
        '<head>',
        '<head><style>html, body { margin:0; padding:0; background:black; }</style>'
    )

    # inject CSS to center the figure on a black background
    html = html.replace(
        '<body>',
        '<body style="margin:0; padding:0; background:black; '
        'display:flex; justify-content:center; '
        'align-items:center; min-height:100vh;">'
    )

    # prevent auto-play on page load
    html = html.replace(
        '</body>',
        '''<script>
        window.addEventListener("load", function() {
            setTimeout(function() {
                var divs = document.getElementsByClassName("plotly-graph-div");
                if (divs.length > 0) {
                    Plotly.animate(divs[0].id, [], {mode: "immediate"});
                }
            }, 500);
        });
        </script></body>'''
    )

    # ensure output directory exists
    os.makedirs('output', exist_ok=True)

    # clean up old simulation files
    for old_file in glob.glob('output/f1_simulation*.html'):
        os.remove(old_file)

    with open('output/f1_simulation.html', 'w') as f:
        f.write(html)

    filepath = os.path.abspath('output/f1_simulation.html')
    webbrowser.open(filepath)