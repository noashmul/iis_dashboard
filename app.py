import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# must add this line in order for the app to be deployed successfully on Heroku
from app_def import app
# import all pages in the app
from apps import main, safety, crime, income, elderly, population

app.layout = html.Div(
    [dbc.Row(
        [
            html.H1('-', style={'color': '#252e3f'}),
            html.Img(src="/assets/city.png", height="30px"),
            html.H1('-', style={'color': '#252e3f'}),
            html.H1('Hadar Neighborhood: Semi-annual report',
                    style={'color': '#FFFFFF', 'text-transform': 'none'}, ),
        ],
        align="left",
    ),
        html.Div([
            dcc.Location(id="url"),

            dbc.NavbarSimple(
                children=[
                    dbc.Container(
                        [
                            dbc.NavLink("Main", href="/main"),
                            dbc.NavLink("Safety", href="/safety"),
                            dbc.NavLink("Crime", href="/crime"),
                            dbc.NavLink("Income", href="/income"),
                            dbc.NavLink("Elderly", href="/elderly"),
                            dbc.NavLink("Population", href="/population"),
                        ])],
                brand="Choose the wanted tab",
                color="primary",
                dark=True,
                style={'font-size': 15},
            ),

            dbc.Container(fluid=False,
                          id="page-content", className="pt-4"),
        ],
        )])


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
    else:
        return main.layout


if __name__ == '__main__':
    app.run_server(debug=True)
