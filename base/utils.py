import matplotlib.pyplot as plt
import base64
from io import BytesIO

def get_graph():

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def bar_graph(x, y):

    plt.switch_backend('AGG')
    plt.figure(figsize=(8,5), facecolor="#171C27")
    #plt.title('Bar Graph')
    plt.bar(x, y, color="#96B7FF")
    plt.xticks(rotation=45)
    plt.xlabel('Dates', color="white")
    plt.ylabel('Units', color="white")
    plt.tight_layout()
    ax = plt.gca()
    ax.set_facecolor("#171C27")
    ax.spines['bottom'].set_color("white")
    ax.spines['left'].set_color("white")
    ax.spines['top'].set_color("#171C27")
    ax.spines['right'].set_color("#171C27")
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    plt.bar_label(ax.containers[0], label_type='center')
    
    graph = get_graph()
    return graph

def line_graph(x, y):

    plt.switch_backend('AGG')
    plt.figure(figsize=(8,5), facecolor="#171C27")
    #plt.title('Bar Graph')
    plt.plot(x, y, color="#96B7FF")
    plt.xticks(rotation=45)
    plt.xlabel('Dates', color="white")
    plt.ylabel('Units', color="white")
    plt.tight_layout()
    ax = plt.gca()
    ax.set_facecolor("#171C27")
    ax.spines['bottom'].set_color("white")
    ax.spines['left'].set_color("white")
    ax.spines['top'].set_color("#171C27")
    ax.spines['right'].set_color("#171C27")
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    
    graph = get_graph()
    return graph