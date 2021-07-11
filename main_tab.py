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

df = pd.read_csv('gal_data.csv')

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(
    html.H1('Hadar Neighborhood: Semi-annual report'),
    html.Iframe(id='map', srcDoc=open('map.html', 'r').read(), width="90%", height="700")
    ),
    dt.DataTable(id="table",
    columns = [{"name": i, "id": i} for i in df.columns],
              data = df.to_dict('records')
    )
    ])



if __name__ == '__main__':
    app.run_server(debug=True)
