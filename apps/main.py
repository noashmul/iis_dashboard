import dash
import numpy as np
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import folium
import dash_table as dt
from pre_process import *
from choroplethmapbox import get_main_tab_map


def generate_table_old(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ], style={'justify-content': 'center'})


def generate_table(dataframe, max_rows=10):
    val = ['table-light', 'table-primary'] * 10
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col, scope="col", className="table-dark") for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Th(dataframe.iloc[i][col], scope="row", className=val[i]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ], className="table table-hover")


dfs_dict = create_dfs_dict()
df = create_df_main_dash(dfs_dict)
# \U000025B2 and \U000025BC are up and down arrows, \U0001F534 and \U0001F7E2 are red and green circles
df['Percent_comparison'] = df['Percent_comparison'].apply(lambda x: "\U000025BC" +
                                                                    "\U0001F534" + str(x) + "%" if x < 0
else "\U000025B2" + "\U0001F7E2 " + " " + str(x) + "%")


layout = html.Div(
            children=[
                html.Div(children=[
                    html.H4(children='Welcome to our dashboard.',
                            style={'text-align': 'left', 'text-transform': 'none', 'font-family': 'sans-serif',
                                   'letter-spacing': '0em'}),
                    html.H4(children='Above are different tabs, a tab for each subject.',
                            style={'text-align': 'left', 'text-transform': 'none', 'font-family': 'sans-serif',
                                   'letter-spacing': '0em'}),
                    html.H4(
                        children='This dashboard is interactive - make sure to hover / choose / click on the visualizations.',
                        style={'text-align': 'left', 'text-transform': 'none', 'font-family': 'sans-serif',
                               'letter-spacing': '0em'}),
                    html.H5(children='The data below is for the date range of X to Y.',
                            style={'text-align': 'left', 'text-transform': 'none', 'font-family': 'sans-serif',
                                   'letter-spacing': '0em'}
                            )
                ] ),
                # html.Iframe(id='map', srcDoc=open('map.html', 'r').read(), width="100%", height="300",
                #             style={'justify-content': 'center', 'text-transform': 'none', 'font-family': 'sans-serif',
                #                    'letter-spacing': '0em'}),
                html.Div(
                            [
                                dcc.Graph(figure=get_main_tab_map(show_text=True))
                            ],
                            className='main_map_container',
                        ),
                generate_table(df),
            ],
            className="pretty_container twelve columns",
            id="cross-filter-options",
            style={"text-align": "justify"},
        )

