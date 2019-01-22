import dash
import numpy as np
import pandas as pd
import plotly as py
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from bubbly.bubbly import bubbleplot

df = pd.read_csv('nl_elections.csv')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children = [

html.H1(children = 'Lok Sabha Election Analysis',
style = { 'textAlign' : 'center'}),

html.Div(children = 'Select State'),

dcc.Dropdown( id = 'state',
options = [{'label' :i, 'value': i} for i in df.st_name.unique()],
),

dcc.Graph(id = 'bubble-plot'),

html.Div(children = 'Gender Distribution'),
dcc.Graph(id = 'gender-plot')




])

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
                       name = 'M')
    trace2 = go.Scatter(x = gender_f.year,
                       y =gender_f.Total,
                       mode = 'markers+lines',
                       name = 'F')
    data =[trace1,trace2]
    layout = go.Layout( title = 'Candidate Gender Distribution',
                        xaxis = dict(title = 'Year', range = [1977,2014]),
                        yaxis = dict(title = 'Count'))
    fig = go.Figure(data=data, layout = layout)
    return fig

if __name__ == '__main__':
    app.run_server(debug = True)
