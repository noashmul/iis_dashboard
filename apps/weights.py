import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app_def import app
import dash_bootstrap_components as dbc
from dash.dependencies import State
from choroplethmapbox import get_area_in_km2_for_stat_zones
from pre_process import *
import pickle

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

### choose initial score for each weight
scores = [3] * 12


def calc_safety_scores(StatZone, df_salary, df_conflicts, df_cameras, df_aband, df_106,
                       df_crimes):
    df_area_salary = df_salary[df_salary['StatZone'] == StatZone]
    df_area_cameras = df_cameras[df_cameras['StatZone'] == StatZone]
    df_ares_aband = df_aband[df_aband['StatZone'] == StatZone]
    df_area_106_security = df_106[(df_106['StatZone'] == StatZone) &
                                  (df_106['בעל המשימה'] == 'בטחון')]
    df_area_106_social = df_106[(df_106['StatZone'] == StatZone) &
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

layout = html.Div(children=[
    html.Div([html.H4(
        'ציון הביטחון האישי הוא קומבינציה של 12 רכיבים שונות המציגים הביטים שונים של ביטחון אישי. אנא בחר את החשיבות של כל רכיב בהתאם להעדפותיך '
        ,
        style={'text-align': 'right', 'text-transform': 'none', 'font-family': 'sans-serif',
               'letter-spacing': '0em'}, )],
        className='pretty_container'
    ),

    html.Div([html.Div([
        html.Div([html.Div([
            dbc.Button('אפס חשיבות רכיבים', id='reset_weights_weights', n_clicks=0, color='dark',
                       style={'text-align': 'right', 'text-transform': 'none', 'font-family': 'sans-serif',
                              'letter-spacing': '0em', 'font-size': 15}
                       ),
            html.H4("5: רמת חשיבות נמוכה :1, רמת חשיבות גבוהה", style={'text-align': 'right', 'text-transform': 'none',
                                                                       'font-family': 'sans-serif',
                                                                       'letter-spacing': '0em', 'font-size': 15,
                                                                       'font-weight': 'bold'}),
        ], className='row_rapper'), ], className='pretty_container'),
        html.Div([html.P(id="slider-text1", children="קונפליקטים בין שכנים",
                         style={'color': 'black', 'text-align': 'center'},
                         ),
                  dcc.Slider(id="Weight 1_weights", min=1, max=5, value=scores[0], step=None,
                             marks={
                                 str(num): {"label": str(num),
                                            "style": {"color": "#7fafdf"}, }
                                 for num in [1, 2, 3, 4, 5]
                             }),
                  html.P(id="slider-text2", children="מצלמות אבטחה",
                         style={'color': 'black', 'text-align': 'center'},
                         ),
                  dcc.Slider(id="Weight 2_weights", min=1, max=5, value=scores[1], step=None,
                             marks={
                                 str(num): {"label": str(num),
                                            "style": {"color": "#7fafdf"}, }
                                 for num in [1, 2, 3, 4, 5]
                             }),
                  html.P(id="slider-text3", children="בתים נטושים",
                         style={'color': 'black', 'text-align': 'center'},
                         ),
                  dcc.Slider(id="Weight 3_weights", min=1, max=5, value=scores[2], step=None,
                             marks={
                                 str(num): {"label": str(num),
                                            "style": {"color": "#7fafdf"}, }
                                 for num in [1, 2, 3, 4, 5]
                             }),
                  html.P(id="slider-text4", children="שיחות למוקד העירייה בנושא ביטחון",
                         style={'color': 'black', 'text-align': 'center'},
                         ),
                  dcc.Slider(id="Weight 4_weights", min=1, max=5, value=scores[3], step=None,
                             marks={
                                 str(num): {"label": str(num),
                                            "style": {"color": "#7fafdf"}, }
                                 for num in [1, 2, 3, 4, 5]
                             }),
                  ], className="slider-container"),
        html.Div([html.P(id="slider-text5", children="שיחות למוקד העירייה בנושא סוציאלי",
                         style={'color': 'black', 'text-align': 'center'},
                         ),
                  dcc.Slider(id="Weight 5_weights", min=1, max=5, value=scores[4], step=None,
                             marks={
                                 str(num): {"label": str(num),
                                            "style": {"color": "#7fafdf"}, }
                                 for num in [1, 2, 3, 4, 5]
                             }),
                  html.P(id="slider-text6", children="פשיעה",
                         style={'color': 'black', 'text-align': 'center'},
                         ),
                  dcc.Slider(id="Weight 6_weights", min=1, max=5, value=scores[5], step=None,
                             marks={
                                 str(num): {"label": str(num),
                                            "style": {"color": "#7fafdf"}, }
                                 for num in [1, 2, 3, 4, 5]
                             }),
                  html.P(id="slider-text7", children="גניבות",
                         style={'color': 'black', 'text-align': 'center'},
                         ),
                  dcc.Slider(id="Weight 7_weights", min=1, max=5, value=scores[6], step=None,
                             marks={
                                 str(num): {"label": str(num),
                                            "style": {"color": "#7fafdf"}, }
                                 for num in [1, 2, 3, 4, 5]
                             }),
                  html.P(id="slider-text8", children="תקיפות גוף",
                         style={'color': 'black', 'text-align': 'center'},
                         ),
                  dcc.Slider(id="Weight 8_weights", min=1, max=5, value=scores[7], step=None,
                             marks={
                                 str(num): {"label": str(num),
                                            "style": {"color": "#7fafdf"}, }
                                 for num in [1, 2, 3, 4, 5]
                             }),
                  ], className="slider-container"),
        html.Div([html.P(id="slider-text9", children="תקיפות מיניות",
                         style={'color': 'black', 'text-align': 'center'},
                         ),
                  dcc.Slider(id="Weight 9_weights", min=1, max=5, value=scores[8], step=None,
                             marks={
                                 str(num): {"label": str(num),
                                            "style": {"color": "#7fafdf"}, }
                                 for num in [1, 2, 3, 4, 5]
                             }),
                  html.P(id="slider-text10", children="שודים",
                         style={'color': 'black', 'text-align': 'center'},
                         ),
                  dcc.Slider(id="Weight 10_weights", min=1, max=5, value=scores[9], step=None,
                             marks={
                                 str(num): {"label": str(num),
                                            "style": {"color": "#7fafdf"}, }
                                 for num in [1, 2, 3, 4, 5]
                             }),
                  html.P(id="slider-text11", children="הכנסה ממוצעת",
                         style={'color': 'black', 'text-align': 'center'},
                         ),
                  dcc.Slider(id="Weight 11_weights", min=1, max=5, value=scores[10],
                             step=None,
                             marks={
                                 str(num): {"label": str(num),
                                            "style": {"color": "#7fafdf"}, }
                                 for num in [1, 2, 3, 4, 5]
                             }),
                  html.P(id="slider-text12", children="צפיפות דמוגרפית",
                         style={'color': 'black', 'text-align': 'center'},
                         ),
                  dcc.Slider(id="Weight 12_weights", min=1, max=5, value=scores[11],
                             step=None,
                             marks={
                                 str(num): {"label": str(num),
                                            "style": {"color": "#7fafdf"}, }
                                 for num in [1, 2, 3, 4, 5]
                             }), ], className="slider-container")],
    )]),
    html.Div(id='fake_output')]
)


@app.callback(
    Output(component_id='fake_output', component_property='value'),
    Input(component_id='Weight 1_weights', component_property='value'),
    Input(component_id='Weight 2_weights', component_property='value'),
    Input(component_id='Weight 3_weights', component_property='value'),
    Input(component_id='Weight 4_weights', component_property='value'),
    Input(component_id='Weight 5_weights', component_property='value'),
    Input(component_id='Weight 6_weights', component_property='value'),
    Input(component_id='Weight 7_weights', component_property='value'),
    Input(component_id='Weight 8_weights', component_property='value'),
    Input(component_id='Weight 9_weights', component_property='value'),
    Input(component_id='Weight 10_weights', component_property='value'),
    Input(component_id='Weight 11_weights', component_property='value'),
    Input(component_id='Weight 12_weights', component_property='value'),
)
def update_output_div(w1, w2, w3, w4, w5, w6, w7, w8, w9, w10, w11, w12):
    """
    create all the graphs that rely on the input values (weights and area)
    :param w1: weight value
    :param w2: weight value
    :param area: statistic ares (or 'All')
    :return: all wanted figures
    """
    W = [w1, w2, w3, w4, w5, w6, w7, w8, w9, w10, w11, w12]
    W = [float(i) / sum(W) for i in W]

    # Save weights locally by user choice
    weights = open("weights.pkl", "wb")
    pickle.dump(W, weights)
    weights.close()

    return 0


@app.callback(
    [Output(f"collapse-1_weights", "is_open")],
    [Input(f"group-1-toggle", "n_clicks")],
    [State(f"collapse-1_weights", "is_open")],
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


@app.callback(
    Output(component_id='Weight 1_weights', component_property='value'),
    Output(component_id='Weight 2_weights', component_property='value'),
    Output(component_id='Weight 3_weights', component_property='value'),
    Output(component_id='Weight 4_weights', component_property='value'),
    Output(component_id='Weight 5_weights', component_property='value'),
    Output(component_id='Weight 6_weights', component_property='value'),
    Output(component_id='Weight 7_weights', component_property='value'),
    Output(component_id='Weight 8_weights', component_property='value'),
    Output(component_id='Weight 9_weights', component_property='value'),
    Output(component_id='Weight 10_weights', component_property='value'),
    Output(component_id='Weight 11_weights', component_property='value'),
    Output(component_id='Weight 12_weights', component_property='value'),
    Input(component_id='reset_weights_weights', component_property='n_clicks'),
)
def reset_all_weights(n1):
    ctx = dash.callback_context
    if not ctx.triggered:
        return scores
    else:
        return scores
