import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np
import pandas as pd
import plotly.express as px

def get_graph():

    buffer = BytesIO()
    plt.savefig(buffer, format='png', transparent=True, dpi=300)
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def bar_graph(x, y):

    plt.switch_backend('AGG')
    plt.figure(figsize=(9,4), facecolor="#1F2126")
    #plt.title('Bar Graph')
    plt.bar(x, y, color="#96B7FF")
    plt.xticks(rotation=0)
    plt.tight_layout()
    ax = plt.gca()
    ax.set_facecolor("#1F2126")
    ax.spines['bottom'].set_color("white")
    ax.spines['left'].set_color("white")
    ax.spines['top'].set_color("#1F2126")
    ax.spines['right'].set_color("#1F2126")
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    if (len(y) > 0):
        avg = sum(y)/len(y)
        ax.axhline(avg, color='#F2CD49', linewidth=2)
    
    #plt.plot(x, y, color="#F2CD49")
    plt.bar_label(ax.containers[0], label_type='center')
    
    graph = get_graph()
    return graph

def line_graph(x, y, change):

    plt.switch_backend('AGG')
    plt.figure(figsize=(2.5,.5), facecolor="#1F2126")

    if change > 0:
        plt.plot(x, y, color="#58E767")
    elif change < 0:
        plt.plot(x, y, color="#FC5151")
    else:
        plt.plot(x, y, color="#FFFFFF")
        
    plt.tight_layout()
    ax = plt.gca()
    plt.gca().set_position((0, 0, 1, 1))
    ax.set_facecolor("#1F2126")
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.xticks([])
    plt.yticks([])
    
    graph = get_graph()
    return graph

# Define a function that takes in two lists of data points and generates a radar chart
def radar_chart(labels, results, date):
    # Create a pandas DataFrame from the data
    df = pd.DataFrame(dict(Result=results, Test=labels))
    
    # Create the radar chart with Plotly
    fig = px.line_polar(df, r='Result', theta='Test', line_close=True)
    
    # Update the style of the chart
    fig.update_traces(line=dict(color='#96b7ff', width=2))
    # Update the layout of the figure to set the background color and add a title
    fig.update_layout(
        # Set the title text, font color, and size
        title={
            'text': f'Results for {date}',
            'font': {
                'color': '#ffffff',
                'size': 24
            },
            # Set the position of the title
            'x': 0.005,
            'y': 0.95
        },
        # Set the background color of the plot
        paper_bgcolor='#1f2126',
        # Update the styling of the radial axis
        polar=dict(
            # Set the background color of the circular chart
            bgcolor='#1f2126',
            radialaxis=dict(
                # Set the font color of the radial axis labels
                tickfont=dict(color='#ffffff')
            ),
            # Update the styling of the angular axis
            angularaxis=dict(
                # Set the font color of the angular axis labels
                tickfont=dict(color='#ffffff')
            )
        )
    )
    
    # Set the config of the figure to make it non-interactive
    # fig.update_config({'displayModeBar': False})
    
    # Convert the figure to a HTML string and return it
    # displayModeBar False gets rid of the menu (download as png, zoom)
    graph = fig.to_html(full_html=False, config={'displayModeBar': False})
    return graph