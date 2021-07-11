import dash
import numpy as np
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import folium
import dash_table as dt

df = pd.read_csv('df_main_dash.csv')

app = dash.Dash(__name__)
colors = {'title': 'skyblue'}

app.layout = html.Div(children=[
    html.H1(children ='Hadar Neighborhood: Semi-annual report',
    style={'text-align':'center', 'fontSize': 100,'font-family':'sans-serif'
        , 'color':colors['title']}),
    html.Iframe(id='map', srcDoc=open('map.html', 'r').read(), width="70%", height="700",
                style={'justify-content': 'center'}),

    dt.DataTable(id="table",
    columns = [{"name": i, "id": i} for i in df.columns],
              data=df.to_dict('records')
    )
    ])


if __name__ == '__main__':
    app.run_server(debug=True)
