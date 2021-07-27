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


def generate_table(dataframe, max_rows=10):
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


dfs_dict = create_dfs_dict()
df = create_df_main_dash(dfs_dict)
df['Percent_comparison'] = df['Percent_comparison'].apply(lambda x:
              "⇩\U0001F534" + str(x) + "%" if x < 0
              else "⇧\U0001F7E2 " + " " + str(x) + "%")

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {'title': 'skyblue'}

layout = html.Div(
[
    html.Div(
        children=[
            html.H3(children='Hadar Neighborhood: Semi-annual report',
                    style={'text-align': 'center', 'font-family': ' sans-serif','color': colors['title']}),
            html.H6(children='Welcome to our dashboard.',
                    style={'text-align': 'center'}),
            html.H6(children='Above are different tabs, a tab for each subject.',
                    style={'text-align': 'center'}),
            html.H6(children='This dashboard is interactive - make sure to hover / choose / click on the visualizations.',
                    style={'text-align': 'center'}),
            html.P(children='The data below is for the date range of X to Y.'),
            html.Iframe(id='map', srcDoc=open('../map.html', 'r').read(), width="100%", height="300",
                        style={'justify-content': 'center'}),
            generate_table(df),
        ],
        className="pretty_container twelve columns",
        id="cross-filter-options",
        style={"text-align": "justify"},
    ),
]
)

if __name__ == '__main__':
    app.run_server(debug=True)
