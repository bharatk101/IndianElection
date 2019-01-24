#import packages
import dash
import numpy as np
import pandas as pd
import plotly as py
import dash_table
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from bubbly.bubbly import bubbleplot
from textwrap import dedent

#run_server
server = app.server
# read dataset
df = pd.read_csv('nl_elections.csv')

# column names for tables
#col = pd.DataFrame(columns=['year', 'partyabbre', 'Average_Votes'])

#total votes across years
total = df.groupby(['year']).sum()['totvotpoll'].reset_index(name ='Total')

# candidate participation rate
participation = df.groupby('year').count()['cand_name'].reset_index(name='Total')


#gender_distri
gen_m = df[df['cand_sex'] == 'M']
gen_f = df[df['cand_sex'] == 'F']
total_m = gen_m.groupby(['year']).count()['cand_sex'].reset_index(name ='Total')
total_f = gen_f.groupby(['year']).count()['cand_sex'].reset_index(name ='Total')

#stylesheet
external_stylesheets = ['https://bootswatch.com/4/flatly/bootstrap.css']

#app init
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# layout
app.layout = html.Div(children = [
    #header
    html.H1(children = 'National Legislature Election Analysis',
    style = { 'textAlign' : 'center', 'padding': 20}),

    #introduction
    dcc.Markdown(dedent('''
    * Elections in the Republic of India include elections for the Parliament,\
    Rajya Sabha, Lok Sabha, the Legislative Assemblies, and numerous
    other Councils and local bodies.
    * This dataset contains details of Lok Sabha elections from 1977 - 2014.
    * Select State and the Parlimentary constituency under it to find out who got the
    most votes across year and the distribution of candidate gender.

    * This Dataset was downloaded from [Harvard Dataverse](https://dataverse.harvard.edu)
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

    dcc.Markdown(dedent('''
    *   All political parties were making extensive use of social media during the
        election campaign - relatively new in Indian politics.
    *   While social media still has a long way to reach India's remote corners,
        it certainly appeals to the youth who are a significant vote bank in 2014.
    *   In current 2019 where Internet is widely available in almost everywhere
        corner we can see a huge rise in the vote counts this year.
     ''')),

     # participation ratio
     dcc.Graph(id='participation ratio',
             figure={
                 'data': [
                     {'x': participation.year, 'y': participation.Total, \
                     'type': 'lines+markers'}
                 ],
                 'layout': go.Layout(
                 title = 'Candidate Participation',
                 xaxis = {'title' : 'Year'},
                 yaxis = {'title' : 'Count'}
                 )
             }),

    dcc.Markdown(dedent('''

    * The 9th General Elections had 6K candidates in the fray,
    while in the 10th General Elections around 8K candidates contested for 543 seats.
    * In the Eleventh General Elections, 13K candidates contested for 543 seats,
      which were reduced drastically to 4K candidates in 12th Lok Sabha,
      because of increase of security deposit amount.

     ''')),

     #overall candidate gender
     dcc.Graph(id='overall-gen',
         figure={
             'data': [
                 {'x': total_m.year, 'y': total_m.Total, 'type': 'Scatter', \
                 'mode': 'lines+markers', 'name' : 'Male'},
                 {'x': total_f.year, 'y': total_f.Total, 'type': 'Scatter', \
                 'mode': 'lines+markers', 'name' : 'Female'}
             ],
             'layout': go.Layout(
             title = 'Candidate Gender Distribution',
             xaxis = {'title' : 'Year'},
             yaxis = {'title' : 'Count'}
             )
         }),

    dcc.Markdown(dedent('''

    * There is a slight increase in female candidates over the past few elections.

     ''')),

    #dropdown for state wise Analysis graph
    html.Div(children = 'Select a state to find out peoples choice',
    style = {'padding': 30}),
    dcc.Dropdown( id = 'state',
    options = [{'label' :i, 'value': i} for i in df.st_name.unique()],
    value  = '',
    style = {  'paddingLeft': 30, 'width' : '50%'},
    placeholder=["Select State"]
    ),
    #graph
    dcc.Graph(id = 'bubble-plot',
    ),

    # state wise gender_graph
    dcc.Graph(id = 'gender-plot'),

    #dropdown for district
    html.Div(children = 'Select Parlimentary constituency\
    to find out peoples choice',
    style = {'padding': 30}),
    dcc.Dropdown(id ='dist-dropdown',
    value  = '',
    style = {  'paddingLeft': 30, 'width' : '50%'},
    placeholder=["Select"]),

    #plot
    dcc.Graph(id = 'constituency-plot'),
    #constituency gender
    dcc.Graph(id = 'con-gen')

],
style={'marginBottom': 70, 'marginTop': 10})

# graph for state wise Analysis
@app.callback(
    Output ('bubble-plot', 'figure'),
    [Input( component_id = 'state', component_property = 'value')]
    )
def update_graph(value):
    state = df[df['st_name'] == value]
    total = state.groupby(['partyabbre', 'year']).sum()['totvotpoll'].reset_index(name ='Total')
    ttile = 'Peopel\'s choice in ' + value
    figure = bubbleplot(dataset=total,
        x_column='year', y_column='Total', bubble_column='partyabbre',
        size_column='Total', color_column='partyabbre', scale_bubble=3,
        x_title="Years", y_title="Total Number of Votes",
        title=ttile,
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
    ttitle = 'Peopel\'s choice in ' + value
    figure = bubbleplot(dataset=total,
        x_column='year', y_column='Total', bubble_column='partyabbre',
        size_column='Total', color_column='partyabbre',
        x_title="Years", y_title="Total Number of Votes",
        title=ttitle,
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
