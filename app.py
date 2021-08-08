import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# must add this line in order for the app to be deployed successfully on Heroku
from app_def import app
# import all pages in the app
from apps import main, safety, crime, income, elderly, population, safety_immersive, weights

server = app.server
app.config.suppress_callback_exceptions = True

app.layout = html.Div(
    [
        html.Div([
            html.Img(src='../assets/city.png', height='60px', alt='logo', style={'float': 'right'}),
            html.H1('שכונת הדר: דו"ח חצי שנתי',
                    style={'color': '#FFFFFF', 'text-transform': 'none', 'align-items': 'center',
                           'text-align': 'center', 'font-size': '60px', 'position': 'relative'}),
        ]),

        html.Div([
            dcc.Location(id="url"),
            dbc.NavbarSimple(
                children=[
                    dbc.Container(
                        [
                            dbc.NavLink("משקולות ביטחון", href="/weights"),
                            dbc.NavLink("ביטחון - מסך אימרסיבי   ||", href="/safety_immersive"),
                            dbc.NavLink("קשישים", href="/elderly"),
                            dbc.NavLink("הכנסה", href="/income"),
                            dbc.NavLink("דמוגרפיה", href="/population"),
                            dbc.NavLink("פשיעה", href="/crime"),
                            dbc.NavLink("ביטחון", href="/safety"),
                            dbc.NavLink("ראשי", href="/main"),

                        ])],
                color="primary",
                dark=True,
                style={'font-size': 15},
            ),

            dbc.Container(fluid=True,
                          id="page-content", className="pt-4"),
        ],
        ),
        dcc.Interval(
            id='interval-component',
            interval=1 * 1000,  # in milliseconds
            n_intervals=0
        )
    ]
)


def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/main':
        return main.layout
    elif pathname == '/safety':
        return safety.layout
    elif pathname == '/crime':
        return crime.layout
    elif pathname == '/income':
        return income.layout
    elif pathname == '/elderly':
        return elderly.layout
    elif pathname == '/population':
        return population.layout
    elif pathname == '/safety_immersive':
        return safety_immersive.layout
    elif pathname == '/weights':
        return weights.layout
    else:
        return main.layout


if __name__ == '__main__':
    app.run_server(debug=True)
