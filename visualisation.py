import plotly.graph_objects as go
import webbrowser

from config import W, H

def build_and_show(x_cords, y_cords, frames):
    """
    Build the Plotly figure with the track and simulation data, and display it in a web browser.
    Args:
        x_cords (list): List of X coordinates for the track.
        y_cords (list): List of Y coordinates for the track.
        frames (list): List of Plotly frames for the simulation.
    
    Returns:
        None
    """

    # trace 0 = track outline, trace 1 = driver positions at t=0
    fig = go.Figure(
        data=[go.Scatter(x=x_cords, y=y_cords, mode='lines', line=dict(color='white', width=3)), 
              go.Scatter(x=frames[0].data[0].x, y=frames[0].data[0].y, mode='markers')
              ],
        frames=frames
    )

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
            buttons=[dict(
                label="Play",
                method="animate",
                args=[None, {"frame": {"duration": 10, "redraw": True}, "fromcurrent": True}]
            )]
        )]
    )

    html = fig.to_html(include_plotlyjs='cdn')
    # inject CSS to center the figure on a black background
    html = html.replace('<body>', '<body style="margin:0; background:black; display:flex; justify-content:center; align-items:center; height:100vh;">')

    with open('f1_simulation.html', 'w') as f:
        f.write(html)

    webbrowser.open('f1_simulation.html')