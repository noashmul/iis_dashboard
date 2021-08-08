from choroplethmapbox import get_choroplethmap_fig
from app_def import app
from pre_process import *
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
from utils import add_annotations_to_fig, options_map, stat_zones_names_dict, options


def blank_fig(height):
    """
    Build blank figure with the requested height
    """
    return {
        "data": [],
        "layout": {
            "height": height,
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
        },
    }


def manipulate_holucaust_df(df, statzone):
    df["HoloSurvNdDesc"].dropna()
    df['tmp_col'] = 1
    df = df.replace(
        {'בעיות הנובעות ממחלות אקוטיות או כרוניות (למעט בריאות הנפש)': 'מחלות אקוטיות או כרוניות',
         'בעיות הנובעות מרמת הכנסה נמוכה או מירידה ברמת הכנסה': 'רמת הכנסה נמוכה',
         'בעיות הנובעות ממומים ו/או מגבלות פיזיות (נכות)': 'נכות',
         'בעיות בתקשורת בקליטה (עלייה)': 'בעיות בתקשורת וקליטה'})
    df["HoloSurvNdDesc"] = df["HoloSurvNdDesc"].apply(
        lambda x: str(x)[:-1] + '(' if str(x)[-1] == ')' else x)
    if statzone == 'All Statistical Zones':  # TODO delete or statzone==623
        df_holocaust1_type = df.groupby(by=["HoloSurvNdDesc"]).count()[['tmp_col']]
        df_holocaust1_type = df_holocaust1_type.sort_values(by=['tmp_col'], ascending=False).head(5)
    else:
        df_holocaust1_type = df.groupby(by=["StatZone", "HoloSurvNdDesc"]).count()[['tmp_col']]
        df_holocaust1_type = df_holocaust1_type.loc[statzone].sort_values(by=['tmp_col'], ascending=False).head(5)

    df_holocaust1_type.index = [s[::-1].strip(' ') for s in df_holocaust1_type.index]
    df_holocaust1_type.rename(columns={'tmp_col': 'Amount of Holocaust Survivors'}, inplace=True)
    return df_holocaust1_type



# Calculate % change in total amount of seniors from time t0 to t1
seniors0, seniors1 = dfs_dict['df_seniors_t0'], dfs_dict['df_seniors_t1']
seniors0['tmp_col'] = 1
seniors1['tmp_col'] = 1
# percentage change in % units from time0 to time1
seniors1_per_zone = seniors1.groupby(by=["StatZone"]).count()[['tmp_col']]
seniors0_per_zone = seniors0.groupby(by=["StatZone"]).count()[['tmp_col']]


@app.callback(
    Output(component_id='seniors_type', component_property='figure'),
    Output(component_id='needed_help_type', component_property='figure'),
    Output(component_id='num_holocaust_survivors', component_property='figure'),
    Input(component_id='areas', component_property='value')
)
def get_graphs(statzone):
    df_seniors1 = dfs_dict['df_seniors_t1']

    if statzone == 0:
        statzone = 'All Statistical Zones'

    if statzone != 'All Statistical Zones':
        df_seniors1 = df_seniors1[df_seniors1['StatZone'] == statzone]

    food1_alone1 = len(df_seniors1[(df_seniors1['SeniorAlone'] == 1) &
                                   (df_seniors1['SeniorRecivFood'] == 1)])
    food1_alone0 = len(df_seniors1[(df_seniors1['SeniorAlone'] == 0) &
                                   (df_seniors1['SeniorRecivFood'] == 1)])
    food0_alone1 = len(df_seniors1[(df_seniors1['SeniorAlone'] == 1) &
                                   (df_seniors1['SeniorRecivFood'] == 0)])
    food0_alone0 = len(df_seniors1[(df_seniors1['SeniorAlone'] == 0) &
                                   (df_seniors1['SeniorRecivFood'] == 0)])

    pie_df = pd.DataFrame.from_dict(
        {'status': ['קשישים בודדים ומקבלי מזון', 'קשישים מקבלי מזון', 'קשישים בודדים', 'אחר'],
         'amount': [food1_alone1, food1_alone0, food0_alone1, food0_alone0]})

    pie_df['status'] = pie_df['status'].apply(lambda x: str(x)[::-1])
    fig1 = px.pie(pie_df, values='amount', names='status', title='Status of seniors citizens',
                  color='status', color_discrete_map={list(pie_df['status'])[0]: '#19D3F3',
                                                      list(pie_df['status'])[1]: '#0099C6',
                                                      list(pie_df['status'])[2]: '#636EFA',
                                                      list(pie_df['status'])[3]: 'darkblue'}
                  )

    string = " Stat Zone " if statzone != 'All Statistical Zones' else " "
    statzone_name = str(statzone)[::-1]
    title1 = "מצב האזרחים המבוגרים בכל שכונת הדר"[
             ::-1] if statzone == 'All Statistical Zones' else f"מצב האזרחים המבוגרים באזור סטטיסטי {statzone_name}"[
                                                               ::-1]

    fig1.update_layout(title_text=title1,
                       yaxis=dict(
                           titlefont_size=18,
                       ),
                       xaxis=dict(
                           titlefont_size=18,
                       ), legend={'traceorder': 'normal'},
                       template='none',
                       )
    df_holocaust0 = dfs_dict['df_holocaust_t0']
    df_holocaust1 = dfs_dict['df_holocaust_t1']
    if statzone == 'All Statistical Zones':
        text3 = len(df_holocaust1)
    else:
        text3 = len(df_holocaust1[df_holocaust1['StatZone'] == statzone])

    text3 = int(text3)
    text3_display = {
        "data": [
            {
                "type": "indicator",
                "value": text3,
                "number": {"font": {"color": "#263238"}},
            }
        ],
        "layout": {
            # "template": template,
            "height": 150,
            "margin": {"l": 10, "r": 10, "t": 10, "b": 10},
        },
    }

    df_holocaust1_type = manipulate_holucaust_df(df_holocaust1, statzone)
    df_holocaust0_type = manipulate_holucaust_df(df_holocaust0, statzone)
    percentage_change = 100 * (df_holocaust1_type['Amount of Holocaust Survivors'] - df_holocaust0_type[
        'Amount of Holocaust Survivors']) / \
                        df_holocaust0_type['Amount of Holocaust Survivors']

    fig2 = px.bar(df_holocaust1_type, x=df_holocaust1_type.index, y=df_holocaust1_type['Amount of Holocaust Survivors'],
                  color_discrete_sequence=['#252E3F'])
    title2 = "כמות ניצולי השואה על פי הצרכים שלהם בכל שכונת הדר"[::-1] if statzone == 'All Statistical Zones' \
        else f"כמות ניצולי השואה על פי הצרכים שלהם באזור סטטיסטי {statzone_name}"[::-1]
    fig2.update_xaxes(title='סוג נזקקות'[::-1], tickangle=45)
    fig2.update_yaxes(title='כמות ניצולי השואה'[::-1])
    fig2.update_layout(title_text=title2,
                       title_x=0.5, yaxis=dict(
            titlefont_size=18,
            tickfont_size=18,
        ),
                       xaxis=dict(
                           titlefont_size=18,
                           tickfont_size=18,
                       ), xaxis_showgrid=True, yaxis_showgrid=True, template='simple_white')
    add_annotations_to_fig(fig2, fig2.data[0].x, fig2.data[0].y, percentage_change,
                           old_y=list(df_holocaust0_type['Amount of Holocaust Survivors']))
    fig2.update_layout(showlegend=False)
    max_y = max(df_holocaust1_type['Amount of Holocaust Survivors'])
    fig2.update_layout(yaxis_range=[0, max_y * 1.1])

    return fig1, fig2, text3_display


@app.callback(
    Output(component_id='primary_map_elderly', component_property='figure'),
    Input(component_id='map_definition', component_property='value')
)
def change_map(map_def):
    if map_def == 0:  # 'שינוי באחוזים מהדו"ח הקודם'
        percentage_change = 100 * ((seniors1_per_zone.tmp_col - seniors0_per_zone.tmp_col) / seniors0_per_zone.tmp_col)
        values_for_heatmap = {statzone_code: perc_change for statzone_code, perc_change in
                              zip(stat_zones_names_dict.keys(), percentage_change)}

        map_fig = get_choroplethmap_fig(values_dict={k: int(v) for k, v in values_for_heatmap.items()},
                                        map_title="% of change in seniors amount",
                                        colorscale=[[0, '#561162'], [0.5, 'white'], [1, '#0B3B70']],
                                        hovertemplate='<b>StatZone</b>: %{text}' + '<br><b>Percentage of change</b>: %{customdata}%<br>')
        map_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return map_fig
    else:  # 'הצג ערך נוכחי'
        values_for_heatmap = {statzone_code: perc_change for statzone_code, perc_change in
                              zip(stat_zones_names_dict.keys(), seniors1_per_zone.tmp_col)}
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
            children=[html.H4(['.בעמוד הנוכחי תוכלו לראות מגוון נתונים בנושא האוכלוסיה המבוגרת בהדר'],
                              style={'text-align': 'right', 'text-transform': 'none', 'font-family': 'sans-serif',
                                     'letter-spacing': '0em'}, ),
                      html.H4([
                          'ניתן לבחור ולראות מפה המציגה את הערכים הנוכחיים של כמות האוכלוסיה המבוגרת בכל אזור סטטיסטי, וכן מפה המראה את השינויים בין התקופות השונות. בהמשך מוצגים גרפים אשר מציגים מידע נוסף על אוכלוסיה זו, וניתן לבחור להציג בהם מידע רק על אזור סטטיסטי מסוים. תצוגה ראשונית מדגישה את כמות ניצולי השואה (עבור הדר כולה או עבור האזור הנבחר). בנוסף, מוצגים 2 גרפים המציגים את מצב האזרחים המבוגרים והנזקקות שלהם- גרף המפרט מה סוג הנזקקות של המבוגרים באזור ואת השינוי בין התקופות השונות וגרף המפרט מי מהקששים מקבל מזון ומי בודד (במעבר על גרף העוגה ניתן לראות גם את הערכים עצמם ולא רק אחוזים)']
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
                                                                value=0),
                        ],
                        className="mini_container",
                    ),
                    html.Div([
                        dcc.Graph(id='primary_map_elderly')
                    ], className="map_container"),
                ],
                className="row_rapper",
            )], className='pretty_container'),
        html.Div(
            children=[
                html.H4(
                    [": כמות ניצולי השואה (עבור האזור הנבחר)"], style={'text-align': 'right', },
                    className="container_title",
                ),
                dcc.Loading(
                    dcc.Graph(
                        id="num_holocaust_survivors",
                        figure=blank_fig(150),
                        config={"displayModeBar": False},
                    ),
                    className="svg-container",
                    style={"height": 150},
                ),
            ],
            className="pretty_container",
        ),

        html.Div([
            html.Div(
                [dcc.Graph(id='seniors_type')],
                className='narrow_container',
            ),
            html.Div(
                [dcc.Graph(id='needed_help_type')],
                className='narrow_container', ),
        ]),
    ],
    style={"text-align": "justify"},
)
