from app_def import app
from choroplethmapbox import get_choroplethmap_fig
from pre_process import *
from utils import add_annotations_to_fig
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

options = list()
for key, value in statistic_area.items():
    if key != 'הכל':
        options.append({'label': "  " + key + ' ' + str(value),
                        'value': value})
    else:
        options.append({'label': "  " + key,
                        'value': value})

citizen0, citizen1 = dfs_dict['df_salaries_t0'], dfs_dict['df_salaries_t1']

# percentage change in % units from time0 to time1
percentage_change = 100 * (citizen1.ResNum - citizen0.ResNum) / citizen0.ResNum
values_for_heatmap = {statzone_code: perc_change for statzone_code, perc_change in
                      zip(stat_zones_names_dict.keys(), percentage_change)}
map_fig = get_choroplethmap_fig(values_dict={k: int(v) for k, v in values_for_heatmap.items()},
                                map_title="% of change in total crime cases",
                                colorscale=[[0, '#561162'], [0.5, 'white'], [1, '#0B3B70']],
                                hovertemplate='<b>StatZone</b>: %{text}' + '<br><b>Precentage of change</b>: %{customdata}%<br>')
map_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})


@app.callback(
    Output(component_id='haredim', component_property='figure'),
    Output(component_id='gender', component_property='figure'),
    Output(component_id='age_group', component_property='figure'),
    Input(component_id='areas', component_property='value')
)
def get_graphs(statzone):
    haredim_df = dfs_dict['df_haredim_t1']
    gender_df = dfs_dict['df_salaries_t1'][['StatZone', 'Women', 'Men']]
    gender_df['Total'] = gender_df['Women'] + gender_df['Men']
    age_group_df = dfs_dict['df_salaries_t1'][['StatZone', '18_34', '35_44', '45_54', '55_64', '65_74', '75_84', '85+']]
    age_group_df_old = dfs_dict['df_salaries_t0'][
        ['StatZone', '18_34', '35_44', '45_54', '55_64', '65_74', '75_84', '85+']]

    if statzone == 0:
        haredim_df = haredim_df.append({'StatZone': 'All', 'TotHaredim': haredim_df['TotHaredim'].sum(),
                                        'TotNonHaredim': haredim_df['TotNonHaredim'].sum(),
                                        'Total': haredim_df['Total'].sum(),
                                        'PropoHaredim': haredim_df['PropoHaredim'].sum()}, ignore_index=True)
        haredim_df = haredim_df[haredim_df['StatZone'] == 'All']

        gender_df = gender_df.append({'StatZone': 'All', 'Women': gender_df['Women'].sum(),
                                      'Men': gender_df['Men'].sum(), 'Total': gender_df['Total'].sum()},
                                     ignore_index=True)
        gender_df = gender_df[gender_df['StatZone'] == 'All']

        age_group_df = age_group_df.append({'StatZone': 'All', '18_34': age_group_df['18_34'].sum(),
                                            '35_44': age_group_df['35_44'].sum(), '45_54': age_group_df['45_54'].sum(),
                                            '55_64': age_group_df['55_64'].sum(), '65_74': age_group_df['65_74'].sum(),
                                            '75_84': age_group_df['75_84'].sum(), '85+': age_group_df['85+'].sum(),
                                            },
                                           ignore_index=True)
        age_group_df = age_group_df[age_group_df['StatZone'] == 'All']

        age_group_df_old = age_group_df_old.append({'StatZone': 'All', '18_34': age_group_df_old['18_34'].sum(),
                                                    '35_44': age_group_df_old['35_44'].sum(),
                                                    '45_54': age_group_df_old['45_54'].sum(),
                                                    '55_64': age_group_df_old['55_64'].sum(),
                                                    '65_74': age_group_df_old['65_74'].sum(),
                                                    '75_84': age_group_df_old['75_84'].sum(),
                                                    '85+': age_group_df_old['85+'].sum(),
                                                    },
                                                   ignore_index=True)
        age_group_df_old = age_group_df_old[age_group_df_old['StatZone'] == 'All']

        title1 = 'Haredim percentage in All Statistical zones'
        title2 = 'Genders percentages in All Statistical zones'
        title3 = 'Age groups distribution in All Statistical zones'
    else:
        haredim_df = haredim_df[haredim_df['StatZone'] == statzone]
        gender_df = gender_df[gender_df['StatZone'] == statzone]
        age_group_df = age_group_df[age_group_df['StatZone'] == statzone]
        age_group_df_old = age_group_df_old[age_group_df_old['StatZone'] == statzone]
        title1 = f'Haredim percentage in {statzone} stat zone'
        title2 = f'Genders percentages in {statzone} stat zone'
        title3 = f'Age groups distribution in {statzone} stat zone'

    pie1_df = {'Label': ['חרדים', 'לא חרדים'],
               'Amount': [int(haredim_df['TotHaredim']), int(haredim_df['Total']) - int(haredim_df['TotHaredim'])]}
    pie1_df['Label'] = [(str(x)[::-1]) for x in pie1_df['Label']]

    fig1 = px.pie(pie1_df, values='Amount', names='Label', title=title1, color='Label',
                  color_discrete_map={list(pie1_df['Label'])[0]: '#8FBC8F', list(pie1_df['Label'])[1]: '#F5DEB3'})

    pie2_df = {'Gender': ['גברים', 'נשים'],
               'Amount': [int(gender_df['Men']), int(gender_df['Total']) - int(gender_df['Men'])]}
    pie2_df['Gender'] = [(str(x)[::-1]) for x in pie2_df['Gender']]

    fig2 = px.pie(pie2_df, values='Amount', names='Gender', title=title2, color='Gender',
                  color_discrete_map={list(pie2_df['Gender'])[0]: 'skyblue', list(pie2_df['Gender'])[1]: 'lightpink'})
    age_group_df_new = pd.DataFrame(columns=['Age group', 'Amount of citizen'])
    age_group_df_old_new = pd.DataFrame(columns=['Age group', 'Amount of citizen'])
    old_y = []
    percentage_change = []
    for col in age_group_df.columns:
        if col == 'StatZone':
            continue
        if col == '85+':
            col_name = col
        else:
            col_name = col[:2] + '-' + col[3:]
        age_group_df_new = age_group_df_new.append({'Amount of citizen': int(age_group_df[col]), 'Age group': col_name},
                                                   ignore_index=True)
        age_group_df_old_new = age_group_df_old_new.append(
            {'Amount of citizen': int(age_group_df_old[col]), 'Age group': col_name}, ignore_index=True)
        new, old = int(age_group_df[col]), int(age_group_df_old[col])
        percentage_change.append(100 * (new - old) / old if old != 0 else 100)
        old_y.append(int(age_group_df_old[col]))

    fig3 = px.bar(age_group_df_new, y=age_group_df_new['Amount of citizen'],
                  x=age_group_df_new['Age group'], title=title3, color_discrete_sequence=['#252E3F'])
    fig3.update_layout(title_text=title1,
                       yaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ),
                       xaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ), xaxis_showgrid=True, yaxis_showgrid=True)
    add_annotations_to_fig(fig3, fig3.data[0].x, fig3.data[0].y, percentage_change, old_y=old_y)
    fig3.update_layout(showlegend=False)
    max_y = max(age_group_df_new['Amount of citizen'])
    fig3.update_layout(yaxis_range=[0, max_y * 1.1])

    return fig1, fig2, fig3


layout = html.Div(children=[
    html.H4(children='Choose the wanted area to see the graphs changes',
            style={'text-align': 'left', 'text-transform': 'none', 'font-family': 'sans-serif',
                   'letter-spacing': '0em'}, className="pretty_container"
            ),
    html.Div([
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
                    dcc.Graph(figure=map_fig)
                ], className="map_container"),
            ],
            className="row_rapper",
        ), ], className="pretty_container"),
    html.Div(
        [
            html.Div(
                [
                    dcc.Graph(id='haredim')
                ],
                className='narrow_container',
            ),
            html.Div(
                [
                    dcc.Graph(id='gender')
                ],
                className='narrow_container',
            ),
        ], ),
    html.Div(
        [dcc.Graph(id='age_group')
         ], className='pretty_container')]

)
