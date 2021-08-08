from app_def import app
from choroplethmapbox import get_choroplethmap_fig
from pre_process import *
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from utils import create_horizontal_bar_plot_with_annotations, options_map, stat_zones_names_dict, options


sal0, sal1 = dfs_dict['df_salaries_t0'], dfs_dict['df_salaries_t1']
for df in [sal0, sal1]:
    df['SalNoHKResNum_avg'] = df['SalNoHKResNum'] * df['SalNoHKAve']
    df['SalHKResNum_avg'] = df['SalHKResNum'] * df['SalHKAve']
    df['SalPenResNum_avg'] = df['SalPenResNum'] * df['SalPenAve']
    df['SalSHNoBTLResNum_avg'] = df['SalSHNoBTLResNum'] * df['SalSHNoBTLAve']
    df['IncSelfResNum_avg'] = df['IncSelfResNum'] * df['IncSelfAve']
    df['tot_res'] = df[[col for col in
                        ['SalNoHKResNum', 'SalHKResNum', 'SalPenResNum', 'SalSHNoBTLResNum',
                         'IncSelfResNum']]].sum(axis=1)
    df['total_sal_avg'] = df[[col for col in
                              ['SalNoHKResNum_avg', 'SalHKResNum_avg', 'SalPenResNum_avg', 'SalSHNoBTLResNum_avg',
                               'IncSelfResNum_avg']]].sum(axis=1) / df['tot_res']


@app.callback(
    Output(component_id='Avg_salary', component_property='figure'),
    Output(component_id='Amount_of_workers', component_property='figure'),
    Input(component_id='areas', component_property='value')
)
def get_graphs(statzone):
    df_salary1 = dfs_dict['df_salaries_t1']
    df_salary1, df_avg_sal1 = manipulate_df_salary_fig1(df_salary1, statzone)
    df_salary0 = dfs_dict['df_salaries_t0']
    df_salary0, df_avg_sal0 = manipulate_df_salary_fig1(df_salary0, statzone)

    if statzone == 0:
        title1 = "משכורת ממוצעת עבור כל סוגי המשכורות בכל שכונת הדר"[::-1]
        title2 = "כמות העובדים עבור כל סוגי המשכורות בכל שכונת הדר"[::-1]
    else:
        statzone_name = str(statzone)
        title1 = f"משכורת ממוצעת עבור כל סוגי המשכורות באזור סטטיסטי {statzone_name[::-1]}"[::-1]
        title2 = f"כמות העובדים עבור כל סוגי המשכורות באזור סטטיסטי {statzone_name[::-1]}"[::-1]

    percentage_change = 100 * (df_avg_sal1['Average salary'] - df_avg_sal0['Average salary']) / df_avg_sal0[
        'Average salary']
    max_y = max(df_avg_sal1['Average salary'])

    fig1 = create_horizontal_bar_plot_with_annotations(numeric_vals=df_avg_sal1['Average salary'],  # x
                                                       old_numeric_vals=df_avg_sal0['Average salary'],  # old x
                                                       category_vals=df_avg_sal1['Salary type'],  # y
                                                       percentage_change_value=percentage_change,
                                                       # pay attention to order
                                                       title_text=title1, text_offset_to_the_right=0.15 * max_y,
                                                       tickfont_size=18,
                                                       annotations_text_size=18,
                                                       is_safety=False)
    fig1.update_layout(xaxis_range=[0, max_y * 1.15], title_x=0.5, titlefont_size=18)

    df_amount_of_workers1 = manipulate_df_salary_fig2(df_salary1)
    df_amount_of_workers0 = manipulate_df_salary_fig2(df_salary0)

    percentage_change = 100 * (
            df_amount_of_workers1['Amount of workers'] - df_amount_of_workers0['Amount of workers']) / \
                        df_amount_of_workers0['Amount of workers']
    max_y = max(df_amount_of_workers1['Amount of workers'])

    fig2 = create_horizontal_bar_plot_with_annotations(numeric_vals=df_amount_of_workers1['Amount of workers'],  # x
                                                       old_numeric_vals=df_amount_of_workers0['Amount of workers'],
                                                       # old x
                                                       category_vals=df_amount_of_workers1['Salary type'],  # y
                                                       percentage_change_value=percentage_change,
                                                       # pay attention to order
                                                       title_text=title2, text_offset_to_the_right=0.15 * max_y,
                                                       is_safety=False)

    fig2.update_layout(xaxis_range=[0, max_y * 1.15], title_x=0.5, titlefont_size=18)
    return fig1, fig2


@app.callback(
    Output(component_id='primary_map_income', component_property='figure'),
    Input(component_id='map_definition', component_property='value')
)
def change_map(map_def):
    if map_def == 0:  # 'שינוי באחוזים מהדו"ח הקודם'
        percentage_change = 100 * (sal1.total_sal_avg - sal0.total_sal_avg) / sal0.total_sal_avg
        values_for_heatmap = {statzone_code: perc_change for statzone_code, perc_change in
                              zip(stat_zones_names_dict.keys(), percentage_change)}
        map_fig = get_choroplethmap_fig(values_dict={k: int(v) for k, v in values_for_heatmap.items()},
                                        map_title="% of change in total crime cases",
                                        colorscale=[[0, '#561162'], [0.5, 'white'], [1, '#0B3B70']],
                                        hovertemplate='<b>StatZone</b>: %{text}' + '<br><b>Percentage of change</b>: %{customdata}%<br>')
        map_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return map_fig
    else:  # 'הצג ערך נוכחי'
        values_for_heatmap = {statzone_code: perc_change for statzone_code, perc_change in
                              zip(stat_zones_names_dict.keys(), sal1.total_sal_avg)}
        map_fig = get_choroplethmap_fig(values_dict={k: int(v) for k, v in values_for_heatmap.items()},
                                        map_title="Current values in total crime cases",
                                        colorscale=[[0, '#561162'], [0.5, 'white'], [1, '#0B3B70']],
                                        hovertemplate='<b>StatZone</b>: %{text}' + '<br><b>Current Value</b>: %{customdata}<br>',
                                        changes_map=False)
        map_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return map_fig


def manipulate_df_salary_fig1(df_salary, statzone):
    df_salary['SalNoHKResNum_avg'] = df_salary['SalNoHKResNum'] * df_salary['SalNoHKAve']
    df_salary['SalHKResNum_avg'] = df_salary['SalHKResNum'] * df_salary['SalHKAve']
    df_salary['SalPenResNum_avg'] = df_salary['SalPenResNum'] * df_salary['SalPenAve']
    df_salary['SalSHNoBTLResNum_avg'] = df_salary['SalSHNoBTLResNum'] * df_salary['SalSHNoBTLAve']
    df_salary['IncSelfResNum_avg'] = df_salary['IncSelfResNum'] * df_salary['IncSelfAve']
    # fig 1
    df_avg_sal = pd.DataFrame(columns=['Salary type', 'Average salary'])
    df_avg_sal['Salary type'] = ['שכר כולל מעבודה (לא כולל עבודה במשק בית(', 'שכר כולל מעבודה במשק בית',
                                 'שכר כולל מפנסיה',
                                 'שכר כולל מקצבת שארים (שלא מהביטוח הלאומי(', 'הכנסה מעבודה עצמאית']
    df_avg_sal['Salary type'] = [s[::-1].strip(' ') for s in df_avg_sal['Salary type']]

    if statzone == 0:
        df_avg_sal['Average salary'] = [df_salary['SalNoHKResNum_avg'].sum() / df_salary['SalNoHKResNum'].sum(),
                                        df_salary['SalHKResNum_avg'].sum() / df_salary['SalHKResNum'].sum(),
                                        df_salary['SalPenResNum_avg'].sum() / df_salary['SalPenResNum'].sum(),
                                        df_salary['SalSHNoBTLResNum_avg'].sum() / df_salary['SalSHNoBTLResNum'].sum(),
                                        df_salary['IncSelfResNum_avg'].sum() / df_salary['IncSelfResNum'].sum()]
    else:
        df_salary = df_salary[df_salary['StatZone'] == statzone]
        df_avg_sal['Average salary'] = [df_salary['SalNoHKAve'].sum(), df_salary['SalHKAve'].sum(),
                                        df_salary['SalPenAve'].sum(), df_salary['SalSHNoBTLAve'].sum(),
                                        df_salary['IncSelfAve'].sum()]
    return df_salary, df_avg_sal


def manipulate_df_salary_fig2(df_salary):
    df_amount_of_workers = pd.DataFrame(columns=['Salary type', 'Amount of workers'])
    df_amount_of_workers['Salary type'] = ['שכר כולל מעבודה (לא כולל עבודה במשק בית(', 'שכר כולל מעבודה במשק בית',
                                           'שכר כולל מפנסיה',
                                           'שכר כולל מקצבת שארים (שלא מהביטוח הלאומי(', 'הכנסה מעבודה עצמאית']
    df_amount_of_workers['Salary type'] = [s[::-1].strip(' ') for s in df_amount_of_workers['Salary type']]
    df_amount_of_workers['Amount of workers'] = [df_salary['SalNoHKResNum'].sum(), df_salary['SalHKResNum'].sum(),
                                                 df_salary['SalPenResNum'].sum(), df_salary['SalSHNoBTLResNum'].sum(),
                                                 df_salary['IncSelfResNum'].sum()]
    return df_amount_of_workers


layout = html.Div(children=[html.H4(
    children=[html.H4(['.בעמוד הנוכחי תוכלו לראות מגוון נתונים בנושא ההכנסה של האוכלוסיה בהדר'],
                      style={'text-align': 'right', 'text-transform': 'none', 'font-family': 'sans-serif',
                             'letter-spacing': '0em'}, ),
              html.H4([
                  'ניתן לבחור ולראות מפה המציגה את הערכים הנוכחיים של ההכנסה הממוצעת בכל אזור סטטיסטי, וכן מפה המראה את השינויים מהחצי שנה הקודמת. בהמשך מוצגים גרפים אשר מציגים מידע נוסף על ההכנסה, וניתן לבחור להציג בהם מידע רק על אזור סטטיסטי מסוים. מוצגים 2 גרפים המציגים את כמות העובדים והשכר הממוצע עבור מגוון סוגי הכנסות. הגרפים מציגים את המצב הנוכחי ומוצג בהם השינוי בין התקופות השונות. (במעבר על הגרפים ניתן לראות את הערכים עצמם ואת השינוי בהם)']
                  , style={'text-align': 'right', 'text-transform': 'none', 'font-family': 'sans-serif',
                           'letter-spacing': '0em', 'line-height': '1.6em'}
              )]
    ,
    className='pretty_container'
),
    html.Div([
        html.Div([html.H6('בחר את תצוגת המפה',
                          style={'Font-weight': 'bold', 'text-transform': 'none',
                                 'letter-spacing': '0em', 'font-family': 'sans-serif',
                                 'font-size': 20}),
                  dcc.RadioItems(id='map_definition',
                                 options=options_map,
                                 value=0,
                                 labelStyle={'display': 'block'},
                                 inputStyle={'textAlign': 'right'}

                                 ), ], style={'textAlign': 'center', 'font-size': 17,
                                              'font-family': 'sans-serif',
                                              'letter-spacing': '0em'}),
        html.Div(
            [
                html.Div(
                    [
                        ':בחר אזור סטטיסטי', dcc.RadioItems(id='areas',
                                                            options=options,
                                                            value=0
                                                            ),
                    ],
                    className="mini_container",
                ),
                html.Div([
                    dcc.Graph(id='primary_map_income')
                ], className="map_container"),
            ],
            className="row_rapper",
        ), ], className="pretty_container"),
    html.Div(
        [
            html.Div(
                [
                    dcc.Graph(id='Avg_salary')
                ],
                className='pretty_container',
            ),
            html.Div(
                [
                    dcc.Graph(id='Amount_of_workers')
                ],
                className='pretty_container',
            ),
        ], )
]

)
