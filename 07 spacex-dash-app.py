# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Get all launch sites for the dropdown options
launch_sites = spacex_df['Launch Site'].unique().tolist()
# Add 'All Sites' option to the beginning of the list
launch_sites.insert(0, 'All Sites')

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    html.Div([
        dcc.Dropdown(
            id='site-dropdown',
            options=[{'label': site, 'value': site} for site in launch_sites],
            value='All Sites', # Default value
            placeholder="Select a Launch Site here",
            searchable=True
        ),
    ]),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0, # Set minimum to 0 for a cleaner range, or round min_payload
        max=10000, # Set maximum to 10000 or round max_payload up
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 1000)}, # Marks at every 1000 kg
        value=[min_payload, max_payload] # Initial range set to min and max payload
    ),
    html.Br(),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'All Sites':
        # If 'All Sites' is selected, calculate total successful launches count for all sites
        # Filter for successful launches (class = 1)
        filtered_df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
            filtered_df,
            values='class', # Use 'class' directly for counts of successful launches
            names='Launch Site', # Group by Launch Site
            title='Total Successful Launches By Site'
        )
        return fig
    else:
        # If a specific launch site is selected, show the Success vs. Failed counts for the site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count success (class=1) and failed (class=0) outcomes
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        # Map 1 to Success and 0 to Failed for better labeling
        success_counts['outcome'] = success_counts['class'].apply(lambda x: 'Success' if x == 1 else 'Failed')

        fig = px.pie(
            success_counts,
            values='count',
            names='outcome',
            title=f'Total Successful vs. Failed Launches for {entered_site}'
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    # Filter the dataframe by payload range first
    filtered_payload_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if entered_site == 'All Sites':
        # If 'All Sites' is selected, show all successful launches
        fig = px.scatter(
            filtered_payload_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for All Sites'
        )
        return fig
    else:
        # If a specific site is selected, filter by site and then plot
        filtered_site_payload_df = filtered_payload_df[
            filtered_payload_df['Launch Site'] == entered_site
        ]
        fig = px.scatter(
            filtered_site_payload_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for {entered_site}'
        )
        return fig




# Run the app
if __name__ == '__main__':
    app.run()
