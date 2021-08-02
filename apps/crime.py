import dash
import numpy as np
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px

import folium
import dash_table as dt
from app_def import app
from pre_process import *

dfs_dict = create_dfs_dict()

# TODO add 'ALL' option
statistic_area = {'גן הבהאים': 612,
                  'הדר מזרח - גאולה': 642,
                  'הדר מזרח - רח\' יל"ג': 641,
                  "הדר מערב - רח' אלמותנבי": 611,
                  "הדר מערב - רח' מסדה": 613,
                  'הדר מרכז - בית העירייה': 633,
                  'הדר מרכז - התיאטרון העירוני': 631,
                  "הדר מרכז - רח' הרצליה": 632,
                  'הדר מרכז - שוק תלפיות': 634,
                  "הדר עליון - רח' הפועל": 622,
                  'הדר עליון -בי"ח בני ציון': 621,
                  'מעונות גאולה': 644,
                  "רמת הדר - רח' המיימוני": 623,
                  "רמת ויז'ניץ": 643}
options = list()
for key, value in statistic_area.items():
    options.append({'label': key + ' ' + str(value),
                    'value': value})  # TODO value need to be int or str? in Gal's function its int


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


@app.callback(
    Output(component_id='crime_trend_graph', component_property='figure'),
    Output(component_id='crime_location_type', component_property='figure'),
    Output(component_id='crime_type', component_property='figure'),
    Input(component_id='areas', component_property='value')
)
def get_graphs(statzone):
    # TODO handle the 'All' case
    df_crimes = dfs_dict['df_crime_2010_to_2015']
    df_crimes = df_crimes[df_crimes['Year'] == 2012]
    df_total_crimes = df_crimes.groupby(by=["StatZone", "Month"]).count()[['Street']]

    fig1 = px.line(df_total_crimes, x=df_total_crimes.loc[statzone]['Street'].index
                   , y=df_total_crimes.loc[statzone]['Street'].values)
    fig1.update_layout(title_text=f"Amount of crimes per month in {statzone} stat zone)",
                       yaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ),
                       xaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ), xaxis_showgrid=True, yaxis_showgrid=True)
    fig1.update_yaxes(title='Amount of crimes')
    fig1.update_xaxes(title='month in 2012')

    # TODO handle the 'All' case
    df_location = df_crimes.groupby(by=["StatZone", "CrimeLocType"]).count()[['Street']]
    df_location = df_location.loc[statzone].sort_values(by=['Street'], ascending=False).head(10)

    fig2 = px.bar(df_location, x=df_location.index, y=df_location.Street)
    # for_title = "crimes per location" if graph_type == "CrimeLocType" else "crimes per type"
    fig2.update_layout(title_text=f"Amount of crimes per location in {statzone} stat zone",
                       yaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ),
                       xaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ), xaxis_showgrid=True, yaxis_showgrid=True)
    fig2.update_yaxes(title='Amount of crimes')
    fig2.update_xaxes(title='Crime location')

    df_type = df_crimes.groupby(by=["StatZone", "CrimeType"]).count()[['Street']]
    df_type = df_type.loc[statzone].sort_values(by=['Street'], ascending=False).head(10)

    fig3 = px.bar(df_type, x=df_type.index, y=df_type.Street)
    fig3.update_layout(title_text=f"Amount of crimes per type in {statzone} stat zone",
                       yaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ),
                       xaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ), xaxis_showgrid=True, yaxis_showgrid=True)
    fig3.update_yaxes(title='Amount of crimes')
    fig3.update_xaxes(title='Crime type')

    return fig1, fig2, fig3


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
colors = {'title': 'skyblue'}

layout = html.Div(
    [
        html.Div(
            children=[
                html.H3(children='Hadar Neighborhood: Semi-annual report',
                        style={'text-align': 'center', 'font-family': ' sans-serif', 'color': colors['title']}),
                html.P(children='The data below is for the date range of X to Y.'),
                html.Div(
                    [
                        html.Div(
                            [
                                'Choose area: ', dcc.RadioItems(id='areas',
                                                                options=options,
                                                                value=611
                                                                ),
                            ],
                            className="mini_container",
                        ),
                        html.Div(
                            html.Iframe(id='map', srcDoc=open('map.html', 'r').read(), width="80%", height="300",
                                        style={'justify-content': 'center'}),
                            className="map_container")],
                    id="info-container1",
                    className="row container-display",
                ),
                html.Div(
                    [
                        dcc.Graph(id='crime_trend_graph')
                    ], className="mini_container"
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Graph(id='crime_location_type')
                            ],  # TODO fix the hebrew order, maybe with: lang='he',
                            className='narrow_container',
                        ),
                        html.Div(
                            [
                                dcc.Graph(id='crime_type')
                            ],
                            className='narrow_container',
                        ),
                    ],
                    id="info-container2",
                    className="row container-display",
                ),
            ],
            className="pretty_container twelve columns",
            id="cross-filter-options1",
            style={"text-align": "justify"},
        ),
    ])
