import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np
import threading
import time

# Create an empty DataFrame to store new data
new_data = pd.DataFrame(columns=['age', 'output', 'sex', 'cp'])

def generate_random_data():
    global new_data
    while True:
        # Generate 10 random entries
        new_entries = pd.DataFrame({
            'age': np.random.randint(25, 85, 50),
            'output': np.random.randint(0, 2, 50),
            'sex': np.random.randint(0, 2, 50),
            'cp': np.random.randint(0, 4, 50)
        })
        
        # Append to new_data
        new_data = pd.concat([new_data, new_entries], ignore_index=True)
        
        time.sleep(1)  # Wait for 1 second

# Start the data generation in a separate thread
data_thread = threading.Thread(target=generate_random_data, daemon=True)
data_thread.start()

# Read the CSV file
df = pd.read_csv(r'C:\Master\an_2_sem_1\Big_Data\Project\heart_diseases_big_data-main\data\heart_dataset.csv')

# Create a Dash application
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div(style={'height': '100vh', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'}, children=[
    html.Div(style={'padding': '10px', 'textAlign': 'center'}, children=[
        html.Button('Update Charts', id='update-button', n_clicks=0)
    ]),
    html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'flexGrow': 1}, children=[
        html.Div(style={'padding': '10px'}, children=[
            dcc.Graph(id='age-distribution-fig')
        ]),
        html.Div(style={'padding': '10px'}, children=[
            dcc.Graph(id='heart-disease-distribution-fig')
        ]),
        html.Div(style={'padding': '10px'}, children=[
            dcc.Graph(id='sex-count-fig')
        ]),
        html.Div(style={'padding': '10px'}, children=[
            dcc.Graph(id='chest-pain-analysis-fig')
        ]),
    ]),
])

# Callback to update the figures
@app.callback(
    Output('age-distribution-fig', 'figure'),
    Output('heart-disease-distribution-fig', 'figure'),
    Output('sex-count-fig', 'figure'),
    Output('chest-pain-analysis-fig', 'figure'),
    Input('update-button', 'n_clicks')
)
def update_figures(n_clicks):
    # Combine the original dataset with the new data
    combined_df = pd.concat([df, new_data], ignore_index=True)
    
    # Age Distribution
    age_distribution_fig = px.histogram(combined_df, x='age', nbins=30, title='Age Distribution', 
                                      labels={'age': 'Age'}, color_discrete_sequence=['blue'])
    
    # Heart Disease Distribution
    heart_disease_distribution_fig = px.histogram(
        combined_df, 
        x='output', 
        title='Heart Disease Distribution', 
        labels={'output': 'Heart Disease (1 = Yes, 0 = No)'}, 
        color_discrete_sequence=['orange'],
        category_orders={'output': [0, 1]}
    )
    heart_disease_distribution_fig.update_xaxes(tickvals=[0, 1], dtick=1)

    # Sex Count
    sex_count_fig = px.histogram(
        combined_df, 
        x='sex', 
        title='Sex Count', 
        labels={'sex': 'Sex (0 = Female, 1 = Male)'}, 
        color_discrete_sequence=['green'],
        category_orders={'sex': [0, 1]}
    )
    sex_count_fig.update_xaxes(tickvals=[0, 1], dtick=1)

    # Chest Pain Analysis
    chest_pain_analysis_fig = px.histogram(
        combined_df, 
        x='cp', 
        color='output', 
        title='Chest Pain Analysis by Heart Disease', 
        labels={'cp': 'Chest Pain Type', 'output': 'Heart Disease'}, 
        color_discrete_sequence=px.colors.qualitative.Set2,
        category_orders={'cp': [0, 1, 2, 3]}
    )
    chest_pain_analysis_fig.update_xaxes(tickvals=[0, 1, 2, 3], dtick=1)

    return age_distribution_fig, heart_disease_distribution_fig, sex_count_fig, chest_pain_analysis_fig

if __name__ == '__main__':
    app.run_server(debug=True)

