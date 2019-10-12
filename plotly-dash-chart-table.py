import plotly.graph_objects as go
from plotly.colors import n_colors
from plotly.offline import download_plotlyjs, init_notebook_mode, plot,iplot
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_auth


USERNAME_PASSWORD_PAIRS = [['username', 'password'], ['Joe', 'Doe']]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
auth = dash_auth.BasicAuth(app, USERNAME_PASSWORD_PAIRS)

##############################
df1 = pd.read_excel('I_NTA_Analysis.xlsx', encoding = 'utf-8')

countries = df1['Country']
years = df1['Year']

relevant_data = df1.drop(axis = 1, columns = ['Country', 'Year'])

age_category = [int(age.replace("Age", "")) for age in relevant_data.columns]
labels = [countries[i] + ', ' + str(years[i]) for i in range(len(countries))]
sum_list = [sum(relevant_data.iloc[i]) for i in range(relevant_data.shape[0])]
relevant_ratio = [(10000 * relevant_data.iloc[i])/(sum_list[i]) for i in range(relevant_data.shape[0])]
age_60_80 = [sum(relevant_data.iloc[i, 60:80]) for i in range(relevant_data.shape[0])]
age_60_80_ratio = [age_60_80[i]/ sum_list[i] for i in range(relevant_data.shape[0])]
#############################
df2 = pd.DataFrame({'Country': countries, 'Year': years, 'Pop between 60 and 80': age_60_80_ratio})


def country_data(df, i):
    data = df[i]
    country = []
    counter = 0
    for k in age_category:
        country.extend([k] * int(round(data[counter])))
        counter+=1
    return country

data1_plot = [country_data(relevant_ratio, i) for i in range(len(countries))]

app.layout = html.Div([

    html.Div([
    dcc.Dropdown(
        id = 'Country',
        options = [{'label': i, 'value': i} for i in labels],
        multi = True,
        value = ['Hungary, 2005'])]
    ), dcc.Graph(id='indicator-graphic'),    
    dcc.Graph(id='my-graph')
])

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('Country', 'value')]
)


def update_graph(Country):
    trace_list = []
    for entry in Country:
        title = (entry.replace(',', '')).split()
        place, year = title[0], title[1]
        dataframe1 = df1[df1['Country']==place]
        dataframe1 = dataframe1[dataframe1['Year']==int(year)]
        dataframe1.drop(axis = 1, columns = ['Country', 'Year'], inplace = True)
        df = dataframe1.iloc[0]
        trace_list.append(go.Scatter(
                x = age_category, y = df, name = entry
            ))                      
    layout = go.Layout(title = {'text': 'Distribution of Population by Country and Year'},
                            xaxis = {'title': 'Age'},
                            yaxis = {'title': 'Population Size'})
    return {
       'data': trace_list,
        'layout': layout

    }


@app.callback(
    Output('my-graph', 'figure'),
    [Input('Country', 'value')]
)

def update_table(Country):
    country_list = []
    year_list = []
    percentage_60_80 = []
    for entry in Country:
        title = (entry.replace(',', '')).split()
        place, year = title[0], title[1]
        dataframe2 = df2[df2['Country']==place]
        dataframe2 = dataframe2[dataframe2['Year'] ==int(year)]
        country_list.append(dataframe2.iloc[0, 0])
        year_list.append(dataframe2.iloc[0, 1])
        percentage_60_80.append(dataframe2.iloc[0, 2])
    trace2 = go.Table(columnwidth= [80, 120, 120], header=dict(values=['Country', 'Year', 'Population % <br>between 60 and 80'], font = dict(color=['rgb(45,45,45)']*5, size=18),
                                    fill = dict( color = 'rgb(224, 187, 228)')),
                        cells=dict(values= [country_list, year_list, percentage_60_80], font = dict(size = 22),
                        height = 30, fill = dict( color = ['rgb(255, 223, 211)', 'rgba(228, 222,249, 0.65)'])))

    return {
        'data': [trace2]
    }


if __name__ == '__main__':
    app.run_server()
