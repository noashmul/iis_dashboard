from choroplethmapbox import get_choroplethmap_fig
from app_def import app
from pre_process import *
from utils import add_annotations_to_fig
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np

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
# Calculate % change in total crime cases from time t0 to t1
crime0, crime1 = dfs_dict['df_crime_t0'], dfs_dict['df_crime_t1']
for df in [crime0, crime1]:
    df['total_crime_cases'] = df[[col for col in df.columns if col != 'StatZone' and col != 'Year']].sum(axis=1)


options_map = [{'label': ' הצג מפת שינויים ', 'value': 0}, {'label': ' הצג ערכים נוכחיים', 'value': 1}]


@app.callback(
    Output(component_id='crime_trend_graph', component_property='figure'),
    Output(component_id='crime_location_type', component_property='figure'),
    Output(component_id='crime_type', component_property='figure'),
    Input(component_id='areas', component_property='value')
)
def get_graphs(statzone):
    df_crimes = dfs_dict['df_crime_2010_to_2015']
    df_crimes = df_crimes[df_crimes['Year'] == 2012]
    if statzone == 0:
        statzone = 'All Statistical zones'

    """fig1"""
    if statzone == 'All Statistical zones':
        df_total_crimes = df_crimes.groupby(by=["Month"]).count()[['Street']] // 14
        df_total_crime_all = pd.DataFrame(columns=['Month', 'Amount of Crimes'])
        df_total_crime_all['Month'] = df_total_crimes['Street'].index
        df_total_crime_all['Amount of Crimes'] = df_total_crimes['Street'].values
        fig1 = px.scatter(df_total_crime_all, x=df_total_crime_all['Month']
                          , y=df_total_crime_all['Amount of Crimes'], color_discrete_sequence=['#252E3F'],
                          ).update_traces(mode='lines+markers')
        max_y = df_total_crime_all['Amount of Crimes'].max()
    else:
        df_total_crimes = df_crimes.groupby(by=["StatZone", "Month"]).count()[['Street']]
        df_tot_crime_per_area = pd.DataFrame(columns=['Month', 'Amount of Crimes'])
        df_tot_crime_per_area['Month'] = df_total_crimes.loc[statzone]['Street'].index
        df_tot_crime_per_area['Amount of Crimes'] = df_total_crimes.loc[statzone]['Street'].values
        fig1 = px.scatter(df_tot_crime_per_area, x=df_tot_crime_per_area['Month']
                          , y=df_tot_crime_per_area['Amount of Crimes'], color_discrete_sequence=['#252E3F'],
                          ).update_traces(mode='lines+markers')
        max_y = df_tot_crime_per_area['Amount of Crimes'].max()

    string = (str(statzone) + "באזור סטטיסטי "[::-1]) if statzone != 'All Statistical zones' else "בכל האזורים הסטטיסטיים"[::-1]

    # TODO this title is not visible because of the margin 0, add a title to the html
    fig1.update_layout(title_text=string + "מספר פשעים לפי חודש "[::-1],
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
    fig1.update_xaxes(title='חודש'[::-1])
    fig1.update_yaxes(title='כמות פשעים'[::-1])

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
        df_location = current_semi_annual.groupby(by=["CrimeLocType"]).count()[['Street']] // 14
        df_location = df_location.sort_values(by=['Street'], ascending=False).head(10)
        df_location.index = [s[::-1].strip(' ') for s in df_location.index]
        df_location.rename(columns={'Street': 'Amount of Crimes'}, inplace=True)

        prev_df_location = previous_semi_annual.groupby(by=["CrimeLocType"]).count()[['Street']] // 14
        prev_df_location = prev_df_location.sort_values(by=['Street'], ascending=False)
        prev_df_location.index = [s[::-1].strip(' ') for s in prev_df_location.index]
        prev_df_location = prev_df_location.loc[[idx for idx in df_location.index if idx in prev_df_location.index]]
        prev_df_location.rename(columns={'Street': 'Amount of Crimes'}, inplace=True)

        for idx in df_location.index:
            if idx in prev_df_location.index:
                old, new = float(prev_df_location.loc[idx].values), float(df_location.loc[idx].values)
                percentage_change_value.append(100 * (new - old) / old if old != 0 else 100)
                old_y.append(old)
            else:
                percentage_change_value.append(np.nan)
                old_y.append(np.nan)

    else:
        df_location = current_semi_annual.groupby(by=["StatZone", "CrimeLocType"]).count()[['Street']]
        df_location = df_location.loc[statzone].sort_values(by=['Street'], ascending=False).head(10)
        df_location.index = [s[::-1].strip(' ') for s in df_location.index]
        df_location.rename(columns={'Street': 'Amount of Crimes'}, inplace=True)

        prev_df_location = previous_semi_annual.groupby(by=["StatZone", "CrimeLocType"]).count()[['Street']]
        prev_df_location = prev_df_location.loc[statzone].sort_values(by=['Street'], ascending=False)
        prev_df_location.index = [s[::-1].strip(' ') for s in prev_df_location.index]
        prev_df_location = prev_df_location.loc[[idx for idx in df_location.index if idx in prev_df_location.index]]
        prev_df_location.rename(columns={'Street': 'Amount of Crimes'}, inplace=True)

        for idx in df_location.index:
            if idx in prev_df_location.index:
                old, new = float(prev_df_location.loc[idx].values), float(df_location.loc[idx].values)
                percentage_change_value.append(100 * (new - old) / old if old != 0 else 100)
                old_y.append(old)
            else:
                percentage_change_value.append(np.nan)
                old_y.append(np.nan)

    # TODO the next two graphs are not centered and are being cut from the bottom
    fig2 = px.bar(df_location, x=df_location.index, y=df_location['Amount of Crimes'],
                  color_discrete_sequence=['#252E3F'])


    # for_title = "crimes per location" if graph_type == "CrimeLocType" else "crimes per type"
    fig2.update_layout(title_text=string + "מספר פשעים לפי סוג מיקום "[::-1],
                       title_x=0.5,
                       yaxis=dict(
                           titlefont_size=14,
                           tickfont_size=14,
                       ),
                       xaxis=dict(
                           titlefont_size=14,
                           tickfont_size=14,
                       ), xaxis_showgrid=True, yaxis_showgrid=True,
                       template='simple_white',
                       showlegend=False,
                       yaxis_range=[0, max(fig2.data[0].y) * 1.2]
                       )
    fig2.update_xaxes(title='סוג מיקום'[::-1], tickangle=45)
    fig2.update_yaxes(title='כמות פשעים'[::-1])
    add_annotations_to_fig(fig=fig2, x=fig2.data[0].x, y=fig2.data[0].y,
                           percentage_change_value=percentage_change_value, old_y=old_y)

    """fig3"""
    percentage_change_value, old_y = [], []
    if statzone == 'All Statistical zones':
        df_type = current_semi_annual.groupby(by=["CrimeType"]).count()[['Street']] // 14
        df_type = df_type.sort_values(by=['Street'], ascending=False).head(10)
        df_type.index = [s[::-1].strip(' ') for s in df_type.index]
        df_type.rename(columns={'Street': 'Amount of Crimes'}, inplace=True)

        prev_df_type = previous_semi_annual.groupby(by=["CrimeType"]).count()[['Street']] // 14
        prev_df_type = prev_df_type.sort_values(by=['Street'], ascending=False)
        prev_df_type.index = [s[::-1].strip(' ') for s in prev_df_type.index]
        prev_df_type = prev_df_type.loc[[idx for idx in df_type.index if idx in prev_df_type.index]]
        prev_df_type.rename(columns={'Street': 'Amount of Crimes'}, inplace=True)

        for idx in df_type.index:
            if idx in prev_df_type.index:
                old, new = float(prev_df_type.loc[idx].values), float(df_type.loc[idx].values)
                percentage_change_value.append(100 * (new - old) / old if old != 0 else 100)
                old_y.append(old)
            else:
                percentage_change_value.append(np.nan)
                old_y.append(np.nan)
    else:
        df_type = current_semi_annual.groupby(by=["StatZone", "CrimeType"]).count()[['Street']]
        df_type = df_type.loc[statzone].sort_values(by=['Street'], ascending=False).head(10)
        df_type.index = [s[::-1].strip(' ') for s in df_type.index]
        df_type.rename(columns={'Street': 'Amount of Crimes'}, inplace=True)

        prev_df_type = previous_semi_annual.groupby(by=["StatZone", "CrimeType"]).count()[['Street']]
        prev_df_type = prev_df_type.loc[statzone].sort_values(by=['Street'], ascending=False)
        prev_df_type.index = [s[::-1].strip(' ') for s in prev_df_type.index]
        prev_df_type = prev_df_type.loc[[idx for idx in df_type.index if idx in prev_df_type.index]]
        prev_df_type.rename(columns={'Street': 'Amount of Crimes'}, inplace=True)

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
    fig3.update_layout(title_text=string + "מספר פשעים לפי סוג פשע "[::-1],
                       title_x=0.5,
                       yaxis=dict(
                           titlefont_size=14,
                           tickfont_size=14,
                       ),
                       xaxis=dict(
                           titlefont_size=14,
                           tickfont_size=14,
                       ), xaxis_showgrid=True, yaxis_showgrid=True,
                       template='simple_white',
                       showlegend=False,
                       yaxis_range=[0, max(fig3.data[0].y) * 1.2],
                       )
    fig3.update_xaxes(title='סוג פשע'[::-1], tickangle=45)
    fig3.update_yaxes(title='כמות פשעים'[::-1])
    add_annotations_to_fig(fig=fig3, x=fig3.data[0].x, y=fig3.data[0].y,
                           percentage_change_value=percentage_change_value, old_y=old_y)

    return fig1, fig2, fig3


@app.callback(
    Output(component_id='primary_map_crime', component_property='figure'),
    Input(component_id='map_definition', component_property='value')
)
def change_map(map_def):
    if map_def == 0:  # 'הצג מפת שינויים'
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
                                  'ניתן לבחור ולראות מפה המציגה את הערכים הנוכחיים של הפשיעה הכוללת בכל אזור סטטיסטי, וכן מפה המראה את השינויים מהחצי שנה הקודמת. בהמשך מוצגים גרפים אשר מציגים מידע נוסף על הפשיעה, וניתן לבחור להציג בהם מידע רק על אזור סטטיסטי מסוים. הגרף הראשון מציג את מגמת הפשיעה בשנה האחרונה, עם הפרדה בין החצי שנה הנוכחית לקודמת. הנוסף אליו מוצגים 2 גרפים המציגים את כמות הפשיעה מבחינת מיקומים ומבחינת סוגי פשעים. ב2 הגרפים מוצגת גם מגמת השינוי בחצי שנה הנוכחית מהחצי שנה הקודמת לה. שימו לב לעבור על הגרפים ולראות את המיגע הנוסף שהם מציגים']
                              , style={'text-align': 'right', 'text-transform': 'none', 'font-family': 'sans-serif',
                                       'letter-spacing': '0em', 'line-height':'1.6em'}
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
                            ': בחר אזור', dcc.RadioItems(id='areas',
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
                # id="info-container1",
                className="row_rapper",
            ),
        ], className='pretty_container'),
        html.Div(
            [
                dcc.Graph(id='crime_trend_graph')
            ], className="pretty_container"
        ),
        # html.Div(
        #     [
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
        #     ],
        #     id="info-container2",
        #     className="row container-display",
        # )
    ],
    # className="pretty_container twelve columns",
    style={"text-align": "justify"},
)
