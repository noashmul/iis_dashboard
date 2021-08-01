import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from app_def import app
from choroplethmapbox import get_choroplethmap_fig
import numpy as np

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


# app = dash.Dash(__name__, )
# external_stylesheets=external_stylesheets)
# statistic_area_ = ['All', '611', '612', '613', '621', '622', '623', '631', '632', '633', '634',
#                    '641', '642', ' 643', '644']
statistic_area = {'גן הבהאים': 612,
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
    options.append({'label': key + ' ' + str(value), 'value': str(value)})

layout = html.Div([
    html.H3("Change the value to see callbacks in action!"),
    html.Div(
        id="app-container",
        children=[
            html.Div(className='narrow_container', children=[
            html.Div(id="left-column",className="pretty_container", children=[
                html.Div(className="slider-container",
                         children=[
                             html.P(id="slider-text1", children="Choose the wanted weight 1:", style={'color': 'black'},
                                    ),
                             dcc.Slider(id="Weight 1", min=0.0, max=1.0, value=0.5, step=None,
                                        marks={str(num): {"label": str(num), "style": {"color": "#7fafdf"}, }
                                               for num in [0, 0.25, 0.5, 0.75, 1]
                                               }),
                             html.P(id="slider-text2", children="Choose the wanted weight 2:", style={'color': 'black'},
                                    ),
                             dcc.Slider(id="Weight 2", min=0.0, max=1.0, value=0.5, step=None,
                                        marks={str(num): {"label": str(num), "style": {"color": "#7fafdf"}, }
                                               for num in [0, 0.25, 0.5, 0.75, 1]
                                               }),
                         ]),
                html.Div(className="mini_container",
                         children=[
                             html.Div(
                                 [
                                 'Choose area: ', dcc.RadioItems(id='areas',
                                                                 options=options,
                                                                 value='MTL'
                                                                 ),
                                 # html.Br(),
                                 # dcc.Graph(id='graph_with_slider'),
                                 # dcc.Graph(id='graph_with_slider2')

                             ])])
            ])]),
            html.Div(className='narrow_container', children=[
            html.Div(
                id="graph-container",
                children=[
                    # html.P(id="chart-selector", children="Select chart:"),
                    dcc.Graph(id='graph_with_slider')
                ])
        ])])])


@app.callback(
    Output(component_id='graph_with_slider', component_property='figure'),
    # Output(component_id='graph_with_slider2', component_property='figure'),
    Input(component_id='Weight 1', component_property='value'),
    Input(component_id='Weight 2', component_property='value'),
    Input(component_id='areas', component_property='value')
)
def update_output_div(w1, w2, area):
    """
    create all the graphs that rely on the input values (weights and area)
    :param w1: weight value
    :param w2: weight value
    :param area: statistic ares (or 'All')
    :return: all wanted figures
    """
    # fig = px.scatter(x=[w1], y=
    values_dict = dict.fromkeys([611, 612, 613, 621, 622, 623, 631, 632, 633, 634, 641, 642, 643, 644], 0.)

    for key in values_dict.keys():
        values_dict[key] = np.random.randn()

    fig = get_choroplethmap_fig(values_dict=values_dict, map_title="Exmple Title")
    return fig

# if __name__ == '__main__':
#     app.run_server(debug=True)
