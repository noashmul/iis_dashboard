import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from app_def import app
from choroplethmapbox import get_choroplethmap_fig
import dash_bootstrap_components as dbc
from dash.dependencies import State
import numpy as np
# import plotly.io as pio
# pio.renderers.default = "browser"
from choroplethmapbox import get_area_in_km2_for_stat_zones
from pre_process import *

#### Create scores #####
df_salaries_t1 = dfs_dict['df_salaries_t1']
df_salaries_t0 = dfs_dict['df_salaries_t0']
df_conflicts_t1 = dfs_dict['df_conflicts_t1']
df_conflicts_t0 = dfs_dict['df_conflicts_t0']
df_cameras_t1 = dfs_dict['df_cameras_t1']
df_cameras_t0 = dfs_dict['df_cameras_t0']
df_aband_t1 = dfs_dict['df_aband_t1']
df_aband_t0 = dfs_dict['df_aband_t0']
df_106_t1 = dfs_dict['df_106_t1']
df_106_t0 = dfs_dict['df_106_t0']
df_crimes_t1 = dfs_dict['df_crime_t1']
df_crimes_t0 = dfs_dict['df_crime_t0']
StatZone_size_dict = get_area_in_km2_for_stat_zones()


def calc_safety_scores(StatZone, df_salary, df_conflicts, df_cameras, df_aband, df_106,
                       df_crimes):
    df_area_salary = df_salary[df_salary['StatZone'] == StatZone]
    df_area_cameras = df_cameras[df_cameras['StatZone'] == StatZone]
    df_ares_aband = df_aband[df_aband['StatZone'] == StatZone]
    df_area_106_security = df_106[(df_106['stat_zone_number'] == StatZone) &
                                  (df_106['בעל המשימה'] == 'בטחון')]
    df_area_106_social = df_106[(df_106['stat_zone_number'] == StatZone) &
                                (df_106['בעל המשימה'] == 'רווחה הדר/עיר תחתית')]

    df_area_crimes = df_crimes[df_crimes['StatZone'] == StatZone]

    # ******* Variables ********#
    population = df_area_salary['ResNum']
    Tot_crimes = df_crimes[df_crimes.columns[2:]].sum().sum()
    Tot_area_crimes = df_area_crimes[df_area_crimes.columns[2:]].sum(axis=1)
    HaifaAvgIncome = 13110
    Demographic_density_haifa = 271291 / 63.67

    # ******************* PART 1 SCORES **********************#
    conflicts_s = 1 - (df_conflicts[df_conflicts['StatZone'] == StatZone]['Conflicts'] / population)
    cameras_s = ((len(df_area_cameras) * 1000) / population)
    aband_s = (1 - len(df_ares_aband) / population)
    security_106_s = (1 - len(df_area_106_security) / population)
    social_106_s = (1 - len(df_area_106_social) / population)

    # ******************* PART 2 -CRIME SCORES **********************#
    crime_s = 1 - Tot_area_crimes / Tot_crimes
    crime_thefts_s = 1 - df_area_crimes['Thefts'] / Tot_area_crimes
    crime_BodyAssaults_s = 1 - df_area_crimes['BodyAssaults'] / Tot_area_crimes
    crime_SexualAssaults_s = 1 - df_area_crimes['SexualAssaults'] / Tot_area_crimes
    crime_Robbery_s = 1 - df_area_crimes['Robbery'] / Tot_area_crimes

    # ******************* PART 3 -INCOME SCORES **********************#
    income_avg_s = df_area_salary['IncSelfAve'] / HaifaAvgIncome
    Demographic_density_area = population / StatZone_size_dict[StatZone]
    Demographic_density_s = Demographic_density_area / Demographic_density_haifa

    X_features = [conflicts_s, cameras_s, aband_s, security_106_s, social_106_s, crime_s, \
                  crime_thefts_s, crime_BodyAssaults_s, crime_SexualAssaults_s, crime_Robbery_s, \
                  income_avg_s, Demographic_density_s]
    X_features = [x.values[0] for x in X_features]
    return X_features


def create_safety_table(df_salaries, df_conflicts, df_cameras, df_aband, df_106, df_crimes):
    values_dict = dict.fromkeys([611, 612, 613, 621, 622, 623, 631, 632, 633, 634, 641, 642, 643, 644], 0.)
    data = dict.fromkeys([611, 612, 613, 621, 622, 623, 631, 632, 633, 634, 641, 642, 643, 644], 0.)

    for StatZone in values_dict.keys():
        X_features = calc_safety_scores(StatZone, df_salaries, df_conflicts, df_cameras, df_aband, df_106,
                                        df_crimes)
        data[StatZone] = X_features

    df_score = pd.DataFrame(data.values(),
                            columns=['conflicts_s', 'cameras_s', 'aband_s', 'security_106_s', 'social_106_s', 'crime_s', \
                                     'crime_thefts_s', 'crime_BodyAssaults_s', 'crime_SexualAssaults_s',
                                     'crime_Robbery_s', 'income_avg_s', 'Demographic_density_s'])
    df_score['StatZone'] = data.keys()
    for col in df_score.columns[:-1]:
        df_score[col] = (df_score[col] - df_score[col].min()) / (df_score[col].max() - df_score[col].min())

    return df_score, values_dict


df_score_t1, values_dict_t1 = create_safety_table(df_salaries_t1, df_conflicts_t1, df_cameras_t1, df_aband_t1,
                                                  df_106_t1, df_crimes_t1)
df_score_t0, values_dict_t0 = create_safety_table(df_salaries_t0, df_conflicts_t0, df_cameras_t0, df_aband_t0,
                                                  df_106_t0, df_crimes_t0)

statistic_area = {'הכל': 0,
                  "הדר מערב - רח' אלמותנבי": 611,
                  'גן הבהאים': 612,
                  "הדר מערב - רח' מסדה": 613,
                  'הדר עליון -בי"ח בני ציון': 621,
                  "הדר עליון - רח' הפועל": 622,
                  "רמת הדר - רח' המיימוני": 623,
                  'הדר מרכז - התיאטרון העירוני': 631,
                  "הדר מרכז - רח' הרצליה": 632,
                  'הדר מרכז - בית העירייה': 633,
                  'הדר מרכז - שוק תלפיות': 634,
                  'הדר מזרח - רח\' יל"ג': 641,
                  'הדר מזרח - גאולה': 642,
                  "רמת ויז'ניץ": 643,
                  'מעונות גאולה': 644}

options = list()
for key, value in statistic_area.items():
    if key != 'הכל':
        options.append({'label': "  " + key + ' ' + str(value),
                        'value': value})
    else:
        options.append({'label': "  " + key,
                        'value': value})

layout = html.Div(children=[
    html.Div([html.H4(
        'Choose the weight for each component in the safety formula to influence the score in each Stat Zone',
        style={'text-align': 'left', 'text-transform': 'none', 'font-family': 'sans-serif',
               'letter-spacing': '0em'}, )],
        className='pretty_container'
    ),

    html.Div([html.Div(
        dbc.Card(
            [
                dbc.CardHeader(
                    html.H2(
                        dbc.Button(
                            "\U0001F446" + "  Click here to select the importance of each attribute to the final score for each statistical zone   "
                            + "\U000021E9",
                            color="link",
                            id=f"group-1-toggle",
                            n_clicks=0,
                            style={'text-align': 'center', 'text-transform': 'none', 'font-family': 'sans-serif',
                                   'letter-spacing': '0em', 'font-size': 20},
                        ),
                    ),
                ),
                dbc.Collapse(
                    dbc.CardBody([html.Div([html.P(id="slider-text1", children="ציון קונפליקטים בין שכנים",
                                                   style={'color': 'black', 'text-align': 'left'},
                                                   ),
                                            dcc.Slider(id="Weight 1", min=1, max=5, value=1, step=None,
                                                       marks={
                                                           str(num): {"label": str(num),
                                                                      "style": {"color": "#7fafdf"}, }
                                                           for num in [1, 2, 3, 4, 5]
                                                       }),
                                            html.P(id="slider-text2", children="ציון מצלמות אבטחה",
                                                   style={'color': 'black'},
                                                   ),
                                            dcc.Slider(id="Weight 2", min=1, max=5, value=1, step=None,
                                                       marks={
                                                           str(num): {"label": str(num),
                                                                      "style": {"color": "#7fafdf"}, }
                                                           for num in [1, 2, 3, 4, 5]
                                                       }),
                                            html.P(id="slider-text3", children="ציון בתים נטושים",
                                                   style={'color': 'black'},
                                                   ),
                                            dcc.Slider(id="Weight 3", min=1, max=5, value=1, step=None,
                                                       marks={
                                                           str(num): {"label": str(num),
                                                                      "style": {"color": "#7fafdf"}, }
                                                           for num in [1, 2, 3, 4, 5]
                                                       }),
                                            html.P(id="slider-text4", children="ציון שיחות למוקד העירייה בנושא ביטחון",
                                                   style={'color': 'black'},
                                                   ),
                                            dcc.Slider(id="Weight 4", min=1, max=5, value=1, step=None,
                                                       marks={
                                                           str(num): {"label": str(num),
                                                                      "style": {"color": "#7fafdf"}, }
                                                           for num in [1, 2, 3, 4, 5]
                                                       }),
                                            ], className="slider-container"),
                                  html.Div([html.P(id="slider-text5", children="ציון שיחות למוקד העירייה בנושא סוציאלי",
                                                   style={'color': 'black'},
                                                   ),
                                            dcc.Slider(id="Weight 5", min=1, max=5, value=1, step=None,
                                                       marks={
                                                           str(num): {"label": str(num),
                                                                      "style": {"color": "#7fafdf"}, }
                                                           for num in [1, 2, 3, 4, 5]
                                                       }),
                                            html.P(id="slider-text6", children="ציון פשיעה",
                                                   style={'color': 'black'},
                                                   ),
                                            dcc.Slider(id="Weight 6", min=1, max=5, value=1, step=None,
                                                       marks={
                                                           str(num): {"label": str(num),
                                                                      "style": {"color": "#7fafdf"}, }
                                                           for num in [1, 2, 3, 4, 5]
                                                       }),
                                            html.P(id="slider-text7", children="ציון גניבות",
                                                   style={'color': 'black'},
                                                   ),
                                            dcc.Slider(id="Weight 7", min=1, max=5, value=1, step=None,
                                                       marks={
                                                           str(num): {"label": str(num),
                                                                      "style": {"color": "#7fafdf"}, }
                                                           for num in [1, 2, 3, 4, 5]
                                                       }),
                                            html.P(id="slider-text8", children="ציון תקיפות גוף",
                                                   style={'color': 'black'},
                                                   ),
                                            dcc.Slider(id="Weight 8", min=1, max=5, value=1, step=None,
                                                       marks={
                                                           str(num): {"label": str(num),
                                                                      "style": {"color": "#7fafdf"}, }
                                                           for num in [1, 2, 3, 4, 5]
                                                       }),
                                            ], className="slider-container"),
                                  html.Div([html.P(id="slider-text9", children="ציון תקיפות מיניות",
                                                   style={'color': 'black'},
                                                   ),
                                            dcc.Slider(id="Weight 9", min=1, max=5, value=1, step=None,
                                                       marks={
                                                           str(num): {"label": str(num),
                                                                      "style": {"color": "#7fafdf"}, }
                                                           for num in [1, 2, 3, 4, 5]
                                                       }),
                                            html.P(id="slider-text10", children="ציון שודים",
                                                   style={'color': 'black'},
                                                   ),
                                            dcc.Slider(id="Weight 10", min=1, max=5, value=1, step=None,
                                                       marks={
                                                           str(num): {"label": str(num),
                                                                      "style": {"color": "#7fafdf"}, }
                                                           for num in [1, 2, 3, 4, 5]
                                                       }),
                                            html.P(id="slider-text11", children="ציון הכנסה ממוצעת",
                                                   style={'color': 'black'},
                                                   ),
                                            dcc.Slider(id="Weight 11", min=1, max=5, value=1, step=None,
                                                       marks={
                                                           str(num): {"label": str(num),
                                                                      "style": {"color": "#7fafdf"}, }
                                                           for num in [1, 2, 3, 4, 5]
                                                       }),
                                            html.P(id="slider-text12", children="ציון צפיפות דמוגרפית",
                                                   style={'color': 'black'},
                                                   ),
                                            dcc.Slider(id="Weight 12", min=1, max=5, value=1, step=None,
                                                       marks={
                                                           str(num): {"label": str(num),
                                                                      "style": {"color": "#7fafdf"}, }
                                                           for num in [1, 2, 3, 4, 5]
                                                       }), ], className="slider-container"),
                                  ]),
                    id=f"collapse-1",
                    is_open=False,
                ),
            ]
        ), className='accordion'), ], className='pretty_container'),
    html.Div(children=[
        html.Div([
            html.Div(
                children=[
                    html.Div(
                        id="graph-container",
                        children=[
                            dcc.Graph(id='graph_with_slider')
                        ], className='map_container_safety'),

                ],
                className="row_rapper")
        ], className="pretty_container"),
        html.Div([
            html.Div([
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
                    [
                        dcc.Graph(id='score_graph')
                    ],
                    className='map_container', )
            ], id="info-container1",
                className="row container-display")], className='pretty_container')
    ], )
], )


@app.callback(
    Output(component_id='graph_with_slider', component_property='figure'),
    Output(component_id='score_graph', component_property='figure'),
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
    W = [float(i) / sum(W) for i in W]

    for idx, row in df_score_t1.iterrows():
        tmp_score = sum(np.multiply(list(row[:-1]), W))
        values_dict_t1[row.StatZone] = int(tmp_score * 100)

    for idx, row in df_score_t0.iterrows():
        tmp_score = sum(np.multiply(list(row[:-1]), W))
        values_dict_t0[row.StatZone] = int(tmp_score * 100)
    scores_dict = [values_dict_t0, values_dict_t1]
    fig1 = get_choroplethmap_fig(values_dict=values_dict_t1, map_title="Stat Zone Safety Score", is_safety_map=True, scores_dicts=scores_dict)
    fig1.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    if area in [0, '0']:
        area = 'All Statistical zones'
    if area == 'All Statistical zones':
        score_area_val = list(df_score_t1.drop("StatZone", axis=1).mean())
        title2 = "Component scores for All Statistical zones "
    else:
        score_area_val = df_score_t1[df_score_t1['StatZone'] == int(area)].drop('StatZone', axis=1).values[0]
        title2 = f"Component scores for stat zone {area}"
    score_area_val = [i * 100 for i in score_area_val]

    y_label = ['ציון קונפליקטים בין שכנים', 'ציון מצלמות אבטחה', 'ציון בתים נטושים',
               'ציון שיחות למוקד העירייה בנושא ביטחון', 'ציון שיחות למוקד העירייה בנושא סוציאלי', 'ציון פשיעה',
               'ציון גניבות', 'ציון תקיפות גוף', 'ציון תקיפות מיניות', 'ציון שודים', 'ציון הכנסה ממוצעת ',
               'ציון צפיפות דמוגרפית']
    y_label = [s[::-1] for s in y_label]
    fig2_df = pd.DataFrame(columns=['Score', 'Score component'])
    fig2_df['Score'] = score_area_val
    fig2_df['Score component'] = y_label
    fig2_df = fig2_df.sort_values(by='Score', ascending='False')
    fig2 = px.bar(fig2_df, x=fig2_df.Score, y=fig2_df['Score component'], color_discrete_sequence=['#252E3F'])
    fig2.update_layout(title_text=title2, barmode='stack', yaxis={'categoryorder': 'total descending'})

    return fig1, fig2


@app.callback(
    [Output(f"collapse-1", "is_open")],
    [Input(f"group-1-toggle", "n_clicks")],
    [State(f"collapse-1", "is_open")],
)
def toggle_accordion(n1, is_open1):
    ctx = dash.callback_context

    if not ctx.triggered:
        return [False]
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "group-1-toggle" and n1:
        return [not is_open1]
    return [False]

# if __name__ == '__main__':
# score_area_val = list(df_scores.mean())
# area=611
# score_area_val = list(df_scores[df_scores['StatZone'] == area].drop("StatZone", axis=1).values[0])
# X_label = ["Neighbors' Conflicts", "Security Cameras", 'Abandoned houses',
#            'Calls to 106 - Security', 'Calls to 106 - Social', 'Crime', 'Thefts',
#            'BodyAssaults','SexualAssaults','Robbery', 'Average Income', 'Demographic density']
# fig2 = px.bar(x=X_label, y=score_area_val, title=f"Component scores for stat zone {area}")
# fig2.show()
# a = 1
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
