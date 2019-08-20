# Import required libraries
import pickle
import copy
import pathlib
import dash
import dash_table
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import io
import xlsxwriter
import flask
from flask import send_file
import urllib


# get relative data folder
PATH = pathlib.Path(__file__).parent

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.css.config.serve_locally = False

server = app.server

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}


# Create global chart template
mapbox_access_token = "pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w"

# Load data
df = pd.ExcelFile(PATH.joinpath("(4.21)Database for China Agricultural_modified.xlsx"))
sheet_to_df_map = {}
available_indicators = []

for sheet_name in df.sheet_names:
    sheet_to_df_map[sheet_name] = df.parse(sheet_name)
    available_indicators.append(df.parse(sheet_name).columns[0])

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


df3_1_1a = sheet_to_df_map['3.1.1a']
df3_1_1a = df3_1_1a.reset_index(drop = True)

df3_1_1a_name = df3_1_1a.columns[0]
df3_1_1a.columns = df3_1_1a.iloc[0].values.tolist()
df3_1_1a = df3_1_1a.reindex(df3_1_1a.index.drop(0)).reset_index(drop = True)
trim3_1_1a = df3_1_1a.drop([df3_1_1a.index[-1]])
trim3_1_1a.set_index('Classification', inplace=True)   
years = trim3_1_1a.columns.values
df3_1_1a = sheet_to_df_map['3.1.1a']


info = {}
years_options_list = []
for i in years:
    info['label'] = str(i)
    info['value'] = str(i)
    years_options_list.append(info)
    info = {}

info = {}
table_options_list = []
for i in range(len(available_indicators)):
    info['label'] = str(available_indicators[i])
    info['value'] = str(df.sheet_names[i])
    table_options_list.append(info)
    info = {}

######################################### MAIN APP #########################################
def serve_layout():
    return html.Div([
        # Banner display
        html.Div([html.H2(
                'UN-CSAM Database',
                id='title'
            ),
        ], style={"textAlign": "center"},
            className="banner"
        ),

        # Body
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H6(children='Dataset'),
                                        dcc.Dropdown(
                                            id='table-selector',
                                            options=table_options_list,
                                            value='3.1.1a'
                                            ),

                                        html.Div(id='output-container'),

                                        html.Div(id='controls-year-selector', children=[
                                        dcc.Dropdown(
                                            id='year-selector',
                                            options=years_options_list,
                                            value='2008-09',
                                            style={'display': 'none'}
                                        ),
                                        ]),
                                        ]),
                                        html.Br(),
                                        html.Br(),
                                        html.H6(children='Graph Selector'),
                                        html.Div(id='graph-selector', children=[
                                            dcc.Dropdown(
                                                id='graph',
                                                options=[{'label': i, 'value': i} for i in ['pie chart']],
                                                value='pie chart',
                                            ),
                                        ]),
                                        html.Br(),
                                        html.Br(),
                                    ]),
                            ],
                            className="four columns",
                            style={'margin-top': '10'}
                        ),
                        html.Br(),
                ], className="row"
                    ),

                html.Div(
                    [
                        html.Div(
                            [
                            dash_table.DataTable(
                                id='table',
                                css=[
                                        {
                                'selector': '.dash-cell div.dash-cell-value',
                                'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                                        }
                                    ],
                                style_cell={
                        
                                'textAlign': 'left'
                                            },
                                style_header={
                                    'backgroundColor': 'white',
                                    'fontWeight': 'bold'
                                },
                                sort_action='native',                        
                                ),
                        
                        #Export data
                        html.Div([
                            html.A(html.Button('Export Data', id='download-button'), id='download-link',download="rawdata.csv", href="",target="_blank")
                            ]),

                        html.Div(
                            [
                                dcc.Graph(id='pie_chart')
                            ],
                            className='six columns',
                            style={'margin-top': '10'}
                        ),
                    ], className="row"
                )
            ],
            className="container"
        )
        ])

app.layout = serve_layout()


######################################### UPDATING FIGURES #########################################
@app.callback(
    Output('year-selector', 'style'),
    [Input('table-selector', 'value')])
def update_3_1_1a_option(table_name):
    if table_name == "3.1.1a":
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# callback for datatable
@app.callback([Output('table', 'data'), Output('table', 'columns')],[Input('table-selector', 'value')])

def updateTable(selected_table):
    selected_df = pd.read_excel(PATH.joinpath("(4.21)Database for China Agricultural_modified.xlsx"),sheet_name = selected_table ,header = 1)
    selected_df = selected_df.drop(selected_df.index[-1])
    return (selected_df.to_dict('records'),[{"name": i, "id": i} for i in selected_df.columns])

# Callback for csv download
@app.callback(
    Output('download-link', 'href'),
    [Input('table-selector', 'value')])

def update_downloader(selected_table):
    selected_df = pd.read_excel(PATH.joinpath("(4.21)Database for China Agricultural_modified.xlsx"),sheet_name = selected_table,header = 1)
    csvString = selected_df.to_csv(index=False,encoding='utf-8-sig')    
    csvString = "data:text/csv;charset=utf-8-sig,%EF%BB%BF" + urllib.parse.quote(csvString)
    return csvString

# callback for pie chart
@app.callback(Output('pie_chart', 'figure'),[Input('year-selector', 'value')])

def update_figure(selected_year):  
    return {
        'data': [go.Pie(
        labels=trim3_1_1a.index.values.tolist()[1:],
        values=trim3_1_1a[selected_year].values.tolist()[1:],
                            marker={'colors': ['#EF963B', '#C93277', '#349600', '#EF533B', '#57D4F1','#96D38C']})],
        'layout': go.Layout(title=f"Yearly result on "+str(selected_year),
                            autosize = True)}

######################################### CSS #########################################

external_css = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css"
    "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",  # Normalize the CSS
    "https://fonts.googleapis.com/css?family=Open+Sans|Roboto"  # Fonts
    "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
    "https://cdn.rawgit.com/TahiriNadia/styles/faf8c1c3/stylesheet.css",
    "https://cdn.rawgit.com/TahiriNadia/styles/b1026938/custum-styles_phyloapp.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})


if __name__ == '__main__':
    app.run_server(debug=True)