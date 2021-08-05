from app_def import app
from choroplethmapbox import get_choroplethmap_fig
from pre_process import *
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

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

stat_zones_names_dict = {
    611: "הדר מערב - רח' אלמותנבי",
    612: 'גן הבהאים',
    613: "הדר מערב - רח' מסדה",
    621: 'הדר עליון -בי"ח בני ציון',
    622: "הדר עליון - רח' הפועל",
    623: "רמת הדר - רח' המיימוני",
    631: 'הדר מרכז - התיאטרון העירוני',
    632: "הדר מרכז - רח' הרצליה",
    633: 'הדר מרכז - בית העירייה',
    634: 'הדר מרכז - שוק תלפיות',
    641: 'הדר מזרח - רח\' יל"ג',
    642: 'הדר מזרח - גאולה',
    643: "רמת ויז'ניץ",
    644: 'מעונות גאולה'
}

options_map = [{'label': ' הצג מפת שינויים ', 'value': 0}, {'label': ' הצג ערכים נוכחיים', 'value': 1}]

options = list()
for key, value in statistic_area.items():
    if key != 'הכל':
        options.append({'label': "  " + key + ' ' + str(value),
                        'value': value})
    else:
        options.append({'label': "  " + key,
                        'value': value})

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
    df_salary = dfs_dict['df_salaries_t1']
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
        statzone = 'All Statistical zones'
        # df_salary = df_salary[['SalNoHKResNum', 'SalHKResNum', 'SalPenResNum', 'SalSHNoBTLResNum', 'IncSelfResNum',
        #                        'SalNoHKAve', 'SalHKAve', 'SalPenAve', 'SalSHNoBTLAve', 'IncSelfAve']]
        df_avg_sal['Average salary'] = [df_salary['SalNoHKResNum_avg'].sum() / df_salary['SalNoHKResNum'].sum(),
                                        df_salary['SalHKResNum_avg'].sum() / df_salary['SalHKResNum'].sum(),
                                        df_salary['SalPenResNum_avg'].sum() / df_salary['SalPenResNum'].sum(),
                                        df_salary['SalSHNoBTLResNum_avg'].sum() / df_salary['SalSHNoBTLResNum'].sum(),
                                        df_salary['IncSelfResNum_avg'].sum() / df_salary['IncSelfResNum'].sum()]
        title1 = "Average Salary per Salary type in All Statistical zones"
        title2 = "Amount of workers per Salary type in All Statistical zones"
    else:
        df_salary = df_salary[df_salary['StatZone'] == statzone]
        df_avg_sal['Average salary'] = [df_salary['SalNoHKAve'].sum(), df_salary['SalHKAve'].sum(),
                                        df_salary['SalPenAve'].sum(), df_salary['SalSHNoBTLAve'].sum(),
                                        df_salary['IncSelfAve'].sum()]
        title1 = f"Average Salary per Salary type in {statzone} stat zone"
        title2 = f"Amount of workers per Salary type in {statzone} stat zone"

    fig1 = px.bar(df_avg_sal, y=df_avg_sal['Salary type'],
                  x=df_avg_sal['Average salary'], orientation='h',
                  color_discrete_sequence=['#252E3F'])
    fig1.update_layout(title_text=title1,
                       yaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ),
                       xaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ), xaxis_showgrid=True, yaxis_showgrid=True,
                       template='simple_white',
                       )
    fig1.update_xaxes(tickangle=45)

    df_amount_of_workers = pd.DataFrame(columns=['Salary type', 'Amount of workers'])
    df_amount_of_workers['Salary type'] = ['שכר כולל מעבודה (לא כולל עבודה במשק בית(', 'שכר כולל מעבודה במשק בית',
                                           'שכר כולל מפנסיה',
                                           'שכר כולל מקצבת שארים (שלא מהביטוח הלאומי(', 'הכנסה מעבודה עצמאית']
    df_amount_of_workers['Salary type'] = [s[::-1].strip(' ') for s in df_amount_of_workers['Salary type']]
    df_amount_of_workers['Amount of workers'] = [df_salary['SalNoHKResNum'].sum(), df_salary['SalHKResNum'].sum(),
                                                 df_salary['SalPenResNum'].sum(), df_salary['SalSHNoBTLResNum'].sum(),
                                                 df_salary['IncSelfResNum'].sum()]
    fig2 = px.bar(df_amount_of_workers, y=df_amount_of_workers['Salary type'],
                  x=df_amount_of_workers['Amount of workers'], orientation='h',
                  color_discrete_sequence=['#252E3F'])
    fig2.update_layout(title_text=title2,
                       yaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ),
                       xaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ), xaxis_showgrid=True, yaxis_showgrid=True,
                       template='simple_white',
                       )
    fig2.update_xaxes(tickangle=45)

    return fig1, fig2


@app.callback(
    Output(component_id='primary_map_income', component_property='figure'),
    Input(component_id='map_definition', component_property='value')
)
def change_map(map_def):
    if map_def == 0:  # 'הצג מפת שינויים'
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


layout = html.Div(children=[html.H4(children='Choose the wanted area to see the graphs changes',
                                    style={'text-align': 'left', 'text-transform': 'none', 'font-family': 'sans-serif',
                                           'letter-spacing': '0em'}, className="pretty_container"
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
                                                'Choose area: ', dcc.RadioItems(id='areas',
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
                                    # id="info-container1",
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
