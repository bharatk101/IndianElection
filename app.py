#import packages
import dash
import numpy as np
import pandas as pd
import plotly as py
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from bubbly.bubbly import bubbleplot
from textwrap import dedent

# read dataset
df = pd.read_csv('nl_elections.csv')
#filter
total = df.groupby(['year']).sum()['totvotpoll'].reset_index(name ='Total')
#stylesheet
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = ['https://bootswatch.com/4/flatly/bootstrap.css']
#app init
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# layout
app.layout = html.Div(children = [
    #header
    html.H1(children = 'National Legislature Election Analysis',
    style = { 'textAlign' : 'center', 'padding': 10}),

    #introduction
    dcc.Markdown(dedent('''
    * Elections in the Republic of India include elections for the Parliament,\
    Rajya Sabha, Lok Sabha, the Legislative Assemblies, and numerous
    other Councils and local bodies.
    * This dataset contains details of Lok Sabha elections from 1977 - 2014.
    * Select State and the Parlimentary constituency under it to find out who got the
    most votes across year and the distribution of candidate gender.

    * This Dataset was downloaded from [Harvard Datavarse](https://dataverse.harvard.edu)
    ''')),


    #vots graph
    dcc.Graph(id='vote-counts',
            figure={
                'data': [
                    {'x': total.year, 'y': total.Total, 'type': 'Scatter', 'mode': 'lines+markers'}
                ],
                'layout': go.Layout(
                title = 'Total Vote counts across Year',
                xaxis = {'title' : 'Year'},
                yaxis = {'title' : 'Count'}
                )
            }),

    #dropdown for state wise Analysis graph
    html.Div(children = 'Select State',
    style = {'padding': 10}),
    dcc.Dropdown( id = 'state',
    options = [{'label' :i, 'value': i} for i in df.st_name.unique()],
    style = {  'paddingLeft': 20, 'width' : '50%'},
    placeholder=["Select State"]
    ),
    #graph
    dcc.Graph(id = 'bubble-plot'),

    # state wise gender_graph
    dcc.Graph(id = 'gender-plot'),

    #dropdown for district
    html.Div(children = 'Select Parlimentary constituency'),
    dcc.Dropdown(id ='dist-dropdown'),

    #plot
    dcc.Graph(id = 'constituency-plot'),

    #constituency gender
    dcc.Graph(id = 'con-gen')
], style={'marginBottom': 50, 'marginTop': 25})

# graph for state wise Analysis
@app.callback(
    Output ('bubble-plot', 'figure'),
    [Input( component_id = 'state', component_property = 'value')]
    )
def update_graph(value):
    state = df[df['st_name'] == value]
    total = state.groupby(['partyabbre', 'year']).sum()['totvotpoll'].reset_index(name ='Total')
    figure = bubbleplot(dataset=total,
        x_column='year', y_column='Total', bubble_column='partyabbre',
        size_column='Total', color_column='partyabbre',
        x_title="Years", y_title="Total Number of Votes",
        title='Peoples votes for each party',
        x_range=['1977', '2014'],
        marker_opacity = 0.6)
    return figure


# gender distribution graph
@app.callback(
    Output ('gender-plot', 'figure'),
    [Input( component_id = 'state', component_property = 'value')]
    )
def gender_graph(value):
    state = df[df['st_name'] == value]
    state_f = state[state['cand_sex'] == 'F']
    state_m = state[state['cand_sex'] == 'M']
    gender = state_m.groupby(['year']).count()['cand_sex'].reset_index(name ='Total')
    gender_f = state_f.groupby(['year']).count()['cand_sex'].reset_index(name ='Total')
    trace1 = go.Scatter(x = gender.year,
                       y =gender.Total,
                       mode = 'lines+markers',
                       name = 'Male')
    trace2 = go.Scatter(x = gender_f.year,
                       y =gender_f.Total,
                       mode = 'markers+lines',
                       name = 'Female')
    data =[trace1,trace2]
    layout = go.Layout( title = 'Candidate Gender Distribution',
                        xaxis = dict(title = 'Year', range = [1977,2014]),
                        yaxis = dict(title = 'Count'))
    fig = go.Figure(data=data, layout = layout)
    return fig

#constituency Dropdown
@app.callback(
    Output('dist-dropdown', 'options'),
    [Input('state', 'value')]
)

def update_dist_dropdown(name):
    state = df[df['st_name'] == name]
    return [{'label': i, 'value': i} for i in state.pc_name.unique()]

#constituency plot

@app.callback(
    Output ('constituency-plot', 'figure'),
    [Input( component_id = 'dist-dropdown', component_property = 'value')]
    )
def update_graph(value):
    con = df[df['pc_name'] == value]
    total = con.groupby(['partyabbre', 'year']).sum()['totvotpoll'].reset_index(name ='Total')
    figure = bubbleplot(dataset=total,
        x_column='year', y_column='Total', bubble_column='partyabbre',
        size_column='Total', color_column='partyabbre',
        x_title="Years", y_title="Total Number of Votes",
        title='Peoples votes for each party',
        x_range=['1977', '2014'],
        marker_opacity = 0.6)
    return figure

# gender distribution graph
@app.callback(
    Output ('con-gen', 'figure'),
    [Input( component_id = 'dist-dropdown', component_property = 'value')]
    )
def gender_graph(value):
    con = df[df['pc_name'] == value]
    con_f = con[con['cand_sex'] == 'F']
    con_m = con[con['cand_sex'] == 'M']
    gender = con_m.groupby(['year']).count()['cand_sex'].reset_index(name ='Total')
    gender_f = con_f.groupby(['year']).count()['cand_sex'].reset_index(name ='Total')
    trace1 = go.Scatter(x = gender.year,
                       y =gender.Total,
                       mode = 'lines+markers',
                       name = 'Male')
    trace2 = go.Scatter(x = gender_f.year,
                       y =gender_f.Total,
                       mode = 'markers+lines',
                       name = 'Female')
    data =[trace1,trace2]
    layout = go.Layout( title = 'Candidate Gender Distribution',
                        xaxis = dict(title = 'Year', range = [1977,2014]),
                        yaxis = dict(title = 'Count'))
    fig = go.Figure(data=data, layout = layout)
    return fig

# rum server
if __name__ == '__main__':
    app.run_server(debug = True)
