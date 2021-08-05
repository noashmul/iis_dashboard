from pre_process import *
from choroplethmapbox import get_main_tab_map
import dash_html_components as html
import dash_core_components as dcc


def generate_table(dataframe, max_rows=10):
    val = ['table-light', 'table-primary'] * 10
    return html.Table([
        html.Thead(
            html.Tr(
                [html.Th(col, scope="col", className="table-dark", dir='rtl', style={'font-size': '17px'}) for col in
                 dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Th(dataframe.iloc[i][col], scope="row", className=val[i], dir='rtl', style={'font-size': '14px'})
                for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ], className="table table-hover")


# \U000025B2 and \U000025BC are up and down arrows, \U0001F534 and \U0001F7E2 are red and green circles
def annotate_table(x):
    if x == 0:
        return "\U000026AA" + "\U000025A0" + str(x) + "%" + "\U00002800"
    return "\U0001F534" + "\U000025BC" + str(x)[1:] + "%" + "-" if x < 0 \
        else "\U0001F7E2" + "\U000025B2" + str(x) + "%" + "+"


df = create_df_main_dash(dfs_dict)
df['אחוז שינוי מהדו"ח הקודם'] = df['אחוז שינוי מהדו"ח הקודם'].apply(lambda x: annotate_table(x))
df = df[['אחוז שינוי מהדו"ח הקודם', 'ערך', 'תיאור', 'נושא']]

layout = html.Div(
    children=[
        html.Div(children=[
            html.H2(children='!ברוכים הבאים',
                    style={'text-align': 'center', 'text-transform': 'none', 'font-family': 'sans-serif',
                           'letter-spacing': '0em', 'text-decoration': 'double'}),
            html.H4(children='.לפניכם כרטיסיות שונות, אחת לכל נושא',
                    style={'text-align': 'right', 'text-transform': 'none', 'font-family': 'sans-serif',
                           'letter-spacing': '0em'}),
            html.H4(
                children='הדשבורד הוא אינטראקטיבי - נסו לרחף/לבחור/להקליק על הויזואליזציות השונות. בכרטיסיות השונות, בחירת אזור סטטיסטי תשנה את הגרפים בהתאם',
                style={'text-align': 'right', 'text-transform': 'none', 'font-family': 'sans-serif',
                       'letter-spacing': '0em'}),
            html.H5(
                children='.הדו"ח מציג נתונים עבור יולי 2020 - דצמבר 2020, ושינויים מהדו"ח הקודם שהוא עבור ינואר 2020 - יוני 2020*',
                style={'text-align': 'right', 'text-transform': 'none', 'font-family': 'sans-serif',
                       'letter-spacing': '0em'}
            )
        ], className="pretty_container"),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(figure=get_main_tab_map(show_text=True))
                    ],
                    className='main_map_container', ),
            ], className="pretty_container"),
        html.Div([
            html.H4(children=':אחוז שינוי מהדו"ח הקודם, במספר תחומים',
                    style={'text-align': 'right', 'text-transform': 'none', 'font-family': 'sans-serif',
                           'letter-spacing': '0em', 'font-size': '20px'}),
            generate_table(df),
        ], className="pretty_container")
    ],
    style={"text-align": "justify"},
)
