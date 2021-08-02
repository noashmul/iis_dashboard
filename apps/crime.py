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
statistic_area = {'הכל': 0,
                  'גן הבהאים': 612,
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
    if key != 'הכל':
        options.append({'label': key + ' ' + str(value),
                        'value': value})  # TODO value need to be int or str? in Gal's function its int
    else:
        options.append({'label': key,
                        'value': value})

# def generate_table(dataframe, max_rows=10):
#     return html.Table([
#         html.Thead(
#             html.Tr([html.Th(col) for col in dataframe.columns])
#         ),
#         html.Tbody([
#             html.Tr([
#                 html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
#             ]) for i in range(min(len(dataframe), max_rows))
#         ])
#     ], style={'justify-content': 'center'})


@app.callback(
    Output(component_id='crime_trend_graph', component_property='figure'),
    Output(component_id='crime_location_type', component_property='figure'),
    Output(component_id='crime_type', component_property='figure'),
    Input(component_id='areas', component_property='value')
)
def get_graphs(statzone):
    df_crimes = dfs_dict['df_crime_2010_to_2015']
    df_crimes = df_crimes[df_crimes['Year'] == 2012]
    if statzone == 0:
        statzone = 'All Statistical zones'

    if statzone == 'All Statistical zones':
        df_total_crimes = df_crimes.groupby(by=["Month"]).count()[['Street']] / 14
        df_total_crime_all = pd.DataFrame(columns=['Month', 'Amount of Crimes'])
        df_total_crime_all['Month'] = df_total_crimes['Street'].index
        df_total_crime_all['Amount of Crimes'] = df_total_crimes['Street'].values
        fig1 = px.line(df_total_crime_all, x=df_total_crime_all['Month']
                       , y=df_total_crime_all['Amount of Crimes'])

    else:
        # TODO handle the 'All' case
        df_total_crimes = df_crimes.groupby(by=["StatZone", "Month"]).count()[['Street']]
        df_tot_crime_per_area = pd.DataFrame(columns=['Month', 'Amount of Crimes'])
        df_tot_crime_per_area['Month'] = df_total_crimes.loc[statzone]['Street'].index
        df_tot_crime_per_area['Amount of Crimes'] = df_total_crimes.loc[statzone]['Street'].values
        fig1 = px.line(df_tot_crime_per_area, x=df_tot_crime_per_area['Month']
                       , y=df_tot_crime_per_area['Amount of Crimes'])
    fig1.update_layout(title_text=f"Amount of crimes per month in {statzone} stat zone",
                       yaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ),
                       xaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                   ), xaxis_showgrid=True, yaxis_showgrid=True)


    # TODO handle the 'All' case
    # statzone = 621
    if statzone == 'All Statistical zones':
        df_location = df_crimes.groupby(by=["CrimeLocType"]).count()[['Street']] / 14
        df_location = df_location.sort_values(by=['Street'], ascending=False).head(10)
        df_location.index = [s[::-1].strip(' ') for s in df_location.index]
        df_location.rename(columns={'Street': 'Amount of Crimes'}, inplace=True)
    else:
        df_location = df_crimes.groupby(by=["StatZone", "CrimeLocType"]).count()[['Street']]
        df_location = df_location.loc[statzone].sort_values(by=['Street'], ascending=False).head(10)
        df_location.index = [s[::-1].strip(' ') for s in df_location.index]
        df_location.rename(columns ={'Street': 'Amount of Crimes'}, inplace=True)

    fig2 = px.bar(df_location, x=df_location.index, y=df_location['Amount of Crimes'])
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
    fig2.update_xaxes(title='Crime location',tickangle=45)

    if statzone == 'All Statistical zones':
        df_type = df_crimes.groupby(by=["CrimeType"]).count()[['Street']] / 14
        df_type = df_type.sort_values(by=['Street'], ascending=False).head(10)
        df_type.index = [s[::-1].strip(' ') for s in df_type.index]
        df_type.rename(columns={'Street': 'Amount of Crimes'}, inplace=True)
    else:
        df_type = df_crimes.groupby(by=["StatZone", "CrimeType"]).count()[['Street']]
        df_type = df_type.loc[statzone].sort_values(by=['Street'], ascending=False).head(10)
        df_type.index = [s[::-1].strip(' ') for s in df_type.index]
        df_type.rename(columns={'Street': 'Amount of Crimes'}, inplace=True)

    fig3 = px.bar(df_type, x=df_type.index, y=df_type['Amount of Crimes'])
    fig3.update_layout(title_text=f"Amount of crimes per type in {statzone} stat zone",
                       yaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ),
                       xaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ), xaxis_showgrid=True, yaxis_showgrid=True)
    fig3.update_xaxes(title='Crime type',tickangle=45)

    return fig1, fig2, fig3


layout = html.Div(
            children=[

                html.H4(children='Choose the wanted area to see the graphs changes',
                        style={'text-align': 'left', 'text-transform': 'none', 'font-family': 'sans-serif',
                               'letter-spacing': '0em'}
                        ),
                html.Div(
                    [
                        html.Div(
                            [
                                'Choose area: ', dcc.RadioItems(id='areas',
                                                                options=options,
                                                                value=0
                                                                ),
                            ],
                            className="mini_container",
                        ),
                        html.Div(
                            html.Iframe(id='map', srcDoc=open('map.html', 'r').read(), width="80%", height="400px",
                                        style={'justify-content': 'center'}),
                            className="map_container")],
                    id="info-container1",
                    className="row container-display",
                ),
                html.Div(
                    [
                        dcc.Graph(id='crime_trend_graph')
                    ], className="graph_container"
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
                )
            ],
            className="pretty_container twelve columns",
            style={"text-align": "justify"},
        )


