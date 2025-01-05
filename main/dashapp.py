import numpy as np
import pandas as pd
import scipy.stats as stats
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
from plotly.offline import init_notebook_mode
init_notebook_mode(connected=True)
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

    container = f"Exported to {country_mapping[country]} in {year}"

    dff = df.copy()

    # Get the 'Import trade _metric Tons' column
    data = dff['Import trade _metric Tons']

    # Fit the data to a normal distribution
    mean_value = np.mean(data)
    std_dev = np.std(data)

    # Normalize the data to have a mean of 0 and standard deviation of 1
    normalized_data = (data - mean_value) / std_dev

    # Now, use the normal distribution to scale the values back
    # Use the CDF (Cumulative Distribution Function) to map the data points to a normal distribution
    normal_distribution_values = stats.norm.cdf(normalized_data)

    # If you want to scale these values back into a desired range, for example between 0 and 100
    scaled_values = normal_distribution_values * 100

    # Assign the transformed values back to the dataframe
    dff['normal_trade'] = scaled_values
    dff = dff[(dff['country1']==country)&(dff["Year"] == year)]
    world = gpd.read_file("ne_110m_admin_0_countries.shp")
    world = world.to_crs(epsg=4326 )
    # Plotly Express
    fig = go.Figure()  # Ensure the correct coordinate reference system

    # fig.add_trace(go.Scattergeo(
    #     lon=[dff["longitude1"].iloc[0]],
    #     lat=[dff["latitude1"].iloc[0]],
    #     mode="markers",
    #     marker=dict(size=10, color="red"),
    #     name="Exporting Country"
    # ))
    # Add each export flow as a line
    hover_texts = []
    for i in range(len(dff)):
        hover_text = (
            f"Export from {country_mapping[dff['country1'].iloc[i]]} to {country_mapping[dff['country2'].iloc[i]]}<br>"
            f"Year: {dff['Year'].iloc[i]}<br>"
            f"Metric Tons: {dff['Import trade _metric Tons'].iloc[i]}<br>"
        )
        trade_value = dff["Import trade _metric Tons"].iloc[i]
        # fig.add_trace(go.Scattergeo(
        
        #     locationmode="ISO-3",
        #     lon=[dff["longitude1"].iloc[i], dff["longitude2"].iloc[i]],  # Start and end longitude
        #     lat=[dff["latitude1"].iloc[i], dff["latitude2"].iloc[i]],  # Start and end latitude
        #     mode="lines",
        #     line=dict(
        #         width=4,
        #         color="blue" if dff["Import trade _metric Tons"].iloc[i] > 200 else "green"  # Example condition for line color
        #     ),
        #     #name=f"Export to {dff['country2'].iloc[i]}"
        # ))
    # Add exporting country as a scatter point (you can dynamically add this for multiple exporting countries)
        fig.add_trace(go.Scattergeo(
            lon=[dff["longitude1"].iloc[i], dff["longitude2"].iloc[i]],
            lat=[dff["latitude1"].iloc[i], dff["latitude2"].iloc[i]],
            mode="lines+markers",
            line=dict(width=2, color="blue"),
            opacity=0.6
            #text=f"Export to {dff['country2'].iloc[i]}, Tons: {dff['Import trade _metric Tons'].iloc[i]}",
            #name=f"Export to {dff['country2'].iloc[i]}"
        ))


        # Add markers for country2 with dynamic color based on trade value
        # fig.add_trace(go.Scattergeo(
        #     lon=[dff["longitude2"].iloc[i]],  # Only plot the marker for country2
        #     lat=[dff["latitude2"].iloc[i]],
        #     mode="markers",
        #     marker=dict(
        #         size=8,
        #         color=trade_value,  # Use the trade value as the color input
        #         colorscale="Viridis",  # You can choose other color scales, e.g., "Rainbow", "Jet", etc.
        #         colorbar=dict(title="Trade Volume (Metric Tons)")  # Optional: add color bar for the scale
        #     ),
        #     hoverinfo='text',
        #     hovertext=hover_text,
        #     name=f"Export to {dff['country2'].iloc[i]}"
        # ))

    fig.add_trace(go.Choropleth(
        z=dff['normal_trade'],  # The trade volume values
        locations=dff['country2'],  # Use ISO-3 country codes for locations
        locationmode='ISO-3',# Location mode for country codes
        #hoverinfo='text',
        #mode='text', 
        colorscale='RdYlGn',# Choose your colorscale
        customdata=dff['Import trade _metric Tons'],
        hovertemplate= 
            "Import from %{text}<br>" +
            "Metric Ton: %{customdata}<br>"+ f"Year: {year}",
        text= [country_mapping[dff['country2'].iloc[i]] for i in range(len(dff['country2']))],
        # colorbar=dict(
        #     title="Normalized Trade Volume (Metric Tons)",
        #     tickvals=[0, 50, 100],  # Optional: Customize tick values
        #     ticktext=[dff["Import trade _metric Tons"].min(), dff["Import trade _metric Tons"].median(), dff["Import trade _metric Tons"].max()]  # Optional: Customize tick labels
        # ), # Add a color bar
        ))

    # Add country labels (country names)
    for i, country in world.iterrows():
        fig.add_trace(go.Scattergeo(
            lon=[country.geometry.centroid.x],
            lat=[country.geometry.centroid.y],
            text=country['NAME'],  # Country name
            mode="text",
            textfont=dict(size=10, color="black", family='Arial Black'),
            showlegend=False,
            hoverinfo="skip"
        ))
    export = dff.groupby(['country1', 'country2'])['Import trade _metric Tons'].sum().reset_index()
    export= export.sort_values(by='Import trade _metric Tons', ascending=False)
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=export['country1'] + ' to ' +export['country2'],  # Combined country pair names
        y=export['Import trade _metric Tons'],
        name="Total Import Metric Tons",
        marker=dict(color='orange'),
        text=export['Import trade _metric Tons'],
        textposition='auto',
    ))
    fig.update_geos(
        scope="africa",  # Focus on Africa
        resolution=50  # Higher resolution for smaller countries
    )
    # Configure the layout
    fig.update_layout(
        #title_text=f"Flow Map: Exports from {country_mapping[str(country)]}",
        showlegend=False,
        geo=dict(
            scope="africa",  # Limit map to Africa
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth",
        ),

        height=1000,  # Increase map height
        width=1200

    )
    fig2.update_layout(
        barmode='group',  # Group the bars together if there are multiple bars
        title_text="Total Import Metric Tons",  # Title for the bar plot
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
    #port = int(os.environ.get('PORT', 8051)) 
    app.run_server(port=8051, debug=True)