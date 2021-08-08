from app_def import app
from choroplethmapbox import get_choroplethmap_fig
from pre_process import *
from utils import add_annotations_to_fig, options_map, stat_zones_names_dict, options
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px


citizen0, citizen1 = dfs_dict['df_salaries_t0'], dfs_dict['df_salaries_t1']


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

        title1 = 'אחוז חרדים בכל שכונת הדר'[::-1]
        title2 = 'אחוז נשים וגברים בכל שכונת הדר'[::-1]
        title3 = 'התפלגות גילאים בכל שכונת הדר'[::-1]

    else:
        haredim_df = haredim_df[haredim_df['StatZone'] == statzone]
        gender_df = gender_df[gender_df['StatZone'] == statzone]
        age_group_df = age_group_df[age_group_df['StatZone'] == statzone]
        age_group_df_old = age_group_df_old[age_group_df_old['StatZone'] == statzone]
        title1 = f'אחוז חרדים באזור סטטיסטי {str(statzone)[::-1]} '[::-1]
        title2 = f'אחוז נשים וגברים באזור סטטיסטי {str(statzone)[::-1]} '[::-1]
        title3 = f'התפלגות גילאים באזור סטטיסטי {str(statzone)[::-1]} '[::-1]

    pie1_df = {'Label': ['חרדים', 'לא חרדים'],
               'Amount': [int(haredim_df['TotHaredim']), int(haredim_df['Total']) - int(haredim_df['TotHaredim'])]}
    pie1_df['Label'] = [(str(x)[::-1]) for x in pie1_df['Label']]

    fig1 = px.pie(pie1_df, values='Amount', names='Label', title=title1, color='Label',
                  color_discrete_map={list(pie1_df['Label'])[0]: '#8FBC8F', list(pie1_df['Label'])[1]: '#F5DEB3'})
    fig1.update_layout(title_x=0.5, )
    pie2_df = {'Gender': ['גברים', 'נשים'],
               'Amount': [int(gender_df['Men']), int(gender_df['Total']) - int(gender_df['Men'])]}
    pie2_df['Gender'] = [(str(x)[::-1]) for x in pie2_df['Gender']]

    fig2 = px.pie(pie2_df, values='Amount', names='Gender', title=title2, color='Gender',
                  color_discrete_map={list(pie2_df['Gender'])[0]: 'skyblue', list(pie2_df['Gender'])[1]: 'lightpink'})
    fig2.update_layout(title_x=0.5, )
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
    fig3.update_yaxes(title="כמות תושבים"[::-1])
    fig3.update_xaxes(title="קבוצת גיל"[::-1])
    fig3.update_layout(title_text=title3, title_x=0.5,

                       yaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ),
                       xaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ), xaxis_showgrid=True, yaxis_showgrid=True,
                       template='simple_white')
    add_annotations_to_fig(fig3, fig3.data[0].x, fig3.data[0].y, percentage_change, old_y=old_y)
    fig3.update_layout(showlegend=False)
    max_y = max(age_group_df_new['Amount of citizen'])
    fig3.update_layout(yaxis_range=[0, max_y * 1.1])
    return fig1, fig2, fig3


@app.callback(
    Output(component_id='primary_map_population', component_property='figure'),
    Input(component_id='map_definition', component_property='value')
)
def change_map(map_def):
    if map_def == 0:  # 'הצג מפת שינויים'
        percentage_change = 100 * (citizen1.ResNum - citizen0.ResNum) / citizen0.ResNum
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
                              zip(stat_zones_names_dict.keys(), citizen1.ResNum)}
        map_fig = get_choroplethmap_fig(values_dict={k: int(v) for k, v in values_for_heatmap.items()},
                                        map_title="Current values in total crime cases",
                                        colorscale=[[0, '#561162'], [0.5, 'white'], [1, '#0B3B70']],
                                        hovertemplate='<b>StatZone</b>: %{text}' + '<br><b>Current Value</b>: %{customdata}<br>',
                                        changes_map=False)
        map_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return map_fig


layout = html.Div(children=[
    html.H4(
        children=[html.H4(['.בעמוד הנוכחי תוכלו לראות מגוון נתונים בנושא הדמוגרפיה של הדר'],
                          style={'text-align': 'right', 'text-transform': 'none', 'font-family': 'sans-serif',
                                 'letter-spacing': '0em'}, ),
                  html.H4([
                      'ניתן לבחור ולראות מפה המציגה את הערכים הנוכחיים של כמות האוכלוסיה הכללית בכל אזור סטטיסטי, וכן מפה המראה את השינויים בין התקופות השונות. בהמשך מוצגים גרפים אשר מציגים מידע נוסף על אוכלוסיה זו, וניתן לבחור להציג בהם מידע רק על אזור סטטיסטי מסוים. מוצגת למטה החלוקה של האוכלוסיה לנשים / גברים ולאחוז החרדים (עבור הדר כולה או עבור האזור הנבחר - במעבר על גרף העוגה ניתן לראות גם את הערכים עצמם ולא רק אחוזים). בנוסף, מוצג גרף אשר מראה את התפלגות הגילאים ואת השינוי בין התקופות השונות']
                      , style={'text-align': 'right', 'text-transform': 'none', 'font-family': 'sans-serif',
                               'letter-spacing': '0em', 'line-height': '1.6em'}
                  )]
        ,
        className='pretty_container'
    ),
    html.Div([
        html.Div([html.H6('בחר את תצוגת המפה', style={'Font-weight': 'bold', 'text-transform': 'none',
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
                                                            value=0,
                                                            ),
                    ],
                    className="mini_container",
                ),
                html.Div([
                    dcc.Graph(id='primary_map_population')
                ], className="map_container"),
            ],
            className="row_rapper",
        ), ], className="pretty_container"),
    html.Div(
        [
            html.Div(
                [
                    dcc.Graph(id='haredim'),
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
         ], className='wide_container')]

)
