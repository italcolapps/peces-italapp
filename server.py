import dash
import dash_bootstrap_components as dbc
import os

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags = [{'name': 'viewport',
                  'content': 'width = device-width, initial-scale = 1.0, maximun-scale = 1.2, minimun-scale = 0.5'}]
)

app.config.suppress_callback_exceptions = True
app.title = 'italApp Peces'

server = app.server
server.config['SECRET_KEY'] = 'k1LUZ1fZS-lkjhjg8768UIEJkJvS8RBF6MMgmNcDGNmgGYr' # i know this should not be in version control...
port = int(os.environ.get("PORT", 5000))
