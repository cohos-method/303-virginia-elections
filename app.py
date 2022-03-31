import dash
from dash import dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import pandas as pd

# Read in the USA counties shape files
from urllib.request import urlopen
import json

########### Define a few variables ######

tabtitle = 'US County Data Exploration'

sourceurl = 'https://www.kaggle.com/muonneutrino/us-census-demographic-data'
githublink = 'https://github.com/cohos-method/303-virginia-elections.git'
dataurl = 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json'

file_county_data = "resources/acs2017_county_data.csv"
file_rural_urban_codes = "resources/ruralurbancodes2013.xls"

colselected = 'TotalPop'
state= "California" #['California','Oregon']

#### Build Continous variables choices.
cont_variables = ['TotalPop', 'Men', 'Women',
    'Hispanic','White', 'Black', 'Native', 'Asian', 'Pacific',
    'Poverty','ChildPoverty',
    'Professional', 'Service', 'Office', 'Construction','Production',
    'Drive', 'Carpool', 'Transit', 'Walk', 'OtherTransp','WorkAtHome',
    'Employed', 'PrivateWork', 'PublicWork','SelfEmployed', 'FamilyWork', 'Unemployment']

cont_variables_desc = ['Population - Total', 'Population - Men', 'Population - Women',
    'Race - Hispanic','Race - White', 'Race - Black', 'Race - Native', 'Race - Asian', 'Race - Pacific',
    'Poverty - Total','Poverty - Child ',
    'Job - Professional', 'Job - Service', 'Job - Office', 'Job - Construction','Job - Production',
    'Communte - Drive', 'Communte - Carpool', 'Communte - Transit', 'Communte - Walk', 'Communte - Other Transportation','Communte - Work At Home',
    'Employment Sector - Employed', 'Employment Sector - Private Work', 'Employment Sector - Public Work','Employment Sector - Self Employed', 'Employment Sector - Family Work', 'Employment Sector - Unemployment']

measure_options = []
state_options = []

for c in range(len(cont_variables_desc)):
    d = {'label':cont_variables_desc[c], 'value':cont_variables[c]}
    measure_options.append(d)

#### load counties geo data.
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

#### buildFig
def buildFig(dfx, colselected, state, imin, imax):

    fig = go.Figure(go.Choroplethmapbox(geojson=counties,
                                    locations=dfx['CountyId'],
                                    z=dfx[colselected],
                                    colorscale='Electric',
                                    text=dfx['County'],
                                    zmin=imin,
                                    zmax=imax,
                                    marker_line_width=0))

    fig.update_layout(mapbox_style="carto-positron"
                      , mapbox_zoom=3.5
                     #, mapbox_center = {"lat": 38.0293, "lon": -79.4428}
                      , mapbox_center = {"lat": 41.101652, "lon": -98.291915}
                      , title_text = "US  County Map for " + colselected
                      , title_font_size = 20
                      , margin = {"r":0,"t":30,"l":0,"b":0}
                      , width  = 1100
                      , height = 500
                     )
    return fig

#### Load all the necessary data and  merge them together to build the master source data includes cleaning and shapping.
def buildSuperData():
    dfc = pd.read_csv(file_county_data)
    #dfc = dfc[ dfc['State'] == state]
    dfru = pd.read_excel(file_rural_urban_codes)
    dfru['rucc_2013_desc'] = dfru['RUCC_2013'].map( {1:'Metro', 2:'Metro', 3:'Metro', 4:'Urban', 5:'Urban', 6:'Suburban', 7:'Suburban', 8:'Rural', 9:'Rural'})
    #dfru.head()

    df = pd.merge(dfc, dfru
             , how='left'
             , left_on = 'CountyId'
             , right_on = 'FIPS'
            )

    #df['FIPS'] = df['FIPS'].astype('str')
    #df['FIPS'] = df['FIPS'].str.pad(width=5, side='left', fillchar='0')
    df['CountyId'] = df['CountyId'].astype('str')
    df['CountyId'] = df['CountyId'].str.pad(width=5, side='left', fillchar='0')
    #df.head()

    #df['rucc_2013_desc'] = pd.Categorical(df['rucc_2013_desc'], ['Metro', 'Urban', 'Suburban', 'Rural'])
    #df['rucc_2013_desc'].value_counts()

    #df.groupby('rucc_2013_desc')[cont_variables].mean().sort_index()
    return df

#### build the data frame that is required for the building the graph
def buildFigDF(df1, state, colselected):
    df1 = df1[ df1['State_x'] == state]
    dfx = pd.DataFrame(df1.groupby(['CountyId','County','rucc_2013_desc'])[colselected].mean())
    imin = dfx[colselected].min()
    imax =  dfx[colselected].max()

    dfx.reset_index(inplace=True)
    return dfx, imin, imax

##### build  the graph using the data
def drawFig(df, state, colselected):
    dfx, imin, imax = buildFigDF(df, state, colselected)
    fig = buildFig(dfx, colselected, state, 0, 1000000)
    return fig
################################
df = buildSuperData()

listOfStates = df['State_x'].unique().tolist()

state_options =[{'label': i, 'value': i} for i in listOfStates]

fig1 = drawFig(df, state, colselected)
#print (fig1)
########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

########### Layout
#print (state_options)
#print (measure_options)

app.layout = html.Div(children=[
    html.H1('US County Data Exploration')
    # Dropdowns
    , html.H6('Select State')
    , dcc.Dropdown(id='state-drop', options=state_options, value='California')
    , html.H6('Select Metrics')
    , dcc.Dropdown(id='measure-drop', options=measure_options, value='TotalPop')
    , dcc.Graph(id='figure1',figure=fig1)
    , html.Br()
    # Footer
    , html.Br()
    , html.A('Code on Github', href=githublink)
    , html.Br()
    , html.A("Data Source", href=sourceurl)
    ]
)

############ Callbacks
@app.callback(Output('figure1', 'figure')
              ,[Input('state-drop', 'value')
              , Input('measure-drop', 'value')])
def display_results(selected_state_value, selected_measure_value):
    fig1 = drawFig(df, selected_state_value, selected_measure_value)
    return fig1


############ Deploy
if __name__ == '__main__':
    app.run_server(debug=True)
