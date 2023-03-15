from functools import wraps
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from flask import session
from Datos.db import usuario


def authenticate_user(credentials):
    '''
    generic authentication function
    returns True if user is correct and False otherwise
    '''
    users = usuario()

    if not (credentials['user'] in users['usuario'].values):
        return [False, None]
    authed = (credentials['user'] in users['usuario'].values) and (credentials['password'] == (users.loc[users['usuario'] == credentials['user'], 'contraseña'].values[0]))
    info = users.loc[users['usuario'] == credentials['user']][['nombre', 'usuario', 'doc_id', 'rol_usuario', 'pais']]
    if not info.empty:
        info.reset_index(drop = True, inplace = True)
    return [authed, info]


def validate_login_session(f):
    '''
    takes a layout function that returns layout objects
    checks if the user is logged in or not through the session.
    If not, returns an error with link to the login page
    '''
    @wraps(f)
    def wrapper(*args,**kwargs):
        if session.get('authed',None)==True:
            return f(*args,**kwargs)
        return html.Div(
            dbc.Row(
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.H2('401 - No Autorizado',className='card-title'),
                                html.A(dcc.Link('Iniciar sesión',href='/login'))
                            ],
                            body=True
                        )
                    ],
                    width=5
                ),
                justify='center'
            )
        )
    return wrapper
