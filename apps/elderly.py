from choroplethmapbox import get_choroplethmap_fig
from app_def import app
from pre_process import *

# TODO make sure to change survival >> Holocaust Survivors
# TODO Gal don't forget to update the .zip through colab

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


def blank_fig(height):
    """
    Build blank figure with the requested height
    """
    return {
        "data": [],
        "layout": {
            "height": height,
            # "template": template,
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
        },
    }


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

# Calculate % change in total amount of seniors from time t0 to t1
seniors0, seniors1 = dfs_dict['df_seniors_t0'], dfs_dict['df_seniors_t1']

# percentage change in % units from time0 to time1
seniors1_per_zone = seniors1.groupby(by=["StatZone"]).count()[['Street']]
seniors0_per_zone = seniors0.groupby(by=["StatZone"]).count()[['Street']]

percentage_change = 100 * ((seniors1_per_zone.Street - seniors0_per_zone.Street) / seniors0_per_zone.Street)
values_for_heatmap = {statzone_code: perc_change for statzone_code, perc_change in
                      zip(stat_zones_names_dict.keys(), percentage_change)}

map_fig = get_choroplethmap_fig(values_dict={k: int(v) for k, v in values_for_heatmap.items()},
                                map_title="% of change in seniors amount",
                                colorscale=[[0, '#561162'], [0.5, 'white'], [1, '#0B3B70']],
                                hovertemplate='<b>StatZone</b>: %{text}' + '<br><b>Precentage of change</b>: %{z}%<br>')
map_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})


@app.callback(
    Output(component_id='seniors_type', component_property='figure'),
    Output(component_id='needed_help_type', component_property='figure'),
    Output(component_id='num_holocaust_survival', component_property='value'),
    Input(component_id='areas', component_property='value')
)
def get_graphs(statzone):
    df_seniors1 = dfs_dict['df_seniors_t1']

    if statzone == 0:
        statzone = 'All Statistical zones'

    if statzone != 'All Statistical zones':
        df_seniors1 = df_seniors1[df_seniors1['StatZone'] == statzone]

    food1_alone1 = len(df_seniors1[(df_seniors1['SeniorAlone'] == 1) &
                                   (df_seniors1['SeniorRecivFood'] == 1)])
    food1_alone0 = len(df_seniors1[(df_seniors1['SeniorAlone'] == 0) &
                                   (df_seniors1['SeniorRecivFood'] == 1)])
    food0_alone1 = len(df_seniors1[(df_seniors1['SeniorAlone'] == 1) &
                                   (df_seniors1['SeniorRecivFood'] == 0)])
    food0_alone0 = len(df_seniors1[(df_seniors1['SeniorAlone'] == 0) &
                                   (df_seniors1['SeniorRecivFood'] == 0)])
    pie_df = {'status': ['Recieve Food & Alone', 'Recieve Food', 'Alone', 'Else'],
              'amount': [food1_alone1, food1_alone0, food0_alone1, food0_alone0]}

    fig1 = px.pie(pie_df, values='amount', names='status', title='Status of seniors citizens')

    string = " stat zone " if statzone != 'All Statistical zones' else " "

    # TODO this title is not visible because of the margin 0, add a title to the html
    fig1.update_layout(title_text=f"Status of seniors citizens in{string}{statzone}",
                       yaxis=dict(
                           titlefont_size=18,
                           # tickfont_size=18,
                       ),
                       xaxis=dict(
                           titlefont_size=18,
                           # tickfont_size=18,
                           # tickvals=[i for i in range(13)],
                           # ticktext=[i for i in range(13)]
                       ),  # xaxis_showgrid=True, yaxis_showgrid=True,
                       template='none',
                       )
    # yaxis_range=[0, max_y * 1.1])

    df_holocaust1 = dfs_dict['df_holocaust_t1']
    df_holocaust1["HoloSurvNdDesc"].dropna()
    df_holocaust1 = df_holocaust1.replace(
        {'בעיות הנובעות ממחלות אקוטיות או כרוניות (למעט בריאות הנפש)': 'מחלות אקוטיות או כרוניות',
         'בעיות הנובעות מרמת הכנסה נמוכה או מירידה ברמת הכנסה': 'רמת הכנסה נמוכה',
         'בעיות הנובעות ממומים ו/או מגבלות פיזיות (נכות)': 'נכות',
         'בעיות בתקשורת בקליטה (עלייה)': 'בעיות בתקשורת וקליטה'})
    df_holocaust1["HoloSurvNdDesc"] = df_holocaust1["HoloSurvNdDesc"].apply(
        lambda x: str(x)[:-1] + '(' if str(x)[-1] == ')' else x)
    if statzone == 'All Statistical zones':
        df_holocaust1_type = df_holocaust1.groupby(by=["HoloSurvNdDesc"]).count()[['Street']]
        df_holocaust1_type = df_holocaust1_type.sort_values(by=['Street'], ascending=False).head(5)
    else:
        df_holocaust1_type = df_holocaust1.groupby(by=["StatZone", "HoloSurvNdDesc"]).count()[['Street']]
        df_holocaust1_type = df_holocaust1_type.loc[statzone].sort_values(by=['Street'], ascending=False).head(5)

    df_holocaust1_type.index = [s[::-1].strip(' ') for s in df_holocaust1_type.index]
    df_holocaust1_type.rename(columns={'Street': 'Amount of Holocaust Survivals'}, inplace=True)

    fig2 = px.bar(df_holocaust1_type, x=df_holocaust1_type.index, y=df_holocaust1_type['Amount of Holocaust Survivals'],
                  color_discrete_sequence=['#252E3F'])
    # for_title = "crimes per location" if graph_type == "CrimeLocType" else "crimes per type"
    fig2.update_layout(title_text=f"Amount of holocaust survivals per needed help <br> type in{string}{statzone}",
                       title_x=0.5, yaxis=dict(
            titlefont_size=14,
            tickfont_size=14,
        ),
                       xaxis=dict(
                           titlefont_size=14,
                           tickfont_size=14,
                       ), xaxis_showgrid=True, yaxis_showgrid=True, template='simple_white')
    fig2.update_xaxes(title='Needed help type', tickangle=45)

    if statzone == 'All Statistical zones':
        text3 = len(df_holocaust1)
    else:
        text3 = len(df_holocaust1[df_holocaust1['StatZone'] == statzone])

    return fig1, fig2, text3


layout = html.Div(
    children=[
        html.H4(children='Choose the wanted area to see the graphs changes',  # TODO adjust title?
                style={'text-align': 'left', 'text-transform': 'none', 'font-family': 'sans-serif',
                       'letter-spacing': '0em'}
                ),
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
            id="info-container1",
            className="row container-display",
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='seniors_type')
                    ],
                    className='narrow_container',
                ),
                html.Div(
                    [
                        dcc.Graph(id='needed_help_type')
                    ],
                    className='narrow_container',
                ),
            ],
            id="info-container2",
            className="row container-display",
        ),
        # html.Div(id='num_holocaust_survival'),

        html.Div(
            [
                dcc.Graph(
                    id="num_holocaust_survival",
                    figure=blank_fig(150),
                    config={"displayModeBar": False},
                ),
            ],
            className='narrow_container',
        ),
    ],
    className="pretty_container twelve columns",
    style={"text-align": "justify"},
)
