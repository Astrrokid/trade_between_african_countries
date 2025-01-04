import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
import geopandas as gpd
import os

app = Dash(__name__)

# -- Import and clean data (importing csv into pandas)
# df = pd.read_csv("intro_bees.csv")
df = pd.read_csv("main/data_with_coordinates.csv")
country_mapping = {
    'EGY': 'Egypt', 'COD': 'Congo (DRC)', 'TZA': 'Tanzania', 'ZAF': 'South Africa', 'KEN': 'Kenya',
    'UGA': 'Uganda', 'SDN': 'Sudan', 'DZA': 'Algeria', 'MAR': 'Morocco', 'AGO': 'Angola',
    'GHA': 'Ghana', 'CIV': 'Ivory Coast', 'CMR': 'Cameroon', 'NER': 'Niger', 'MLI': 'Mali',
    'BFA': 'Burkina Faso', 'TCD': 'Chad', 'SEN': 'Senegal', 'ZWE': 'Zimbabwe', 'GIN': 'Guinea',
    'RWA': 'Rwanda', 'BEN': 'Benin', 'BDI': 'Burundi', 'TUN': 'Tunisia', 'TGO': 'Togo',
    'SLE': 'Sierra Leone', 'CAF': 'Central African Republic', 'LBR': 'Liberia', 'MRT': 'Mauritania',
    'ERI': 'Eritrea', 'GMB': 'Gambia', 'BWA': 'Botswana', 'NAM': 'Namibia', 'GAB': 'Gabon',
    'GNB': 'Guinea-Bissau', 'GNQ': 'Equatorial Guinea', 'MUS': 'Mauritius', 'SWZ': 'Eswatini',
    'SYC': 'Seychelles', 'ETH': 'Ethiopia', 'NGA': 'Nigeria', 'SOM': 'Somalia', 'LBY': 'Libya',
    'MOZ': 'Mozambique', 'MDG': 'Madagascar', 'ZMB': 'Zambia', 'COG': 'Congo', 'MWI': 'Malawi',
    'SSD': 'South Sudan', 'COM': 'Comoros', 'CPV': 'Cape Verde', 'LSO': 'Lesotho', 'STP': 'Sao Tome and Principe',
    'DJI': 'Djibouti'
}
years = [2009, 2020, 2021, 2010, 2011, 2022, 2003, 2006, 2007, 2008, 2012,
         2013, 2014, 2015, 2016, 2017, 2018, 2019, 2004, 2005]

year_dict_list = [{"label": year, "value": year} for year in sorted(years)]
country_dict_list = [{"label": country_mapping[country], "value": country} for country in country_mapping]
#df = df.groupby(['State', 'ANSI', 'Affected by', 'Year', 'state_code'])[['Pct of Colonies Impacted']].mean()
#df.reset_index(inplace=True)
#print(df[:5])

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("Web Application Dashboards with Dash", style={'text-align': 'center'}),

    dcc.Dropdown(id="slct_year",
                 options=year_dict_list,
                 multi=False,
                 value=2009,
                 style={'width': "40%"}
                 ),

    dcc.Dropdown(id="slct_country",
                 options=country_dict_list,
                 multi=False,
                 value='NGA',
                 style={'width': "40%"}
                 ),
    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_bee_map', figure={}),
    dcc.Graph(id='barplot')

])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_bee_map', component_property='figure'),
     Output(component_id='barplot', component_property='figure')],
    [Input(component_id='slct_year', component_property='value'),
    Input(component_id='slct_country', component_property='value')]
)
def update_graph(year, country):
    print(year, country)

    container = "The year chosen by user was: {}".format(year)

    dff = df.copy()
    dff = dff[(dff['country1']==country)&(dff["Year"] == year)]
    world = gpd.read_file("ne_110m_admin_0_countries.shp")
    world = world.to_crs(epsg=4326 )
    # Plotly Express
    fig = go.Figure()

    # Add each export flow as a line
    for i in range(len(dff)):
        hover_text = (
            f"Export from {country_mapping[dff['country1'].iloc[i]]} to {country_mapping[dff['country2'].iloc[i]]}<br>"
            f"Year: {dff['Year'].iloc[i]}<br>"
            f"Metric Tons: {dff['Import trade _metric Tons'].iloc[i]}<br>"
        )
        fig.add_trace(go.Scattergeo(
        
            locationmode="ISO-3",
            lon=[dff["longitude1"].iloc[i], dff["longitude2"].iloc[i]],  # Start and end longitude
            lat=[dff["latitude1"].iloc[i], dff["latitude2"].iloc[i]],  # Start and end latitude
            mode="lines",
            line=dict(
                width=4,
                color="blue" if dff["Import trade _metric Tons"].iloc[i] > 200 else "green"  # Example condition for line color
            ),
            hoverinfo='text',
            hovertext=hover_text,
            name=f"Export to {dff['country2'].iloc[i]}"
        ))

    # # Add exporting country as a scatter point (you can dynamically add this for multiple exporting countries)
        fig.add_trace(go.Scattergeo(
            lon=[dff["longitude1"].iloc[i], dff["longitude2"].iloc[i]],
            lat=[dff["latitude1"].iloc[i], dff["latitude2"].iloc[i]],
            mode="markers",
            line=dict(width=2, color="blue"),
            hoverinfo='text',
            hovertext=hover_text,
            text=f"Export to {dff['country2'].iloc[i]}, Tons: {dff['Import trade _metric Tons'].iloc[i]}",
            name=f"Export to {dff['country2'].iloc[i]}"
        ))
    fig.add_trace(go.Scattergeo(
        lon=[dff["longitude1"].iloc[0]],
        lat=[dff["latitude1"].iloc[0]],
        mode="markers",
        marker=dict(size=10, color="red"),
        name="Exporting Country"
    ))

    # Add country labels (country names)
    # for i, country in world.iterrows():
    #     fig.add_trace(go.Scattergeo(
    #         lon=[country.geometry.centroid.x],
    #         lat=[country.geometry.centroid.y],
    #         text=country['NAME'],  # Country name
    #         mode="text",
    #         textfont=dict(size=8, color="black"),
    #         showlegend=False
    #     ))
    export = dff[(dff['country1']==country)&(dff['Year']==year)].groupby(['country1', 'country2'])['Import trade _metric Tons'].sum().reset_index()
    export= export.sort_values(by='Import trade _metric Tons', ascending=False)
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=export['country1'] + ' to ' + export['country2'],  # Combined country pair names
        y=export['Import trade _metric Tons'],
        name="Total Export Metric Tons",
        marker=dict(color='orange'),
        text=export['Import trade _metric Tons'],
        textposition='auto',
    ))

    # Configure the layout
    fig.update_layout(
        title_text=f"Flow Map: Exports from {country}",
        showlegend=True,
        geo=dict(
            scope="africa",  # Limit map to Africa
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth",
        ),

        height=800,  # Increase map height
        width=1200

    )
    fig2.update_layout(
        barmode='group',  # Group the bars together if there are multiple bars
        title_text="Total Export Metric Tons",  # Title for the bar plot
        xaxis=dict(
            title="Country Pairs",  # Label for the x-axis
            tickangle=45,  # Angle the x-axis labels if they overlap
        ),
        yaxis=dict(
            title="Metric Tons",  # Label for the y-axis
            rangemode='tozero',  # Ensure the y-axis starts at zero
            showgrid=True,  # Show gridlines for better readability
        ),
        margin=dict(t=50, b=100, l=50, r=50),  # Adjust margins for more space
        height=400,  # Height of the bar plot (adjust as needed)
        width=1200,  # Width of the bar plot
    )



    return container, fig, fig2


# ------------------------------------------------------------------------------
if __name__ == '__main__':    
    port = int(os.environ.get('PORT', 5000)) 
    app.run_server(host='0.0.0.0', port=port)