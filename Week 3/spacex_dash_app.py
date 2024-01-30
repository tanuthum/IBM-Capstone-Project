# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the spacex data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                dcc.Dropdown(id="site-dropdown",
                                             options=[{'label': 'All Sites', 'value': 'ALL'},
                                                      {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                      {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                      {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                      {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},],
                                             value='ALL',
                                             placeholder="Select a Launch Site here",
                                             searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                html.Div(dcc.Graph(id='success-pie-chart')),

                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=min_payload,
                                                max=max_payload,
                                                step=100,
                                                marks={i: str(i) for i in range(int(min_payload), int(max_payload)+1, 500)},
                                                value=[min_payload, max_payload]),
                                html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Calculate success/failure counts for all launch sites
        all_sites_counts = spacex_df.groupby('Launch Site')['class'].value_counts().unstack().fillna(0)
        
        # Calculate success percentage for each launch site
        all_sites_counts['Success Percentage'] = (all_sites_counts[1] / (all_sites_counts[0] + all_sites_counts[1])) * 100
        all_sites_counts = all_sites_counts.reset_index()

        # Generate pie chart with success percentage
        fig = px.pie(all_sites_counts, names='Launch Site', values='Success Percentage',
                     title='Success Percentage for Each Launch Site',
                     labels={'Launch Site': 'Launch Site', 'Success Percentage': 'Success Percentage'})

    else:
        # Calculate success/failure counts for the selected launch site
        site_counts = spacex_df[spacex_df['Launch Site'] == entered_site]['class'].value_counts()

        # Generate pie chart with calculated counts
        success_percentage = (site_counts[1] / (site_counts[0] + site_counts[1])) * 100
        fig = px.pie(names=['Failure', 'Success'], values=[100 - success_percentage, success_percentage],
                     title=f'Launch Success/Failure Distribution for {entered_site}',
                     labels={'0': 'Failure', '1': 'Success'})

    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])
def update_scatter_chart(selected_site, selected_payload):
    filtered_df = spacex_df
    if selected_site != 'ALL':
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]

    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= selected_payload[0]) &
                              (filtered_df['Payload Mass (kg)'] <= selected_payload[1])]

    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                     title='Payload vs. Launch Success',
                     labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'},
                     category_orders={'class': ['Failure', 'Success']},
                     color_discrete_map={'Failure': 'red', 'Success': 'green'})

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(port=8052)
   
