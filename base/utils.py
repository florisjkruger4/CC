import matplotlib.pyplot as plt
import base64
from io import BytesIO
import numpy as np
import pandas as pd
import plotly.graph_objects as go

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
    plt.bar(x, y, color="#96B7FF")
    plt.tight_layout()
    ax = plt.gca()
    ax.set_facecolor("#1F2126")
    ax.spines['bottom'].set_color("white")
    ax.spines['left'].set_color("white")
    ax.spines['top'].set_color("#1F2126")
    ax.spines['right'].set_color("#1F2126")
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    if(len(x) > 20):
        plt.xticks(rotation=45)
    elif(len(x) > 40):
        plt.xticks(rotation=90)
    else:
        plt.xticks(rotation=0)

    if (len(y) > 0):
        avg = sum(y)/len(y)
        ax.axhline(avg, color='#F2CD49', linewidth=2)
    
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

# A dictionary of athlete tests and results, a list of nested dictionaries of averages for tests and results, and the selected date are passed
def radar_chart(athlete_results, average_results, date):
    # Create a pandas DataFrame from the athlete date
    df = pd.DataFrame(dict(Result=athlete_results.values(), Test=athlete_results.keys()))
    
    # Create the radar chart with Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=df['Result'], theta=df['Test'], fill='toself', name='Athlete', line=dict(color='#96b7ff', width=2), 
                                  # Customize the hover over info for each date point   
                                  hovertemplate='<b>Result:</b> %{r}<br><b>Test Type:</b> %{theta}<extra></extra>'))
    
    # Colors for team, position, and gender respectively
    average_colors = ['green', 'yellow', 'purple']
    color_index = 0
    for group_dict in average_results:
        group_name = group_dict['group']
        group_results = group_dict['results']
        
        # Create a pandas DataFrame from the group's data
        group_df = pd.DataFrame(dict(Result=group_results.values(), Test=group_results.keys()))

        # Add a trace for the group to the radar chart
        fig.add_trace(go.Scatterpolar(r=group_df['Result'], theta=group_df['Test'], fill='toself', name=group_name, line=dict(color=average_colors[color_index], width=2), 
                                      # Customize the hover over info for each date point  
                                      hovertemplate='<b>Result:</b> %{r}<br><b>Test Type:</b> %{theta}<extra></extra>'))
        # The next trace will have a new color
        color_index += 1

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
    
    # Convert the figure to a HTML string and return it
    # displayModeBar shows the screenshot, zoom, box and lasso select tools
    graph = fig.to_html(full_html=False, config={'displayModeBar': True})
    return graph