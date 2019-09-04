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
    meta_tags=[{"name": "viewport",
                "content": "width=device-width, initial-scale=1"}],
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
df = pd.ExcelFile(PATH.joinpath("(4.21)Database for China Agricultural.xlsx"))
sheet_to_df_map = {}
available_indicators = []

for sheet_name in df.sheet_names:
    sheet_to_df_map[sheet_name] = df.parse(sheet_name)
    available_indicators.append(df.parse(sheet_name).columns[0])


def trim(df):
    trim_df = df.drop([df.index[-1]])
    trim_df = trim_df.set_index('Unnamed: 0')
    years = trim_df.columns.values

    trim_df_T = trim_df.transpose()

    info = {}
    years_options_list = []
    for i in years:
        try:
            info['label'] = int(i)
        except:
            info['label'] = i
        info['value'] = i
        years_options_list.append(info)
        info = {}
    return years, trim_df, trim_df_T, years_options_list


def trim2(df):
    trim_df = df.drop([df.index[-1]])
    trim_df = trim_df.set_index('Year')

    trim_df_T = trim_df.transpose()
    years = trim_df_T.columns.values

    info = {}
    years_options_list = []
    for i in years:
        try:
            info['label'] = int(i)
        except:
            info['label'] = i
        info['value'] = i
        years_options_list.append(info)
        info = {}
    return years, trim_df, trim_df_T, years_options_list


def trim3(df):
    trim_df = df.drop([df.index[-1]])
    trim_df = trim_df.drop([df.index[0]])
    trim_df = trim_df.set_index('Year')

    trim_df_T = trim_df.transpose()
    years = trim_df_T.columns.values

    info = {}
    years_options_list = []
    for i in years:
        try:
            info['label'] = int(i)
        except:
            info['label'] = i
        info['value'] = i

        years_options_list.append(info)
        info = {}
    return years, trim_df, trim_df_T, years_options_list

#df3_1_1a = pd.read_excel(PATH.joinpath("(4.21)Database for China Agricultural.xlsx"),sheet_name = '3.4.16', header = 2)

#years, trim3_1_1a, trim3_1_1a_T, years_options_list = trim(df3_1_1a)
# print(years)
# print(trim3_1_1a)
# print(trim3_1_1a_T)
# print(years_options_list)
# input()


info = {}
table_options_list = []
for i in range(len(available_indicators)):
    info['label'] = str(available_indicators[i])
    info['value'] = str(df.sheet_names[i])
    table_options_list.append(info)
    info = {}

table_list1 = ['3.1.1a', '3.1.1b', '3.2.2', '3.2.4', '3.3.1', '3.3.2a',
               '3.3.2b', '3.4.2', ' 3.4.9', '3.4.11', ' 3.4.13', ' 3.4.16', '3.4.20']
table_list2 = [' 3.4.22', ' 3.5.1', ' 3.5.2']
######################################### MAIN APP #########################################


def description_card():
    """
    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H1("Welcome to UN-CSAM Analytics Dashboard",
                    style={"textAlign": "center", "height": "100%", "width": "100%",
                           "font-size": "28px", "padding-top": "20px"}),

            html.Div(
                id="intro",
                #children="Explore clinic patient volume by time of day, waiting time, and care score. Click on the heatmap to visualize patient experience at different time points.",
            ),
        ]
    )


def generate_control_card():
    """
    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        style={'margin': '10px'},
        children=[
            html.P("Dataset",
                   style={"textAlign": "center", "height": "100%", "width": "100%",
                          "font-size": "26px", "padding-top": "5px"}),
            html.Div(
                className="seven columns",
                children=[
                    dcc.Dropdown(
                        id='table-selector',
                        options=table_options_list,
                        value='3.1.1a'
                    ),
                ],
            ),
            # html.Br(),
            html.Div(
                className="five columns",
                style={'padding-left': '20px'},
                children=[
                    dcc.Dropdown(
                        id='year-selector',
                        style={'display': 'none'}
                    ),
                    html.Br(),
                    # Export data
                    html.Div(
                        style={"textAlign": "right", "padding-bottom": "20px"},
                        children=[

                            html.A(html.Button('Export Data', id='download-button',
                                               style={
                                                   "background-color": "#0074e4", "color": "white"},
                                               # style= {"border-color": "#17a2b8"},
                                               className="button"),
                                   id='download-link', download="rawdata.csv", href="", target="_blank")
                        ]),
                ],
            ),
            html.Br(),
        ],
    )


app.layout = html.Div([
    html.Div(id="app-container", children=[
        # Banner
        html.Div([html.H2(
                'Database for China Agricultural',
                id='title'
        ),
        ], style={"textAlign": "center"},
            className="banner"
        ),
        # Left column
        html.Div(
            # id="left-column",
            className="twelve columns",
            children=[description_card(), generate_control_card()],
            style={"textAlign": "center"}
        ),
        html.Br(),
        # Right column
        html.Div(
            className="card",
            style={'margin': '10px'},
            children=[
                html.Div(
                    id="mid-column",
                    className="twelve columns",
                    children=[
                        html.Div([html.B(
                            'Data Table',
                            id='table-title'
                        ),
                        ], style={"textAlign": "center",
                                  "font-size": "26px", "padding": "20px"},
                        ),
                        # datatable
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
                                    style_table={'overflowX': 'scroll',
                                                 'overflowY': 'scroll',
                                                 'height': '400px',
                                                 },
                                    style_cell={
                                        'fontSize': 12,
                                        'font-family': 'sans-serif',
                                        'textAlign': 'left'
                                    },
                                    style_header={
                                        'backgroundColor': 'white',
                                        'fontWeight': 'bold'
                                    },
                                    sort_action='native',
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
    ),


    html.Br(),
    html.Br(),
    html.Div(id="graph-container", children=[
        html.Div(
            className="card",
            style={'margin': '10px'},
            children=[
                html.Div(
                    id="mid-left-graph",
                    className="twelve columns",
                    children=[
                        html.Div([html.B(
                            'Pie Chart',
                            id='pie-graph-title',
                            className="card-title"
                        ),
                        ], style={"textAlign": "center", "height": "100%", "width": "100%",
                                  "font-size": "26px", "padding-top": "20px"},
                            className="pie_chart",
                        ),
                        html.Div([
                            dcc.Graph(id="pie-chart"),
                        ]
                        ),
                    ],
                ),
            ],
        ),

        html.Br(),
        html.Br(),

        # mid right graph
        html.Div(
            className="card",
            style={'margin': '10px'},
            children=[
                html.Div(
                    id="mid-right-graph",
                    className="eleven columns",
                    children=[
                        html.Div([html.B(
                            'Bar Chart',
                            id='bar-graph-title'
                        ),
                        ], style={"textAlign": "center", "height": "100%", "width": "100%",
                                  "font-size": "26px", "padding-top": "20px"},
                            className="bar_chart",
                        ),
                        html.Div([
                            dcc.Graph(id="bar-chart"),
                        ]
                        ),
                    ],
                ),
            ],
        ),

        html.Br(),
        html.Br(),

        # bottom graph

        html.Div(
            className="card",
            style={'margin': '10px'},
            children=[
                html.Div(
                    id="bottom-graph",
                    className="eleven columns",
                    children=[
                        html.Div([html.B(
                            'Line Chart',
                            id='line-graph-title'
                        ),
                        ], style={"textAlign": "center", "height": "100%", "width": "100%",
                                  "font-size": "26px", "padding-top": "20px"},
                            className="line_chart",
                        ),
                        html.Div([
                            dcc.Graph(id="line-chart"),
                        ]
                        ),
                    ],
                ),
            ],
        ),
    ]),
])

######################################### UPDATING FIGURES #########################################
# callback for display year-selector or not
@app.callback([Output('year-selector', 'style'), Output('year-selector', 'options')], [Input('table-selector', 'value')])
def update_years_option(selected_table):
    if selected_table in table_list1:
        selected_df = pd.read_excel(PATH.joinpath(
            "(4.21)Database for China Agricultural.xlsx"), sheet_name=selected_table, header=2)
        selected_df = selected_df.fillna(9999)
        years, trim_selected_df, trim_selected_df_T, years_options_list = trim(
            selected_df)

    elif selected_table in table_list2:
        selected_df = pd.read_excel(PATH.joinpath(
            "(4.21)Database for China Agricultural.xlsx"), sheet_name=selected_table, header=1)
        selected_df = selected_df.fillna(9999)
        years, trim_selected_df_T, trim_selected_df, years_options_list = trim3(
            selected_df)

    else:
        selected_df = pd.read_excel(PATH.joinpath(
            "(4.21)Database for China Agricultural.xlsx"), sheet_name=selected_table, header=1)
        selected_df = selected_df.fillna(9999)
        years, trim_selected_df_T, trim_selected_df, years_options_list = trim2(
            selected_df)

    # if selected_table in ["3.1.1a","3.3.1"," 3.7.11",""]:
    return {'display': 'block'}, years_options_list
    # else:
    #    return {'display': 'none'} , years_options_list


@app.callback(Output('year-selector', 'value'), [Input('year-selector', 'options')])
def set_years_value(available_options):
    return available_options[0]['value']

# callback for datatable
@app.callback([Output('table', 'data'), Output('table', 'columns')], [Input('table-selector', 'value')])
def updateTable(selected_table):
    if selected_table in table_list1:
        selected_df = pd.read_excel(PATH.joinpath(
            "(4.21)Database for China Agricultural.xlsx"), sheet_name=selected_table, header=2)

    elif selected_table in table_list2:
        selected_df = pd.read_excel(PATH.joinpath(
            "(4.21)Database for China Agricultural.xlsx"), sheet_name=selected_table, header=1)
        years, trim_selected_df_T, trim_selected_df, years_options_list = trim3(
            selected_df)

    else:
        selected_df = pd.read_excel(PATH.joinpath(
            "(4.21)Database for China Agricultural.xlsx"), sheet_name=selected_table, header=1)
    selected_df = selected_df.drop(selected_df.index[-1])
    dt_col_param = []
    for col in selected_df.columns:
        dt_col_param.append({"name": str(col), "id": str(col)})

    return (selected_df.to_dict('records'), (dt_col_param))

# Callback for csv download
@app.callback(Output('download-link', 'href'), [Input('table-selector', 'value')])
def update_downloader(selected_table):
    selected_df = pd.read_excel(PATH.joinpath(
        "(4.21)Database for China Agricultural.xlsx"), sheet_name=selected_table, header=1)
    csvString = selected_df.to_csv(index=False, encoding='utf-8-sig')
    csvString = "data:text/csv;charset=utf-8-sig,%EF%BB%BF" + \
        urllib.parse.quote(csvString)
    return csvString

# callback for pie chart
@app.callback(Output('pie-chart', 'figure'), [Input('year-selector', 'value'), Input('table-selector', 'value')])
def update_pie_chart(selected_year, selected_table):

    if selected_table in table_list1:
        selected_df = pd.read_excel(PATH.joinpath(
            "(4.21)Database for China Agricultural.xlsx"), sheet_name=selected_table, header=2)
        years, trim_selected_df, trim_selected_df_T, years_options_list = trim(
            selected_df)

    # elif selected_table in table_list2:
    #    selected_df = pd.read_excel(PATH.joinpath("(4.21)Database for China Agricultural.xlsx"),sheet_name = selected_table ,header = 1)
    #    years, trim_selected_df_T, trim_selected_df, years_options_list = trim3(selected_df)

    else:
        selected_df = pd.read_excel(PATH.joinpath(
            "(4.21)Database for China Agricultural.xlsx"), sheet_name=selected_table, header=1)
        years, trim_selected_df_T, trim_selected_df, years_options_list = trim2(
            selected_df)

    return {
        'data': [go.Pie(
            labels=trim_selected_df_T.columns,
            values=trim_selected_df[selected_year].values.tolist(),
            marker={'colors': ['#EF963B', '#C93277', '#349600', '#EF533B', '#57D4F1', '#96D38C']})],
        'layout': go.Layout(title=dict(text=f"Yearly result on "+str(selected_year)),
                            legend=dict(x=0.5, y=-0.2,
                                        font=dict(
                                            family="sans-serif",
                                            size=10,
                                            color="black"
                                        ),
                                        # bgcolor='LightSteelBlue',
                                        xanchor='center',
                                        orientation='h'
                                        ),
                            margin={'l': 0, 'r': 0},
                            autosize=True)}

# callback for bar chart
@app.callback(Output('bar-chart', 'figure'), [Input('table-selector', 'value')])
def update_bar_chart(selected_table):
    trace = []

    selected_df = pd.read_excel(PATH.joinpath(
        "(4.21)Database for China Agricultural.xlsx"), sheet_name=selected_table)
    title = selected_df.columns[0].split(":")[1]

    if selected_table in table_list1:
        selected_df = pd.read_excel(PATH.joinpath(
            "(4.21)Database for China Agricultural.xlsx"), sheet_name=selected_table, header=2)
        years, trim_selected_df, trim_selected_df_T, years_options_list = trim(
            selected_df)

    elif selected_table in table_list2:
        selected_df = pd.read_excel(PATH.joinpath(
            "(4.21)Database for China Agricultural.xlsx"), sheet_name=selected_table, header=1)
        years, trim_selected_df_T, trim_selected_df, years_options_list = trim3(
            selected_df)

    else:
        selected_df = pd.read_excel(PATH.joinpath(
            "(4.21)Database for China Agricultural.xlsx"), sheet_name=selected_table, header=1)
        years, trim_selected_df_T, trim_selected_df, years_options_list = trim2(
            selected_df)

    for i in range(len(years)):
        years[i] = str(years[i])[:4]

    for i in trim_selected_df_T.columns:
        trace.append(
            go.Bar(x=years, y=trim_selected_df_T[i].values.tolist(), name=i,))

    return {
        'data': trace,
        'layout': go.Layout(title=str(title), hovermode="closest",
                            xaxis={'title': "year", 'titlefont': {'color': 'black', 'size': 14},
                                   'tickfont': {'size': 9, 'color': 'black'}},
                            yaxis={'title': "Area (‘000 ha)", 'titlefont': {'color': 'black', 'size': 14, },
                                   'tickfont': {'color': 'black'}})}

# callback for line chart
@app.callback(Output('line-chart', 'figure'), [Input('table-selector', 'value')])
def update_line_chart(selected_table):
    trace = []

    selected_df = pd.read_excel(PATH.joinpath(
        "(4.21)Database for China Agricultural.xlsx"), sheet_name=selected_table)
    title = selected_df.columns[0].split(":")[1]

    if selected_table in table_list1:
        selected_df = pd.read_excel(PATH.joinpath(
            "(4.21)Database for China Agricultural.xlsx"), sheet_name=selected_table, header=2)
        years, trim_selected_df, trim_selected_df_T, years_options_list = trim(
            selected_df)

    # elif selected_table in table_list2:
    #    selected_df = pd.read_excel(PATH.joinpath("(4.21)Database for China Agricultural.xlsx"),sheet_name = selected_table ,header = 1)
    #    years, trim_selected_df_T, trim_selected_df, years_options_list = trim3(selected_df)

    else:
        selected_df = pd.read_excel(PATH.joinpath(
            "(4.21)Database for China Agricultural.xlsx"), sheet_name=selected_table, header=1)
        years, trim_selected_df_T, trim_selected_df, years_options_list = trim2(
            selected_df)

    for i in range(len(years)):
        years[i] = str(years[i])[:4]

    for i in trim_selected_df_T.columns:
        trace.append(go.Scatter(
            x=years, y=trim_selected_df_T[i].values.tolist(), name=i, mode='lines',))

    return {
        'data': trace,
        'layout': go.Layout(title=str(title), colorway=['#fdae61', '#abd9e9', '#2c7bb6'],
                            yaxis={"title": str(trim_selected_df.iloc[0, 0])}, xaxis={"title": "Date"})}


######################################### CSS #########################################

external_css = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css"
    # Normalize the CSS
    "https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css",
    "https://fonts.googleapis.com/css?family=Open+Sans|Roboto"  # Fonts
    "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
    "https://cdn.rawgit.com/TahiriNadia/styles/faf8c1c3/stylesheet.css",
    "https://cdn.rawgit.com/TahiriNadia/styles/b1026938/custum-styles_phyloapp.css",
    # Bootstrap in the end
    "https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css",
    "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css",
    "https://use.fontawesome.com/releases/v5.6.1/css/all.css"
]

for css in external_css:
    app.css.append_css({"external_url": css})

if __name__ == '__main__':
    app.run_server(debug=True)
