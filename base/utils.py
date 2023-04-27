import matplotlib.pyplot as plt
import base64
import threading
from io import BytesIO
import numpy as np
import pandas as pd
import scipy.stats as stats
import plotly.graph_objects as go

# Prevents 2 graphs from being rendered at the same time, which resulted
# in garbled info. While one graph is processing, others must wait before
# they are processed.
semaphore = threading.Semaphore(1)

def get_graph():

    buffer = BytesIO()

    plt.savefig(buffer, format='png', transparent=True, dpi=120)

    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()

    return graph


def bar_graph(x, y, T_AVG, G_AVG, P_AVG):

    # Create Lockout
    semaphore.acquire()

    try: 
        plt.switch_backend('AGG')

        if(len(x) > 7):
            plt.figure(figsize=(12,5), facecolor="#1F2126")
            plt.gcf().subplots_adjust(bottom=0.25)
            plt.xticks(rotation=45)
            
        else:
            plt.figure(figsize=(9,3.75), facecolor="#1F2126")
            plt.xticks(rotation=0)

        
        plt.bar(x, y, color="#99C7FF")
        plt.tight_layout()
        ax = plt.gca()
        ax.spines['bottom'].set_color("white")
        ax.spines['left'].set_color("white")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

        if (len(y) > 0):
            avg = sum(y)/len(y)
            roundedAVG = round(avg, 3)
            ax.axhline(avg, color='#F2CD49', linewidth=2, label="Athlete Avg: %.3f" %roundedAVG)

        if (T_AVG != None):
            rounded_T_AVG = round(T_AVG, 3)
            ax.axhline(T_AVG, color='#58E767', linewidth=2, label="Team Avg: %.3f" %rounded_T_AVG)

        if (G_AVG != None):
            rounded_G_AVG = round(G_AVG, 3)
            ax.axhline(G_AVG, color='#0051b5', linewidth=2, label="Gender Avg: %.3f" %rounded_G_AVG)
        
        if (P_AVG != None):
            rounded_P_AVG = round(P_AVG, 3)
            ax.axhline(P_AVG, color='#FC5151', linewidth=2, label="Position Avg: %.3f" %rounded_P_AVG)

        if (ax.containers):
            plt.bar_label(ax.containers[0], label_type='center')

        plt.legend(loc="upper right", labelcolor="white", facecolor="#1C2230", fontsize="x-small")

        graph = get_graph()

        return graph
    
    # Unlock this code
    finally:
        semaphore.release()

def bar_graph_groups(x, y, T_AVG, G_AVG):

    plt.switch_backend('AGG')

    if(len(x) > 7):
        plt.figure(figsize=(12,5), facecolor="#1F2126")
        plt.gcf().subplots_adjust(bottom=0.25)
        plt.xticks(rotation=45)
        
    else:
        plt.figure(figsize=(9,3.75), facecolor="#1F2126")
        plt.xticks(rotation=0)

    
    plt.bar(x, y, color="#99C7FF")
    plt.tight_layout()
    ax = plt.gca()
    ax.spines['bottom'].set_color("white")
    ax.spines['left'].set_color("white")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    if (T_AVG != None):
        rounded_T_AVG = round(T_AVG, 3)
        ax.axhline(T_AVG, color='#58E767', linewidth=2, label="Team Avg: %.3f" %rounded_T_AVG)

    if (G_AVG != None):
        rounded_G_AVG = round(G_AVG, 3)
        ax.axhline(G_AVG, color='#0051b5', linewidth=2, label="Gender Avg: %.3f" %rounded_G_AVG)

    plt.bar_label(ax.containers[0], label_type='center')

    plt.legend(loc="upper right", labelcolor="white", facecolor="#1C2230", fontsize="x-small")

    graph = get_graph()

    return graph

def line_graph(x, y, change, minBetter):

    # Create Lockout
    semaphore.acquire()

    try:
        plt.switch_backend('AGG')
        plt.figure(figsize=(5,1), facecolor="#1F2126")

        # If minBetter is not defined, make it white (bodyweight, body composition, etc)
        if minBetter is None:
            plt.plot(x, y, color="#FFFFFF")

        # Change is increasing
        elif change > 0:
            # If a minimum score is better for a test, make change red
            if minBetter:
                plt.plot(x, y, color="#FC5151")
            # If a minimum score is NOT better for a test, make change green
            elif not minBetter:
                plt.plot(x, y, color="#58E767")

        # Change is decreasing
        elif change < 0:
            # If a minimum score is better for a test, make change green
            if minBetter:
                plt.plot(x, y, color="#58E767")
            # If a minimum score is NOT better for a test, make change red
            elif not minBetter:
                plt.plot(x, y, color="#FC5151")

        # If change = 0, make it white
        else:
            plt.plot(x, y, color="#FFFFFF")
            
        #plt.tight_layout()
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

    # Unlock this code
    finally:
        semaphore.release()

def z_score_graph(x, y): 

    #Create Lockout
    semaphore.acquire()

    try:
        plt.switch_backend('AGG')

        if(len(x) > 7):
            plt.figure(figsize=(12,5), facecolor="#1F2126")
            plt.gcf().subplots_adjust(bottom=0.25)
            plt.xticks(rotation=45)
            
        else:
            plt.figure(figsize=(9,3.75), facecolor="#1F2126")
            plt.xticks(rotation=0)
        
        plt.bar(x, y, color="#99C7FF")
        plt.tight_layout()
        ax = plt.gca()
        ax.spines['bottom'].set_color("white")
        ax.spines['left'].set_color("white")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.set_ylim([0, 100])

        if (len(y) > 0):
            avg = sum(y)/len(y)
            rounded_AVG = round(avg, 3)
            ax.axhline(avg, color='#F2CD49', linewidth=2, label="T-Score Avg: %.3f" %rounded_AVG)
        
        plt.bar_label(ax.containers[0], label_type='center')

        plt.legend(loc="upper right", labelcolor="white", facecolor="#1C2230", fontsize="x-small")

        graph = get_graph()

        return graph
    
    # Unlock this code
    finally:
        semaphore.release()