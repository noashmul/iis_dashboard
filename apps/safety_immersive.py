import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app_def import app
from choroplethmapbox import get_choroplethmap_fig
import dash_bootstrap_components as dbc
from dash.dependencies import State
from choroplethmapbox import get_area_in_km2_for_stat_zones
from pre_process import *
from utils import *
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
    Demographic_density_s = 1 - Demographic_density_area / Demographic_density_haifa

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
        '`ציון הביטחון האישי הוא קומבינציה של 12 רכיבים שונות המציגים הביטים שונים של ביטחון אישי. אנא בחר את החשיבות של כל רכיב בהתאם להעדפותיך בכרטיסיית `משקולות ביטחון ',
        style={'text-align': 'right', 'text-transform': 'none', 'font-family': 'sans-serif',
               'letter-spacing': '0em'}, ),
        html.H4(
            'לפניכם מוצגת מפת חום של ציוני ביטחון אישי באזורים הסטטיסטיים',
            style={'text-align': 'right', 'text-transform': 'none', 'font-family': 'sans-serif',
                   'letter-spacing': '0em'}, )
    ],
        className='pretty_container'
    ),
    html.Div(children=[
        html.Div([
            html.Div(
                children=
                [
                    html.Div(
                        id="graph-container",
                        children=[
                            dcc.Graph(id='graph_with_slider_immersive')
                        ], className='map_container_safety'),

                ],
            )
        ], className="narrow_container"),
        html.Div([
            html.Div([
                html.Div(
                    [
                        ':בחר אזור סטטיסטי', dcc.RadioItems(id='areas',
                                                            options=options,
                                                            value=0
                                                            ),
                    ],
                    className="mini_container",
                ),

                html.Div(
                    [
                        dcc.Graph(id='score_graph_immersive')
                    ],
                    className='map_container', )
            ], className='row_rapper'),
        ], className='narrow_container')
    ])
], )


@app.callback(
    Output(component_id='graph_with_slider_immersive', component_property='figure'),
    Output(component_id='score_graph_immersive', component_property='figure'),
    Input(component_id='areas', component_property='value'),
    Input('interval-component', 'n_intervals')
)
def update_output_div(area, n_interval):
    weights = open("weights.pkl", 'rb')
    W = pickle.load(weights)
    weights.close()
    for idx, row in df_score_t1.iterrows():
        tmp_score = sum(np.multiply(list(row[:-1]), W))
        values_dict_t1[row.StatZone] = int(tmp_score * 100)

    for idx, row in df_score_t0.iterrows():
        tmp_score = sum(np.multiply(list(row[:-1]), W))
        values_dict_t0[row.StatZone] = int(tmp_score * 100)
    scores_dict = [values_dict_t0, values_dict_t1]
    fig1 = get_choroplethmap_fig(values_dict=values_dict_t1, map_title="Stat Zone Safety Score", is_safety_map=True,
                                 scores_dicts=scores_dict)
    fig1.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    if area in [0, '0']:
        area = 'All Statistical zones'
    if area == 'All Statistical zones':
        score_area_val_t1 = list(df_score_t1.drop("StatZone", axis=1).mean())
        score_area_val_t0 = list(df_score_t0.drop("StatZone", axis=1).mean())
        title2 = "פירוט ציונים עבור אספקטים שונים של ביטחון אישי בשכונת הדר"[::-1]
    else:
        score_area_val_t1 = df_score_t1[df_score_t1['StatZone'] == int(area)].drop('StatZone', axis=1).values[0]
        score_area_val_t0 = df_score_t0[df_score_t0['StatZone'] == int(area)].drop('StatZone', axis=1).values[0]
        title2 = f'מרכיבי הציון עבור אזור סטטיסטי {str(area)[::-1]}'[::-1]
    score_area_val_t1 = [i * 100 for i in score_area_val_t1]
    score_area_val_t0 = [i * 100 for i in score_area_val_t0]

    y_label = ['קונפליקטים בין שכנים', 'מצלמות אבטחה', 'בתים נטושים',
               'שיחות למוקד העירייה בנושא ביטחון', 'שיחות למוקד העירייה בנושא סוציאלי', 'פשיעה',
               'גניבות', 'תקיפות גוף', 'תקיפות מיניות', 'שודים', 'הכנסה ממוצעת ',
               'צפיפות דמוגרפית']
    y_label_data = ['הציון מעיד על כמות קונפליקטים בין שכנים באזור, מעט קונפליקטים יגררו ציון גבוה יותר',
                    'הציון מסביר עד כמה האזור מכיל מצלמות אבטחה, ציון גבוה מעיד על הרבה מצלמות',
                    'הציון מעיד על עד כמה האזור מכיל בתים נטושים, ציון גבוה מעיד על מעט בתים נטושים',
                    'הציון מעיד על כמות פניות למוקד העירייה בנושא ביטחון, ציון גבוה מעיד על מעט פניות',
                    'הציון מעיד על כמות פניות למוקד העירייה בנושא סוציאלי, ציון גבוה מעיד על מעט פניות',
                    'הציון מעיד על כמות הפשיעה הכללית באזור, ציון גבוה מעיד על מעט פשיעה',
                    'הציון מעיד על כמות הגניבות באזור, ציון גבוה מעיד על פחות גניבות',
                    'הציון מעיד על כמות תקיפות הגוף באזור, ציון גבוה מעיד על פחות תקיפות גוף',
                    'הציון מעיד על כמות תקיפות מיניות באזור, ציון גבוה מעיד על פחות תקיפות מיניות',
                    'הציון מעיד על כמות שודים באזור, כאשר ציון גבוה מעיד על פחות שודים',
                    'הציון מעיד על ההכנסה הממוצעת של התושבים באזור, ציון גבוה מעיד על הכנסה ממוצעת גבוהה יותר',
                    'הציון מעיד על צפיפות התושבים באזור, ציון גבוה יותר מעיד על צפיפות נמוכה יותר']
    y_label_data = [item[::-1] for item in y_label_data]
    y_label = [s[::-1] for s in y_label]
    fig2_df = pd.DataFrame(columns=['Score', 'Score component'])
    fig2_df['Score_t1'] = score_area_val_t1
    fig2_df['Score_t0'] = score_area_val_t0
    fig2_df['Score component'] = y_label
    fig2_df['diff'] = 100 * (fig2_df['Score_t1'] - fig2_df['Score_t0']) / fig2_df['Score_t0']
    fig2_df['diff'].replace([np.inf, -np.inf], 0, inplace=True)
    fig2_df['diff'].replace([np.nan], 0, inplace=True)
    fig2_df['data'] = y_label_data

    fig2_df = fig2_df.sort_values(by='Score_t1', ascending='False')
    max_y = max(fig2_df['Score_t1'])
    fig2 = create_horizontal_bar_plot_with_annotations(numeric_vals=fig2_df['Score_t1'],
                                                       old_numeric_vals=fig2_df['Score_t0'],
                                                       category_vals=fig2_df['Score component'],
                                                       percentage_change_value=fig2_df['diff'],
                                                       title_text=title2, text_offset_to_the_right=0.2 * max_y,
                                                       tickfont_size=12, annotations_text_size=14,
                                                       is_safety=True, y_label_data=fig2_df['data'])
    return fig1, fig2


@app.callback(
    [Output(f"collapse-1_immersive", "is_open")],
    [Input(f"group-1-toggle", "n_clicks")],
    [State(f"collapse-1_immersive", "is_open")],
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
