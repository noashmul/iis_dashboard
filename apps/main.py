from pre_process import *
from choroplethmapbox import get_main_tab_map
import dash_html_components as html
import dash_core_components as dcc


def generate_table(dataframe, max_rows=10):
    val = ['table-light', 'table-primary'] * 10
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col, scope="col", className="table-dark") for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Th(dataframe.iloc[i][col], scope="row", className=val[i]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ], className="table table-hover")


df = create_df_main_dash(dfs_dict)


# \U000025B2 and \U000025BC are up and down arrows, \U0001F534 and \U0001F7E2 are red and green circles
def annotate_table(x):
    if x == 0:
        return "\U000025A0" + "\U000026AA " + "\U00002800" + str(x) + "%"
    return "\U000025BC" + "\U0001F534" + "   " + str(x) + "%" if x < 0 \
        else "\U000025B2" + "\U0001F7E2 "  + "+" + str(x) + "%"


df['Percent change from last report'] = df['Percent_comparison'].apply(lambda x: annotate_table(x))

df = df.drop('Percent_comparison', axis=1)

layout = html.Div(
    children=[
        html.Div(children=[
            html.H2(children='Welcome to our dashboard',
                    style={'text-align': 'center', 'text-transform': 'none', 'font-family': 'sans-serif',
                           'letter-spacing': '0em'}),
            html.H4(children='Above are different tabs, a tab for each subject.',
                    style={'text-align': 'left', 'text-transform': 'none', 'font-family': 'sans-serif',
                           'letter-spacing': '0em'}),
            html.H4(
                children='This dashboard is interactive - make sure to hover / choose / click on the visualizations. In the next tabs, choosing stat zone will change the charts accordingly.',
                style={'text-align': 'left', 'text-transform': 'none', 'font-family': 'sans-serif',
                       'letter-spacing': '0em'}),
            html.H5(children='*The report presents data from July 2020 to December 2020, and changes from the previous report (from January 2020 to June 2020).',
                    style={'text-align': 'left', 'text-transform': 'none', 'font-family': 'sans-serif',
                           'letter-spacing': '0em'}
                    )
        ], className="pretty_container"),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(figure=get_main_tab_map(show_text=True))
                    ],
                    className='main_map_container',),
            ], className="pretty_container"),
        html.Div([
                    html.H4(children='Percent change from last semi-annual report, in chosen fields.',
                    style={'text-align': 'left', 'text-transform': 'none', 'font-family': 'sans-serif',
                           'letter-spacing': '0em'}),
                    generate_table(df),
                  ], className="pretty_container")
    ],
    # className="pretty_container twelve columns",
    # id="cross-filter-options",
    style={"text-align": "justify"},
)
