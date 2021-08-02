import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# must add this line in order for the app to be deployed successfully on Heroku
from app_def import server
from app_def import app
# import all pages in the app
from apps import main, safety, crime

app.layout = html.Div(
    [html.H1('Hadar Neighborhood: Semi-annual report',
             style={'color': '#FFFFFF', 'text-align': 'left', 'text-transform': None}),
     html.Div([
         dcc.Location(id="url"),
         dbc.NavbarSimple(
             children=[
                 dbc.NavLink("main", href="/main", active="exact"),
                 dbc.NavLink("Safety", href="/safety", active="exact"),
                 dbc.NavLink("Crime", href="/crime", active="exact")
             ],
             brand="Choose the wanted tab",
             color="primary",
             dark=True,
             style={'font-size': 15}
         ),
         dbc.Container(id="page-content", className="pt-4"),
     ]
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
    else:
        return main.layout


if __name__ == '__main__':
    app.run_server(debug=True)
