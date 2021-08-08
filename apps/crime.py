from choroplethmapbox import get_choroplethmap_fig
from app_def import app
from pre_process import *
from utils import add_annotations_to_fig, options_map, stat_zones_names_dict, options
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np

# Calculate % change in total crime cases from time t0 to t1
crime0, crime1 = dfs_dict['df_crime_t0'], dfs_dict['df_crime_t1']
for df in [crime0, crime1]:
    df['total_crime_cases'] = df[[col for col in df.columns if col != 'StatZone' and col != 'Year']].sum(axis=1)



@app.callback(
    Output(component_id='crime_trend_graph', component_property='figure'),
    Output(component_id='crime_location_type', component_property='figure'),
    Output(component_id='crime_type', component_property='figure'),
    Input(component_id='areas', component_property='value')
)
def get_graphs(statzone):
    df_crimes_cases_t0 = dfs_dict['df_crimes_cases_t0']
    df_crimes_cases_t0['tmp_col'] = 1
    df_crimes_cases_t1 = dfs_dict['df_crimes_cases_t1']
    df_crimes_cases_t1['tmp_col'] = 1
    df_crimes = pd.concat([df_crimes_cases_t0, df_crimes_cases_t1])

    if statzone == 0:
        statzone = 'All Statistical zones'

    """fig1"""
    if statzone == 'All Statistical zones':
        df_total_crimes = df_crimes.groupby(by=["Month"]).count()[['tmp_col']] // 14
        df_total_crime_all = pd.DataFrame(columns=['Month', 'Amount of Crimes'])
        df_total_crime_all['Month'] = df_total_crimes['tmp_col'].index
        df_total_crime_all['Amount of Crimes'] = df_total_crimes['tmp_col'].values
        fig1 = px.scatter(df_total_crime_all, x=df_total_crime_all['Month']
                          , y=df_total_crime_all['Amount of Crimes'], color_discrete_sequence=['#252E3F'],
                          ).update_traces(mode='lines+markers')
        max_y = df_total_crime_all['Amount of Crimes'].max()
    else:
        df_total_crimes = df_crimes.groupby(by=["StatZone", "Month"]).count()[['tmp_col']]
        df_tot_crime_per_area = pd.DataFrame(columns=['Month', 'Amount of Crimes'])
        df_tot_crime_per_area['Month'] = df_total_crimes.loc[statzone]['tmp_col'].index
        df_tot_crime_per_area['Amount of Crimes'] = df_total_crimes.loc[statzone]['tmp_col'].values
        fig1 = px.scatter(df_tot_crime_per_area, x=df_tot_crime_per_area['Month']
                          , y=df_tot_crime_per_area['Amount of Crimes'], color_discrete_sequence=['#252E3F'],
                          ).update_traces(mode='lines+markers')
        max_y = df_tot_crime_per_area['Amount of Crimes'].max()

    string = (str(statzone) + "באזור סטטיסטי "[::-1]) if statzone != 'All Statistical zones' else \
        "בכל שכונת הדר"[::-1]

    fig1.update_xaxes(title='חודש'[::-1])
    fig1.update_yaxes(title='כמות פשעים'[::-1])
    fig1.update_layout(title_text=string + "מספר פשעים לפי חודש "[::-1], titlefont_size=18,
                       title_x=0.5,
                       yaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ),
                       xaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                           tickvals=[i for i in range(13)],
                           ticktext=[i for i in range(13)]
                       ), xaxis_showgrid=True, yaxis_showgrid=True,
                       template='none',
                       yaxis_range=[0, max_y * 1.1],
                       showlegend=False)
    fig1.add_vline(x=6.5, line_width=3, line_dash="dash", line_color="#EE553B")

    fig1.add_trace(go.Scatter(
        x=[3.5, 9.5],
        y=[min(fig1.data[0].y) / 2.5, min(fig1.data[0].y) / 2.5],
        mode="text",
        text=['חצי השנה של הדו"ח הקודם'[::-1], 'חצי השנה של הדו"ח הנוכחי'[::-1]],
        textposition="top center",
        textfont=dict(
            family="sans serif",
            size=24,
            color="black"
        ),
        name=''
    ))

    """fig2"""
    current_semi_annual = df_crimes[df_crimes['Month'] >= 7]
    previous_semi_annual = df_crimes[df_crimes['Month'] < 7]
    percentage_change_value, old_y = [], []

    if statzone == 'All Statistical zones':
        df_location = current_semi_annual.groupby(by=["CrimeLocType"]).count()[['tmp_col']] // 14
        df_location = df_location.sort_values(by=['tmp_col'], ascending=False).head(10)
        df_location.index = [s[::-1].strip(' ') for s in df_location.index]
        df_location.rename(columns={'tmp_col': 'Amount of Crimes'}, inplace=True)

        prev_df_location = previous_semi_annual.groupby(by=["CrimeLocType"]).count()[['tmp_col']] // 14
        prev_df_location = prev_df_location.sort_values(by=['tmp_col'], ascending=False)
        prev_df_location.index = [s[::-1].strip(' ') for s in prev_df_location.index]
        prev_df_location = prev_df_location.loc[[idx for idx in df_location.index if idx in prev_df_location.index]]
        prev_df_location.rename(columns={'tmp_col': 'Amount of Crimes'}, inplace=True)

        for idx in df_location.index:
            if idx in prev_df_location.index:
                old, new = float(prev_df_location.loc[idx].values), float(df_location.loc[idx].values)
                percentage_change_value.append(100 * (new - old) / old if old != 0 else 100)
                old_y.append(old)
            else:
                percentage_change_value.append(np.nan)
                old_y.append(np.nan)

    else:
        df_location = current_semi_annual.groupby(by=["StatZone", "CrimeLocType"]).count()[['tmp_col']]
        df_location = df_location.loc[statzone].sort_values(by=['tmp_col'], ascending=False).head(10)
        df_location.index = [s[::-1].strip(' ') for s in df_location.index]
        df_location.rename(columns={'tmp_col': 'Amount of Crimes'}, inplace=True)

        prev_df_location = previous_semi_annual.groupby(by=["StatZone", "CrimeLocType"]).count()[['tmp_col']]
        prev_df_location = prev_df_location.loc[statzone].sort_values(by=['tmp_col'], ascending=False)
        prev_df_location.index = [s[::-1].strip(' ') for s in prev_df_location.index]
        prev_df_location = prev_df_location.loc[[idx for idx in df_location.index if idx in prev_df_location.index]]
        prev_df_location.rename(columns={'tmp_col': 'Amount of Crimes'}, inplace=True)

        for idx in df_location.index:
            if idx in prev_df_location.index:
                old, new = float(prev_df_location.loc[idx].values), float(df_location.loc[idx].values)
                percentage_change_value.append(100 * (new - old) / old if old != 0 else 100)
                old_y.append(old)
            else:
                percentage_change_value.append(np.nan)
                old_y.append(np.nan)

    fig2 = px.bar(df_location, x=df_location.index, y=df_location['Amount of Crimes'],
                  color_discrete_sequence=['#252E3F'])

    fig2.update_xaxes(title='סוג מיקום'[::-1], tickangle=45)
    fig2.update_yaxes(title='כמות פשעים'[::-1])
    # for_title = "crimes per location" if graph_type == "CrimeLocType" else "crimes per type"
    fig2.update_layout(title_text=string + "מספר פשעים לפי סוג מיקום "[::-1], titlefont_size=18,
                       title_x=0.5,
                       yaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ),
                       xaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ), xaxis_showgrid=True, yaxis_showgrid=True,
                       template='simple_white',
                       showlegend=False,
                       yaxis_range=[0, max(fig2.data[0].y) * 1.2]
                       )

    add_annotations_to_fig(fig=fig2, x=fig2.data[0].x, y=fig2.data[0].y,
                           percentage_change_value=percentage_change_value, old_y=old_y)

    """fig3"""
    percentage_change_value, old_y = [], []
    if statzone == 'All Statistical zones':
        df_type = current_semi_annual.groupby(by=["CrimeType"]).count()[['tmp_col']] // 14
        df_type = df_type.sort_values(by=['tmp_col'], ascending=False).head(10)
        df_type.index = [s[::-1].strip(' ') for s in df_type.index]
        df_type.rename(columns={'tmp_col': 'Amount of Crimes'}, inplace=True)

        prev_df_type = previous_semi_annual.groupby(by=["CrimeType"]).count()[['tmp_col']] // 14
        prev_df_type = prev_df_type.sort_values(by=['tmp_col'], ascending=False)
        prev_df_type.index = [s[::-1].strip(' ') for s in prev_df_type.index]
        prev_df_type = prev_df_type.loc[[idx for idx in df_type.index if idx in prev_df_type.index]]
        prev_df_type.rename(columns={'tmp_col': 'Amount of Crimes'}, inplace=True)

        for idx in df_type.index:
            if idx in prev_df_type.index:
                old, new = float(prev_df_type.loc[idx].values), float(df_type.loc[idx].values)
                percentage_change_value.append(100 * (new - old) / old if old != 0 else 100)
                old_y.append(old)
            else:
                percentage_change_value.append(np.nan)
                old_y.append(np.nan)
    else:
        df_type = current_semi_annual.groupby(by=["StatZone", "CrimeType"]).count()[['tmp_col']]
        df_type = df_type.loc[statzone].sort_values(by=['tmp_col'], ascending=False).head(10)
        df_type.index = [s[::-1].strip(' ') for s in df_type.index]
        df_type.rename(columns={'tmp_col': 'Amount of Crimes'}, inplace=True)

        prev_df_type = previous_semi_annual.groupby(by=["StatZone", "CrimeType"]).count()[['tmp_col']]
        prev_df_type = prev_df_type.loc[statzone].sort_values(by=['tmp_col'], ascending=False)
        prev_df_type.index = [s[::-1].strip(' ') for s in prev_df_type.index]
        prev_df_type = prev_df_type.loc[[idx for idx in df_type.index if idx in prev_df_type.index]]
        prev_df_type.rename(columns={'tmp_col': 'Amount of Crimes'}, inplace=True)

        for idx in df_type.index:
            if idx in prev_df_type.index:
                old, new = float(prev_df_type.loc[idx].values), float(df_type.loc[idx].values)
                percentage_change_value.append(100 * (new - old) / old if old != 0 else 100)
                old_y.append(old)
            else:
                percentage_change_value.append(np.nan)
                old_y.append(np.nan)

    fig3 = px.bar(df_type, x=df_type.index, y=df_type['Amount of Crimes'],
                  color_discrete_sequence=['#252E3F'])
    fig3.update_xaxes(title='סוג פשע'[::-1], tickangle=45)
    fig3.update_yaxes(title='כמות פשעים'[::-1])
    fig3.update_layout(title_text=string + "מספר פשעים לפי סוג פשע "[::-1], titlefont_size=18,
                       title_x=0.5,
                       yaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ),
                       xaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ), xaxis_showgrid=True, yaxis_showgrid=True,
                       template='simple_white',
                       showlegend=False,
                       yaxis_range=[0, max(fig3.data[0].y) * 1.2],
                       )

    add_annotations_to_fig(fig=fig3, x=fig3.data[0].x, y=fig3.data[0].y,
                           percentage_change_value=percentage_change_value, old_y=old_y)

    return fig1, fig2, fig3


@app.callback(
    Output(component_id='primary_map_crime', component_property='figure'),
    Input(component_id='map_definition', component_property='value')
)
def change_map(map_def):
    if map_def == 0:  # 'שינוי באחוזים מהדו"ח הקודם'
        # percentage change in % units from time0 to time1
        percentage_change = 100 * (crime1.total_crime_cases - crime0.total_crime_cases) / crime0.total_crime_cases
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
                              zip(stat_zones_names_dict.keys(), crime1.total_crime_cases)}
        map_fig = get_choroplethmap_fig(values_dict={k: int(v) for k, v in values_for_heatmap.items()},
                                        map_title="Current values in total crime cases",
                                        colorscale=[[0, '#561162'], [0.5, 'white'], [1, '#0B3B70']],
                                        hovertemplate='<b>StatZone</b>: %{text}' + '<br><b>Current Value</b>: %{customdata}<br>',
                                        changes_map=False)
        map_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return map_fig


layout = html.Div(
    children=[
        html.H4(
            children=[html.H4(['.בעמוד הנוכחי תוכלו לראות מגוון נתונים בנושא הפשיעה בהדר'],
                              style={'text-align': 'right', 'text-transform': 'none', 'font-family': 'sans-serif',
                                     'letter-spacing': '0em'}, ),
                      html.H4([
                          'ניתן לבחור ולראות מפה המציגה את הערכים הנוכחיים של הפשיעה הכוללת בכל אזור סטטיסטי, וכן מפה המראה את השינויים מהחצי שנה הקודמת. בהמשך מוצגים גרפים אשר מציגים מידע נוסף על הפשיעה, וניתן לבחור להציג בהם מידע רק על אזור סטטיסטי מסוים. הגרף הראשון מציג את מגמת הפשיעה בשנה האחרונה, עם הפרדה בין החצי שנה הנוכחית לקודמת. בנוסף אליו מוצגים 2 גרפים המציגים את כמות הפשיעה מבחינת מיקומים ומבחינת סוגי פשעים. ב2 הגרפים מוצגת גם מגמת השינוי בין התקופות השונות. שימו לב לעבור על הגרפים ולראות את המידע בנוסף שהם מציגים']
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
                                                                value=0
                                                                ),
                        ],
                        className="mini_container",
                    ),
                    html.Div([
                        dcc.Graph(id='primary_map_crime')
                    ], className="map_container"),
                ],
                className="row_rapper",
            ),
        ], className='pretty_container'),
        html.Div(
            [
                dcc.Graph(id='crime_trend_graph')
            ], className="pretty_container"
        ),
        html.Div(
            [
                dcc.Graph(id='crime_location_type')
            ],
            className='pretty_container',
        ),
        html.Div(
            [
                dcc.Graph(id='crime_type')
            ],
            className='pretty_container',
        ),
    ],
    style={"text-align": "justify"},
)
