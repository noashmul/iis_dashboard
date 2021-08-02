from app_def import app
from pre_process import *


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
        options.append({'label': "  " + key + ' ' + str(value),
                        'value': value})
    else:
        options.append({'label': "  " + key,
                        'value': value})


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
    df_avg_sal['Salary type'] = ['שכר כולל מעבודה (לא כולל עבודה במשק בית)', 'שכר כולל מעבודה במשק בית',
                                 'שכר כולל מפנסיה',
                                 'שכר כולל מקצבת שארים (שלא מהביטוח הלאומי)', 'הכנסה מעבודה עצמאית']
    if statzone == 0:
        statzone = 'All Statistical zones'
        df_salary = df_salary[['SalNoHKResNum', 'SalHKResNum', 'SalPenResNum', 'SalSHNoBTLResNum', 'IncSelfResNum',
                               'SalNoHKAve', 'SalHKAve', 'SalPenAve', 'SalSHNoBTLAve', 'IncSelfAve']]
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

    fig1 = px.bar(df_avg_sal, x=df_avg_sal['Salary type'],
                  y=df_avg_sal['Average salary'])
    fig1.update_layout(title_text=title1,
                       yaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ),
                       xaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ), xaxis_showgrid=True, yaxis_showgrid=True)
    fig1.update_xaxes(tickangle=45)

    df_amount_of_workers = pd.DataFrame(columns=['Salary type', 'Amount of workers'])
    df_amount_of_workers['Salary type'] = ['שכר כולל מעבודה (לא כולל עבודה במשק בית)', 'שכר כולל מעבודה במשק בית',
                                           'שכר כולל מפנסיה',
                                           'שכר כולל מקצבת שארים (שלא מהביטוח הלאומי)', 'הכנסה מעבודה עצמאית']
    df_amount_of_workers['Amount of workers'] = [df_salary['SalNoHKResNum'].sum(), df_salary['SalHKResNum'].sum(),
                                                 df_salary['SalPenResNum'].sum(), df_salary['SalSHNoBTLResNum'].sum(),
                                                 df_salary['IncSelfResNum'].sum()]
    fig2 = px.bar(df_amount_of_workers, x=df_amount_of_workers['Salary type'],
                  y=df_amount_of_workers['Amount of workers'])
    fig2.update_layout(title_text=title2,
                       yaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ),
                       xaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ), xaxis_showgrid=True, yaxis_showgrid=True)
    fig1.update_xaxes(tickangle=45)

    return fig1, fig2


layout = html.Div(children=[

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
                                                    value='הכל'
                                                    ),
                ],
                className="mini_container",
            ), ]),
    html.Div(
        [
            html.Div(
                [
                    dcc.Graph(id='Avg_salary')
                ],
                className='narrow_container',
            ),
            html.Div(
                [
                    dcc.Graph(id='Amount_of_workers')
                ],
                className='narrow_container',
            ),
        ],)
]

)
