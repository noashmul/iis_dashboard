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

dfs_dict = create_dfs_dict()
df = create_df_main_dash(dfs_dict)
# df = pd.read_csv('gal_data.csv')

colors = {'title': 'skyblue'}

layout = html.Div(children=[
    html.H1(children ='Hadar Neighborhood: Semi-annual report',
    style={'text-align':'center', 'fontSize': 50,'font-family':'sans-serif'
        , 'color':colors['title']}),
    html.Iframe(id='map', srcDoc=open('map.html', 'r').read(), width="70%", height="700",
                style={'justify-content': 'center'}),

    dt.DataTable(id="table",
    columns = [{"name": i, "id": i} for i in df.columns],
              data=df.to_dict('records')
    )
    ])


