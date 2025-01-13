import sys
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import dash
import numpy as np
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import threading
import time
from pymongo import MongoClient  # Import MongoClient to connect to MongoDB

# MongoDB connection setup
mongo_client = MongoClient(os.getenv('MONGO_URL', 'mongodb://localhost:27017/'))  # Use the URL from environment variable or default to localhost
db = mongo_client["heart_diseases"]  # Use your database name from config
collection = db['patients']  # Use your collection name

output_dir = os.path.abspath(os.path.dirname(__file__))

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

sns.set(style="whitegrid")

# Create a Dash application
app = dash.Dash(__name__)

# Create a new empty DataFrame
new_data = pd.DataFrame(columns=['age', 'output', 'cp'])

def fetch_real_time_data():
    global new_data
    while True:
        # Fetch the latest data from MongoDB
        recent_patients = collection.find({"timestamp": {"$gte": int(time.time()) - 3600}})
        new_entries = pd.DataFrame(list(recent_patients))  # Convert to DataFrame
        
        # Log the number of new entries fetched
        print(f"Fetched {len(new_entries)} new entries from the database.")
        print(new_entries)
        
        # Clean the DataFrame (remove unwanted columns)
        if not new_entries.empty:
            new_entries = new_entries[['age', 'output', 'cp']]  # Adjust based on your actual fields
            new_data = pd.concat([new_data, new_entries], ignore_index=True)
        
        time.sleep(5)  # Wait for 5 seconds before fetching new data

# Start the data fetching in a separate thread
threading.Thread(target=fetch_real_time_data, daemon=True).start()

# Define the layout of the dashboard
app.layout = html.Div(style={'height': '100vh', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}, children=[
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # in milliseconds (10 seconds)
        n_intervals=0
    ),
    html.Div(id='update-indicator', style={'padding': '10px', 'textAlign': 'center'}, children=[
        html.Span('Last updated: ', style={'fontWeight': 'bold'}),
        html.Span(id='last-update-time')
    ]),
    html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'flexGrow': 1}, children=[
        html.Div(style={'padding': '10px'}, children=[
            dcc.Graph(id='age-distribution-fig')
        ]),
        html.Div(style={'padding': '10px'}, children=[
            dcc.Graph(id='heart-disease-distribution-fig')
        ]),
        html.Div(style={'padding': '10px'}, children=[
            dcc.Graph(id='chest-pain-analysis-fig')
        ]),
    ]),
])

# Callback to update the figures and the update indicator
@app.callback(
    Output('age-distribution-fig', 'figure'),
    Output('heart-disease-distribution-fig', 'figure'),
    Output('chest-pain-analysis-fig', 'figure'),
    Output('last-update-time', 'children'),
    Input('interval-component', 'n_intervals')  # Trigger the callback every 10 seconds
)
def update_figures(n_intervals):
    # Use only new_data for the visualizations
    concatenated_data = new_data  # Use only the new data from the database

    # Prepare the figures for the dashboard using the new DataFrame
    age_distribution_fig = px.histogram(concatenated_data, x='age', nbins=30, title='Age Distribution', 
                                         labels={'age': 'Age'}, color_discrete_sequence=['blue'])
    
    heart_disease_distribution_fig = px.histogram(
        concatenated_data, 
        x='output', 
        title='Heart Disease Distribution', 
        labels={'output': 'Heart Disease (1 = Yes, 0 = No)'}, 
        color_discrete_sequence=['orange'],
        category_orders={'output': [0, 1]}  # Set X-axis to show only 0 and 1
    )
    heart_disease_distribution_fig.update_xaxes(tickvals=[0, 1], dtick=1)  # Set X-axis ticks to 0 and 1

    chest_pain_analysis_fig = px.histogram(
        concatenated_data, 
        x='cp', 
        color='output', 
        title='Chest Pain Analysis', 
        labels={'cp': 'Chest Pain Type'}, 
        color_discrete_sequence=px.colors.qualitative.Set2,
        category_orders={'cp': [0, 1, 2, 3]}  # Set X-axis to show 0, 1, 2, and 3
    )
    chest_pain_analysis_fig.update_xaxes(tickvals=[0, 1, 2, 3], dtick=1)  # Set X-axis ticks to 0, 1, 2, and 3

    # Update the last update time
    last_update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    return age_distribution_fig, heart_disease_distribution_fig, chest_pain_analysis_fig, last_update_time

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')