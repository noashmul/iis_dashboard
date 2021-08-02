import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from app_def import app
from choroplethmapbox import get_choroplethmap_fig

import pandas as pd
import numpy as np

from choroplethmapbox import get_area_in_km2_for_stat_zones

from pre_process import *


# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


# app = dash.Dash(__name__, )
# external_stylesheets=external_stylesheets)
# statistic_area_ = ['All', '611', '612', '613', '621', '622', '623', '631', '632', '633', '634',
#                    '641', '642', ' 643', '644']
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
    if key != 'הכל':
        options.append({'label': "  " + key + ' ' + str(value),
                        'value': value})
    else:
        options.append({'label': "  " + key,
                        'value': value})

layout = html.Div([
    html.H3("Change the value to see callbacks in action!"),
    html.Div(
        id="app-container",
        children=[
            html.Div(className='narrow_container', children=[
                html.Div(id="left-column", className="pretty_container", children=[
                    html.Div(className="slider-container",
                             children=[
                                 html.H5("Choose weights"),
                                 html.P(id="slider-text1", children="Choose the wanted weight 1:",
                                        style={'color': 'black'},
                                        ),
                                 dcc.Slider(id="Weight 1", min=0.0, max=1.0, value=0.5, step=None,
                                            marks={str(num): {"label": str(num), "style": {"color": "#7fafdf"}, }
                                                   for num in [0, 0.25, 0.5, 0.75, 1]
                                                   }),
                                 html.P(id="slider-text2", children="Choose the wanted weight 2:",
                                        style={'color': 'black'},
                                        ),
                                 dcc.Slider(id="Weight 2", min=0.0, max=1.0, value=0.5, step=None,
                                            marks={str(num): {"label": str(num), "style": {"color": "#7fafdf"}, }
                                                   for num in [0, 0.25, 0.5, 0.75, 1]
                                                   }),
                                 html.P(id="slider-text3", children="Choose the wanted weight 3:",
                                        style={'color': 'black'},
                                        ),
                                 dcc.Slider(id="Weight 3", min=0.0, max=1.0, value=0.5, step=None,
                                            marks={str(num): {"label": str(num), "style": {"color": "#7fafdf"}, }
                                                   for num in [0, 0.25, 0.5, 0.75, 1]
                                                   }),
                                 html.P(id="slider-text4", children="Choose the wanted weight 4:",
                                        style={'color': 'black'},
                                        ),
                                 dcc.Slider(id="Weight 4", min=0.0, max=1.0, value=0.5, step=None,
                                            marks={str(num): {"label": str(num), "style": {"color": "#7fafdf"}, }
                                                   for num in [0, 0.25, 0.5, 0.75, 1]
                                                   }),
                                 html.P(id="slider-text5", children="Choose the wanted weight 5:",
                                        style={'color': 'black'},
                                        ),
                                 dcc.Slider(id="Weight 5", min=0.0, max=1.0, value=0.5, step=None,
                                            marks={str(num): {"label": str(num), "style": {"color": "#7fafdf"}, }
                                                   for num in [0, 0.25, 0.5, 0.75, 1]
                                                   }),
                                 html.P(id="slider-text6", children="Choose the wanted weight 6:",
                                        style={'color': 'black'},
                                        ),
                                 dcc.Slider(id="Weight 6", min=0.0, max=1.0, value=0.5, step=None,
                                            marks={str(num): {"label": str(num), "style": {"color": "#7fafdf"}, }
                                                   for num in [0, 0.25, 0.5, 0.75, 1]
                                                   }),
                                 html.P(id="slider-text7", children="Choose the wanted weight 7:",
                                        style={'color': 'black'},
                                        ),
                                 dcc.Slider(id="Weight 7", min=0.0, max=1.0, value=0.5, step=None,
                                            marks={str(num): {"label": str(num), "style": {"color": "#7fafdf"}, }
                                                   for num in [0, 0.25, 0.5, 0.75, 1]
                                                   }),
                                 html.P(id="slider-text8", children="Choose the wanted weight 8:",
                                        style={'color': 'black'},
                                        ),
                                 dcc.Slider(id="Weight 8", min=0.0, max=1.0, value=0.5, step=None,
                                            marks={str(num): {"label": str(num), "style": {"color": "#7fafdf"}, }
                                                   for num in [0, 0.25, 0.5, 0.75, 1]
                                                   }),
                                 html.P(id="slider-text9", children="Choose the wanted weight 9:",
                                        style={'color': 'black'},
                                        ),
                                 dcc.Slider(id="Weight 9", min=0.0, max=1.0, value=0.5, step=None,
                                            marks={str(num): {"label": str(num), "style": {"color": "#7fafdf"}, }
                                                   for num in [0, 0.25, 0.5, 0.75, 1]
                                                   }),
                                 html.P(id="slider-text10", children="Choose the wanted weight 10:",
                                        style={'color': 'black'},
                                        ),
                                 dcc.Slider(id="Weight 10", min=0.0, max=1.0, value=0.5, step=None,
                                            marks={str(num): {"label": str(num), "style": {"color": "#7fafdf"}, }
                                                   for num in [0, 0.25, 0.5, 0.75, 1]
                                                   }),
                                 html.P(id="slider-text11", children="Choose the wanted weight 11:",
                                        style={'color': 'black'},
                                        ),
                                 dcc.Slider(id="Weight 11", min=0.0, max=1.0, value=0.5, step=None,
                                            marks={str(num): {"label": str(num), "style": {"color": "#7fafdf"}, }
                                                   for num in [0, 0.25, 0.5, 0.75, 1]
                                                   }),
                                 html.P(id="slider-text12", children="Choose the wanted weight 12:",
                                        style={'color': 'black'},
                                        ),
                                 dcc.Slider(id="Weight 12", min=0.0, max=1.0, value=0.5, step=None,
                                            marks={str(num): {"label": str(num), "style": {"color": "#7fafdf"}, }
                                                   for num in [0, 0.25, 0.5, 0.75, 1]
                                                   }),
                             ]),
                    html.Div(className="mini_container",
                             children=[
                                 html.H5("Choose areas"),
                                 html.Div(
                                     [
                                         dcc.RadioItems(id='areas',
                                                        options=options,
                                                        value='MTL'
                                                        ),
                                         # html.Br(),
                                         # dcc.Graph(id='graph_with_slider'),
                                         # dcc.Graph(id='graph_with_slider2')

                                     ])])
                ])]),
            html.Div(className='narrow_container', children=[
                html.Div(
                    id="graph-container",
                    children=[
                        # html.P(id="chart-selector", children="Select chart:"),
                        dcc.Graph(id='graph_with_slider')
                    ])
            ])])])

def calc_safety_scores(StatZone, df_salary, df_conflicts,df_cameras, df_aband, df_106,
                       df_crimes):
    df_area_salary = df_salary[df_salary['StatZone']==StatZone]
    df_area_cameras = df_cameras[df_cameras['StatZone']==StatZone]
    df_ares_aband = df_aband[df_aband['StatZone']==StatZone]
    df_area_106_security = df_106[(df_106['stat_zone_number'] == StatZone) &
                                  (df_106['בעל המשימה'] == 'בטחון')]
    df_area_106_social = df_106[(df_106['stat_zone_number'] == StatZone) &
                                  (df_106['בעל המשימה'] == 'רווחה הדר/עיר תחתית')]

    df_area_crimes = df_crimes[df_crimes['StatZone']==StatZone]

    StatZone_size_dict = get_area_in_km2_for_stat_zones()

#******* Variables ********#
    population = df_area_salary['ResNum']
    Tot_crimes = df_crimes[df_crimes.columns[2:]].sum().sum()
    Tot_area_crimes = df_area_crimes[df_area_crimes.columns[2:]].sum(axis=1)
    HaifaAvgIncome = 13110
    Demographic_density_haifa = 271291 / 63.67

#******************* PART 1 SCORES **********************#
    conflicts_s = 1 - (df_conflicts[df_conflicts['StatZone'] == StatZone]['Conflicts'] / population)
    cameras_s = ((len(df_area_cameras)*1000) / population)
    aband_s = (1-len(df_ares_aband) / population)
    security_106_s = (1- len(df_area_106_security) / population)
    social_106_s = (1-len(df_area_106_social) / population)

# ******************* PART 2 -CRIME SCORES **********************#
    crime_s  = 1-Tot_area_crimes/Tot_crimes
    crime_thefts_s  = 1-df_area_crimes['Thefts']/Tot_area_crimes
    crime_BodyAssaults_s = 1 - df_area_crimes['BodyAssaults'] / Tot_area_crimes
    crime_SexualAssaults_s = 1 - df_area_crimes['SexualAssaults'] / Tot_area_crimes
    crime_Robbery_s = 1 - df_area_crimes['Robbery'] / Tot_area_crimes

# ******************* PART 3 -INCOME SCORES **********************#
    income_avg_s = df_area_salary['IncSelfAve'] / HaifaAvgIncome
    Demographic_density_area = population/StatZone_size_dict[StatZone]
    Demographic_density_s = Demographic_density_area / Demographic_density_haifa

    X_features = [conflicts_s, cameras_s, aband_s, security_106_s, social_106_s, crime_s,\
           crime_thefts_s, crime_BodyAssaults_s, crime_SexualAssaults_s, crime_Robbery_s, \
           income_avg_s , Demographic_density_s]
    X_features = [x.values[0] for x in X_features]
    return X_features



@app.callback(
    Output(component_id='graph_with_slider', component_property='figure'),
    Input(component_id='Weight 1', component_property='value'),
    Input(component_id='Weight 2', component_property='value'),
    Input(component_id='Weight 3', component_property='value'),
    Input(component_id='Weight 4', component_property='value'),
    Input(component_id='Weight 5', component_property='value'),
    Input(component_id='Weight 6', component_property='value'),
    Input(component_id='Weight 7', component_property='value'),
    Input(component_id='Weight 8', component_property='value'),
    Input(component_id='Weight 9', component_property='value'),
    Input(component_id='Weight 10', component_property='value'),
    Input(component_id='Weight 11', component_property='value'),
    Input(component_id='Weight 12', component_property='value'),
    Input(component_id='areas', component_property='value')
)
def update_output_div(w1, w2, w3, w4, w5, w6, w7, w8, w9, w10, w11, w12, area):
    """
    create all the graphs that rely on the input values (weights and area)
    :param w1: weight value
    :param w2: weight value
    :param area: statistic ares (or 'All')
    :return: all wanted figures
    """
    W = [w1, w2, w3, w4, w5, w6, w7, w8, w9, w10, w11, w12]
    W = [float(i)/sum(W) for i in W]
    values_dict = dict.fromkeys([611, 612, 613, 621, 622, 623, 631, 632, 633, 634, 641, 642, 643, 644], 0.)
    data = dict.fromkeys([611, 612, 613, 621, 622, 623, 631, 632, 633, 634, 641, 642, 643, 644], 0.)

    #load dfs
    df_salaries_t1 = dfs_dict['df_salaries_t1']
    df_conflicts_t1 = dfs_dict['df_conflicts_t1']
    df_cameras = dfs_dict['df_cameras_t1']
    df_aband = dfs_dict['df_aband_t1']
    df_106 = dfs_dict['df_106_t1']
    df_crimes = dfs_dict['df_crime_t1']

    for StatZone in values_dict.keys():
        X_features = calc_safety_scores(StatZone, df_salaries_t1, df_conflicts_t1, df_cameras, df_aband, df_106,
                                        df_crimes)
        data[StatZone] = X_features

    df_scores = pd.DataFrame(data.values(),
                         columns=['conflicts_s', 'cameras_s', 'aband_s', 'security_106_s', 'social_106_s', 'crime_s', \
                                  'crime_thefts_s', 'crime_BodyAssaults_s', 'crime_SexualAssaults_s', 'crime_Robbery_s', \
                                  'income_avg_s', 'Demographic_density_s'])
    df_scores['StatZone'] = data.keys()
    for col in df_scores.columns[:-1]:
        df_scores[col] = (df_scores[col] - df_scores[col].min()) / (df_scores[col].max() - df_scores[col].min())

    SafetyScore_lst =[]
    for idx,row in df_scores.iterrows():
        tmp_score = sum(np.multiply(list(row[:-1]),W))
        SafetyScore_lst.append(tmp_score)

    df_scores['SafetyScore'] = SafetyScore_lst

    for StatZone in values_dict.keys():
        area_score = df_scores[df_scores['StatZone']==StatZone]['SafetyScore'].values[0]
        values_dict[StatZone] = area_score*100

    fig = get_choroplethmap_fig(values_dict=values_dict, map_title="Exmple Title",is_safety_map=True )
    return fig

# if __name__ == '__main__':
#     app.run_server(debug=True)
#     values_dict = dict.fromkeys([611, 612, 613, 621, 622, 623, 631, 632, 633, 634, 641, 642, 643, 644], 0.)
#     data = dict.fromkeys([611, 612, 613, 621, 622, 623, 631, 632, 633, 634, 641, 642, 643, 644], 0.)
#     W = [1,2,3,4,5,6,7,8,9,10,11,12]
#     W = [float(i)/sum(W) for i in W]
#     #load dfs
#     df_salaries_t1 = dfs_dict['df_salaries_t1']
#     df_conflicts_t1 = dfs_dict['df_conflicts_t1']
#     df_cameras = dfs_dict['df_cameras_t1']
#     df_aband = dfs_dict['df_aband_t1']
#     df_106 = dfs_dict['df_106_t1']
#     df_crimes = dfs_dict['df_crime_t1']
#
#     for StatZone in values_dict.keys():
#         X_features = calc_safety_scores(StatZone, df_salaries_t1, df_conflicts_t1, df_cameras, df_aband, df_106,
#                                         df_crimes)
#         data[StatZone] = X_features
#
#     df_scores = pd.DataFrame(data.values(),
#                          columns=['conflicts_s', 'cameras_s', 'aband_s', 'security_106_s', 'social_106_s', 'crime_s', \
#                                   'crime_thefts_s', 'crime_BodyAssaults_s', 'crime_SexualAssaults_s', 'crime_Robbery_s', \
#                                   'income_avg_s', 'Demographic_density_s'])
#     df_scores['StatZone'] = data.keys()
#     for col in df_scores.columns[:-1]:
#         df_scores[col] = (df_scores[col] - df_scores[col].min()) / (df_scores[col].max() - df_scores[col].min())
#
#     SafetyScore_lst =[]
#     for idx,row in df_scores.iterrows():
#         tmp_score = sum(np.multiply(list(row[:-1]),W))
#         SafetyScore_lst.append(tmp_score)
#
#     df_scores['SafetyScore'] = SafetyScore_lst
#
#     for StatZone in values_dict.keys():
#         area_score = df_scores[df_scores['StatZone']==StatZone]['SafetyScore'].values[0]
#         values_dict[StatZone] = area_score
#
#
