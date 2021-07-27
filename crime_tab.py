import dash
import numpy as np
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px

import folium
import dash_table as dt
from pre_process import *
dfs_dict = create_dfs_dict()


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


def get_crime_trend_graph(statzone):
    df_total_crimes = dfs_dict['df_crime_2010_to_2015']
    df_total_crimes = df_total_crimes[df_total_crimes['Year'] == 2012]
    df_total_crimes = df_total_crimes.groupby(by=["StatZone", "Month"]).count()[['Street']]
    # how to get 12 values for stat zone: df_total_crimes.loc[fill_statzone].loc[fill_month]['Street']

    fig = px.line(df_total_crimes, x=df_total_crimes.loc[statzone]['Street'].index
                  , y=df_total_crimes.loc[statzone]['Street'].values)
    fig.update_layout(title_text=f"Amount of crimes per month in {statzone} stat zone)",
                      yaxis=dict(
                          titlefont_size=18,
                          tickfont_size=18,
                      ),
                      xaxis=dict(
                          titlefont_size=18,
                          tickfont_size=18,
                      ), xaxis_showgrid=True, yaxis_showgrid=True)
    fig.update_yaxes(title='Amount of crimes')
    fig.update_xaxes(title='month in 2012')
    return fig


def get_crime_graph(statzone, graph_type: str):
    df_location = dfs_dict['df_crime_2010_to_2015']
    df_location = df_location[df_location['Year'] == 2012]
    df_location = df_location.groupby(by=["StatZone", graph_type]).count()[['Street']]

    df_location = df_location.loc[statzone].sort_values(by=['Street'], ascending=False).head(10)

    fig = px.bar(df_location, x=df_location.index, y=df_location.Street)
    for_title = "crimes per location" if graph_type=="CrimeLocType" else "crimes per type"
    fig.update_layout(title_text=f"Amount of {for_title} in {statzone} stat zone",
                      yaxis=dict(
                          titlefont_size=18,
                          tickfont_size=18,
                      ),
                      xaxis=dict(
                          titlefont_size=18,
                          tickfont_size=18,
                      ), xaxis_showgrid=True, yaxis_showgrid=True)
    fig.update_yaxes(title='Amount of crimes')
    fig.update_xaxes(title='Crime location' if graph_type=="CrimeLocType" else "Crime type")
    return fig

# df = create_df_main_dash(dfs_dict)
# df['Percent_comparison'] = df['Percent_comparison'].apply(lambda x:
#               "⇩\U0001F534" + str(x) + "%" if x < 0
#               else "⇧\U0001F7E2 " + " " + str(x) + "%")

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {'title': 'skyblue'}

app.layout = html.Div(
[
    html.Div(
        children=[
            html.H3(children='Hadar Neighborhood: Semi-annual report',
                    style={'text-align': 'center', 'font-family': ' sans-serif','color': colors['title']}),
            html.H4(children='***Placeholder for the tabs buttons***',
                    style={'text-align': 'center'}),
            html.H6(children='The data below is for the date range of X to Y.'),
            html.Div(
                [
                    html.Div(
                        [
                            html.P(id="well_text"),
                            html.P("***Placeholder for the stats zones buttons***", style={"text-align": "center", "font-weight": "bold"}),
                        ],
                        className="mini_container",
                        id="wells",
                    ),
                    html.Iframe(id='map', srcDoc=open('map.html', 'r').read(), width="80%", height="300",
                                style={'justify-content': 'center'}),
                ],
                id="info-container1",
                className="row container-display",
            ),
            html.Div(
                [
                dcc.Graph(id='crime_trend_graph', figure=get_crime_trend_graph(statzone=611)) # TODO put here the chosen statzone
                ]
            ),
            html.Div(
                [
                    html.Div(
                        [
                            dcc.Graph(id='crime_location_type', figure=get_crime_graph(statzone=611, graph_type='CrimeLocType'))
                        ],
                        className="pretty_container six columns",
                        # id="wells",
                    ),
                    html.Div(
                        [
                            dcc.Graph(id='crime_type', figure=get_crime_graph(statzone=611, graph_type='CrimeType'))
                        ],
                        className="pretty_container six columns",
                        # id="wells",
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
]
)

if __name__ == '__main__':
    app.run_server(debug=True)


#
# html.Div([
#         html.Div(
#             children=[
#                 generate_table(df),
#             ],
#         # className="pretty_container three columns",
#         ),
#         html.Div(className="one-third column", )
#         ,
#         html.Div(
#             children=[
#                 generate_table(df),
#             ],
#         # className="pretty_container three columns",
#         ),
#
#     ], className="row container-display"
# )