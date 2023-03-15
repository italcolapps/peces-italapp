# package imports
import dash 
from dash import exceptions
import dash_bootstrap_components as dbc
from dash_core_components.Store import Store
import dash_html_components as html
import dash_core_components as dcc
#from dash_extensions import Download
from dash.dependencies import Input, Output, State
from dash import no_update
import dash_table
from flask import session, copy_current_request_context
from datetime import datetime, timedelta
from numpy import empty
import pandas as pd
from time import sleep
import os
import base64
from dash_extensions import Download
from random import randint
import json

from pandas._config.config import reset_option

# local imports
from auth import authenticate_user, validate_login_session
from server import app, server, port
from Datos.db import get_data, change_pw, crear_gerente, crear_usuario, crear_cliente, cerrar_lote_, ifExist, trazabilidad
from Datos.insert_dataframe import insert_dataframe
from logo import logo_encoded
from Tablas import render_table
from utils import *
from campos import *
 

# login layout content
def login_layout():
    return html.Div(
        [
            dcc.Location(id='login-url',pathname='/login',refresh=False),
            dbc.Container([
                html.Br(),
                html.Center(
                    dbc.Row(
                        dbc.Col([
                            html.Img(src='data:image/png;base64,{}'.format(logo_encoded.decode()),
                                    style={'max-width': '100%', 'height': 'auto'})
                        ], xl=12, lg=12, md=12, sm=12, xs=12)
                )),
                dbc.Row(
                    dbc.Col([
                        html.Br(),
                        dbc.Card([
                            html.Center(
                                html.H4('Seguimiento de estanques',className='card-title'),),
                            dbc.Input(id='login-email',placeholder='Nombre de usuario'),
                            html.Br(),
                            dbc.Input(id='login-password',placeholder='Contraseña',type='password'),
                            html.Br(),
                            dbc.Button('Iniciar sesión',id='login-button',color='primary',block=True),
                            html.Br(),
                            dcc.Store(id = 'user_info', storage_type = 'session'),
                            dbc.Spinner(html.Div(id='login-alert'))
                            ], body=True
                            )
                        ], xl = 6, lg = 5, md = 8, sm = 10, xs = 10), justify='center'
                    )
                ]
            )
        ]
    )

# cuerpo de la app con ingreso exitoso
@validate_login_session
def app_layout():
    return \
        html.Div([
            dcc.Location(id='home-url',pathname='/home'),
            dbc.Container([
                dcc.ConfirmDialog(
                    id='confirm',
                    message='¿Enviar Información Ingresada?'),
                dcc.ConfirmDialog(
                    id='confirm_pw',
                    message='¿Desea cambiar la contraseña? Esta acción no se puede revertir.'),
                dcc.ConfirmDialog(
                    id='confirm_crear_gerente',
                    message='¿Desea crear un gerente nuevo?'),
                dcc.ConfirmDialog(
                    id='confirm_crear_cliente_ng',
                    message='¿Desea crear un cliente nuevo?'),                    
                dcc.ConfirmDialog(
                    id='confirm_crear_granja_no_cliente',
                    message='¿Desea crear una granja nueva?'),
                dcc.ConfirmDialog(
                    id='confirm_agregar_galpon_nc',
                    message='¿Desea agregar un galpón nuevo?'),
                dcc.ConfirmDialog(
                    id='confirm_crear_especialista',
                    message='¿Desea crear un especialista nuevo?'), 
# 
        
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.Center(
                        html.Img(src='data:image/png;base64,{}'.format(logo_encoded.decode()),
                                    style = {'max-width': '100%', 'height': 'auto'})                        
                    ),
                    ], xl = 12, lg = 12, md = 12, sm = 12, xs = 12,),
            ], align='center', no_gutters = True),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Button('Salir',id='logout-button',color='primary',block=True,size='sm',
                                style = {'color': 'white', 'border-color': 'white'})
                    ], xl = 2, lg = 2, md = 4, sm = 4, xs = 4)                
            ], justify="end"),
            dcc.Store(id = 'user_info', storage_type = 'session'),
            html.Div(children = [dbc.Input(id = 'fake_input')], style = {'display': 'none'}),
            html.Br(),
            titulo(texto = '-', id_ = 'test'),

            dbc.Tabs(children = [
                dbc.Tab(label = 'Gerentes de zona', id = 'gerentes_zona', tab_id = 'tab_gerentes_zona'),
                dbc.Tab(label = 'Especialistas', id = 'especialistas', tab_id = 'tab_especialistas'),
                dbc.Tab(label = 'Clientes', id = 'clientes', tab_id = 'tab_clientes'),
                dbc.Tab(label = 'Administrar granjas', id = 'administrar_granjas', tab_id = 'tab_administrar_granjas'),
                dbc.Tab(label = 'Ingreso de información', id = 'ingreso_datos', tab_id = 'tab_ingreso_datos'),
                dbc.Tab(label = 'Consultar información', id = 'consultar_informacion', tab_id = 'tab_consultar_informacion'),
                dbc.Tab(label = 'Configuración', id = 'configuracion', tab_id = 'tab_configuracion')
                #dbc.Tab(label = 'Gestión de usuarios', tab_id = 'gestion_usuarios'),
                ], id = 'tabs'),
            html.Div(id = 'contenido')
            ],

            )
        ]
    )


# main app layout
app.layout = html.Div(
    [
        dcc.Location(id='url',refresh=False),
        html.Div(
            login_layout(),
            id='page-content'
        ),
    ]
)


###############################################################################
# utilities
###############################################################################
# router
@app.callback(
    Output('page-content','children'),
    [Input('url','pathname')]
)
def router(url):
    if url=='/home':
        return app_layout()
    elif url=='/login':
        return login_layout()
    else:
        return login_layout()

# authenticate
@app.callback(
    [Output('url','pathname'),
     Output('login-alert','children'),
     Output('user_info', 'data')],
    [Input('login-button','n_clicks')],
    [State('login-email','value'),
     State('login-password','value')])
def login_auth(n_clicks,email,pw):
    '''
    check credentials
    if correct, authenticate the session
    otherwise, authenticate the session and send user to login
    '''
    if n_clicks is None or n_clicks==0:
        return no_update,no_update, no_update
    credentials = {'user':email,"password":pw}
    user = authenticate_user(credentials)
    if user[0]:
        session['authed'] = True
        usuario = user[1].to_json(date_format = 'iso', orient = 'split')
        try:
            fecha = datetime.today().date()
            trazabilidad(user[1]['doc_id'][0], user[1]['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Inicio de sesión')
            print(user[1]['doc_id'][0], user[1]['rol_usuario'][0],)
        except Exception as e:
            print(e)
        return ['/home','', usuario]
    session['authed'] = False
    return [no_update, dbc.Alert('Usuario o contraseña incorrectas.',color='danger',dismissable=True), no_update]

@app.callback(
    Output('home-url','pathname'),
    [Input('logout-button','n_clicks')],
    State('user_info', 'data'))
def logout_(n_clicks, data):
    '''clear the session and send user to login'''
    if n_clicks is None or n_clicks==0:
        raise dash.exceptions.PreventUpdate()
        return no_update, no_update
    session['authed'] = False
    return '/login', None

###############################################################################
# callbacks
###############################################################################
## confirm p1
@app.callback([Output('confirm', 'displayed')],
              [Input('enviar_p1', 'n_clicks')])
def display_confirm(value):
    if value:
        return [True]
    else:
        return [False]

## confirm cambio_pw
@app.callback([Output('confirm_pw', 'displayed')],
              [Input('cambiar_pw', 'n_clicks')])
def display_confirm(value):
    if value:
        return [True]
    else:
        return [False]

## confirm crear_gerente
@app.callback([Output('confirm_crear_gerente', 'displayed')],
              [Input('crear_gerente', 'n_clicks')])
def display_confirm(value):
    if value:
        return [True]
    else:
        return [False]

## confirm crear_especialista
@app.callback([Output('confirm_crear_especialista', 'displayed')],
              [Input('crear_especialista', 'n_clicks')])
def display_confirm(value):
    if value:
        return [True]
    else:
        return [False]

## confirm crear_cliente
@app.callback([Output('confirm_crear_cliente_ng', 'displayed')],
              [Input('crear_cliente_ng', 'n_clicks')])
def display_confirm(value):
    if value:
        return [True]
    else:
        return [False]


## confirm crear_granja no cliente
@app.callback([Output('confirm_crear_granja_no_cliente', 'displayed')],
              [Input('crear_granja_no_cliente', 'n_clicks')])
def display_confirm(value):
    if value:
        return [True]
    else:
        return [False]

## confirm agregar galpon no cliente
@app.callback([Output('confirm_agregar_galpon_nc', 'displayed')],
              [Input('agregar_galpon_nc', 'n_clicks')])
def display_confirm(value):
    if value:
        return [True]
    else:
        return [False]


### callback inicial en funcion del rol del usuario
@app.callback([Output('test', 'children'),
               Output('ingreso_datos', 'disabled'),
               Output('ingreso_datos', 'tab_style')],
              Input('fake_input', 'value'),
              State('user_info', 'data'))
def nombre(n, data):
    usuario = pd.read_json(data, orient = 'split')
    if usuario['rol_usuario'].values[0] == 'administrador':
        return [f'Bienvenido {usuario["nombre"].values[0]}',
                False, no_update] #{'display': 'none'}
    else:
        return [f'Bienvenido {usuario["nombre"].values[0]}',
        no_update, no_update]


### ocultar pestaña gerentes
@app.callback([Output('gerentes_zona', 'disabled'),
               Output('gerentes_zona', 'tab_style')],
              Input('fake_input', 'value'),
              State('user_info', 'data'))
def gerenteszona(value, data):
    usuario = pd.read_json(data, orient = 'split')
    if usuario['rol_usuario'].values[0] in ['gerente', 'cliente']:
        return [True, {'display': 'none'}]
    return [no_update, no_update]

### ocultar pestaña especialistas
@app.callback([Output('especialistas', 'disabled'),
               Output('especialistas', 'tab_style')],
              Input('fake_input', 'value'),
              State('user_info', 'data'))
def especialistas(value, data):
    usuario = pd.read_json(data, orient = 'split')
    if usuario['rol_usuario'].values[0] in ['especialista', 'cliente', 'gerente']:
        return [True, {'display': 'none'}]
    return [no_update, no_update]


### ocultar pestaña clientes
@app.callback([Output('clientes', 'disabled'),
               Output('clientes', 'tab_style')],
              Input('fake_input', 'value'),
              State('user_info', 'data'))
def gerenteszona(value, data):
    usuario = pd.read_json(data, orient = 'split')
    if usuario['rol_usuario'].values[0] in ['cliente']:
        return [True, {'display': 'none'}]
    return [no_update, no_update]   

# callback pestaña inicial
@app.callback(Output('tabs', 'active_tab'),
              Input('fake_input', 'value'),
              State('user_info', 'data'))
def active_tab(value, data):
    usuario = pd.read_json(data, orient = 'split')
    if usuario['rol_usuario'].values[0] in ['administrador']:
        return 'tab_gerentes_zona' 
    elif usuario['rol_usuario'].values[0] in ['gerente', 'especialista']:
        return 'tab_clientes'
    elif usuario['rol_usuario'].values[0] == 'cliente':
        return 'tab_ingreso_datos'
    else:
        return no_update

### calback contenido cambio de pestaña 
@app.callback(Output('contenido', 'children'),
              Input('tabs', 'active_tab'),
              State('user_info', 'data'))
def contenido(active_tab, data):
    usuario = pd.read_json(data, orient = 'split')
    rol = usuario['rol_usuario'].values[0]
    user = usuario['nombre'].values[0]
    doc_id = usuario['doc_id'].values[0]
    pais = usuario['pais'].values[0]
    
    if active_tab == 'tab_ingreso_datos':
        if rol == 'administrador':
            try:
                gerentes = get_data('SELECT documento_identidad, nombre_gerente FROM gerentes')
            except Exception as e:
                print(e)
                gerentes = pd.DataFrame({'documento_identidad': [None],
                        'nombre_gerente': ['Error al consultar gerentes de zona']})                                
            if gerentes.empty:
                gerentes = pd.DataFrame({'documento_identidad': [None],
                                        'nombre_gerente': ['Sin registros']})                
            else:
                gerentes.sort_values(by = ['nombre_gerente'], inplace = True)
                gerentes.reset_index(drop = True, inplace = True)
            clientes = pd.DataFrame({'nit': [None],
                                     'nombre_cliente': ['Por favor seleccione un gerente']})
            granjas = pd.DataFrame({'id_granja': [None],
                                    'nombre_granja': ['Sin registros']})
            style_gerente = {'display': 'inline'}
            style_cliente = {'display': 'inline'}
            style_granja = {'display': 'inline'}
        if rol == 'gerente' or rol == 'especialista':
            gerentes = pd.DataFrame({'documento_identidad': [doc_id],
                                     'nombre_gerente': [user]})
            try:
                clientes = get_data(f'''SELECT nit, nombre_cliente FROM clientes WHERE gerente_zona = {doc_id};''')
            except Exception as e:
                print(e)
                clientes = pd.DataFrame({'nit': [None],
                                        'nombre_cliente': ['Error al consultar clientes']})
            if clientes.empty:
                clientes = pd.DataFrame({'nit': [None],
                                        'nombre_cliente': ['Sin registros']})
            else:
                clientes.sort_values(by = ['nombre_cliente'], inplace = True)
                clientes.reset_index(drop = True, inplace = True)
            granjas = pd.DataFrame({'id_granja': [None],
                        'nombre_granja': ['Sin registros']})
            style_gerente = {'display': 'none'}
            style_cliente = {'display': 'inline'}
            style_granja = {'display': 'inline'}
        if rol == 'cliente':
            gerentes = pd.DataFrame({'documento_identidad': [None],
                                     'nombre_gerente': ['Sin registros']})
            clientes = pd.DataFrame({'nit': [doc_id],
                                     'nombre_cliente': [user]})
            try:
                granjas = get_data(f"SELECT id_granja, nombre_granja FROM granjas WHERE nit_cliente = '{doc_id}'")
            except Exception as e:
                print(e)
                granjas = pd.DataFrame({'id_granja': [None],
                            'nombre_granja': ['Error al consultar granjas']})
            if granjas.empty:
                granjas = pd.DataFrame({'id_granja': [None],
                            'nombre_granja': ['Sin registros']})
            else:
                granjas.sort_values(by = ['nombre_granja'], inplace = True)
                granjas.reset_index(drop = True, inplace = True)
            style_gerente = {'display': 'none'}
            style_cliente = {'display': 'none'}
            style_granja = {'display': 'inline'}
        
        gerentes_opt = [{'label': gerentes['nombre_gerente'][i], 'value': gerentes['documento_identidad'][i]} for i in range(gerentes.shape[0])]
        clientes_opt = [{'label': clientes['nombre_cliente'][i], 'value': clientes['nit'][i]} for i in range(clientes.shape[0])]
        granjas_opt = [{'label': granjas['nombre_granja'][i], 'value': granjas['id_granja'][i]} for i in range(granjas.shape[0])]
        
        return [
            html.Br(),
            dbc.Row([
                dbc.Col([
                    html.H5('DATOS IDENTIFICACIÓN'),
                ])
            ]),
            html.Hr(),
            dbc.Row([
                campos(id_ = 'gerente_ingreso', label = 'GERENTE DE ZONA', ayuda = '-',
                        tipo = 'seleccion', style_col = style_gerente,
                        valor = gerentes_opt, vl = doc_id if rol == 'gerente' else None,
                        xl = 3, lg = 3, md = 4, sm = 5, xs = 6),
                campos(id_ = 'cliente_ingreso', label = 'CLIENTE', ayuda = '-', tipo = 'seleccion',
                       valor = clientes_opt, vl = doc_id if rol == 'cliente' else None, style_col = style_cliente,
                       xl = 3, lg = 3, md = 4, sm = 5, xs = 6),
                campos(id_ = 'granja_ingreso', label = 'GRANJA', ayuda = '-', tipo = 'seleccion',
                       valor = granjas_opt, vl = None, style_col = style_granja,
                       xl = 3, lg = 3, md = 4, sm = 5, xs = 6),

            ]),
            dbc.Row([
                dbc.Col([
                    html.H5('DATOS LOTE'),
                ])
            ]),
            html.Hr(),
            dbc.Row([
                campos(id_ = 'lote_nuevo', label = '¿Lote nuevo?', ayuda = '-',
                    tipo = 'seleccion_2', xl = 2, lg = 2, md = 4, sm = 4, xs = 4,
                    valor = [{'label': 'Registrar lote', 'value': 'Si'}], vl = None),
                lote_ingreso,  estanque_ingreso, especie_ingreso, genetica_ingreso
            ]),
            dbc.Row([
                fecha_siembra_ingreso, 
                peso_siembra_ingreso, talla_ingreso,
                numero_inicial_peces_ingreso,
            ]),
            dbc.Row([
                dbc.Col([
                    html.H5('DATOS ESTANQUE'),
                ])
            ]),
            html.Hr(),
            dbc.Row([
                tipo_estanque_ingreso, area_m2_ingreso, vol_m3_ingreso,
                tipo_aireador_ingreso, aireacion_ingreso, etapa_cultivo_ingreso
            ]),
            html.Div(id = 'feeding_fields_alimentacion', children = [
                dbc.Row([
                    dbc.Col([
                        html.H5('FECHA MUESTREO'),
                    ])
                ]), 
                html.Hr(),
                dbc.Row([
                    fecha_ingreso,
                ]),
                dbc.Row([
                    dbc.Col([
                        html.H5('ALIMENTACIÓN'),
                    ])
                ]), 
                html.Hr(),
                dbc.Row([
                    campos(id_ = 'seg_alimentacion', label = 'Seg. Alimentación', ayuda = '-',
                        tipo = 'seleccion_2', xl = 2, lg = 2, md = 4, sm = 4, xs = 4,
                        valor = [{'label': 'Registrar', 'value': 'Si'}], vl = ['No']),                    
                ]),
                html.Div(id = 'feeding_fields_2', children = [
        
                    dbc.Row([
                        #dias_ultima_fecha, alimento_ultima_fecha, 
                        dbc.Col([
                            html.H5(id = 'dias_ultima_fecha', children = '')
                        ], xl = 4, lg = 4, md = 6, sm = 8, xs = 10),
                        dbc.Col([
                            html.H5(id = 'alimento_ultima_fecha', children = '')
                        ], xl = 4, lg = 4, md = 6, sm = 8, xs = 10),
                    ]),
                    html.Br(),
                    dbc.Row([
                        rango_fecha_alm,
                    ]),
                    html.Br(),
                    dbc.Row([
                        marca_alimento, n_fuentes_alimento, tipo_alimento_ingreso
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Div(id = 'tabla_ingreso_alimento', style = {'overflow': 'auto', 'white-space': 'nowrap'})
                        ])                
                    ]),
                ]),

                ]),
            html.Br(),
            # dbc.Row([
            #     tipo_alimento_ingreso, precio_b_ingreso, kg_real_ingreso
            # ]),
            html.Div(id = 'feeding_fields_crecimiento', children = [
                dbc.Row([
                    dbc.Col([
                        html.H5('SEGUIMIENTO AL CRECIMIENTO'),
                    ])
                ]),
                html.Hr(),
                dbc.Row([
                    campos(id_ = 'seg_crecimiento', label = 'Seg. Crecimiento', ayuda = '-',
                        tipo = 'seleccion_2', xl = 2, lg = 2, md = 4, sm = 4, xs = 4,
                        valor = [{'label': 'Registrar', 'value': 'Si'}]),
                    #fecha_muestreo_anterior, 
                    
                ]),
                dbc.Row([
                    dbc.Col(id = 'fecha_muestreo_anterior_col', children = [
                        html.H5(id = 'fecha_muestreo_anterior'),
                    ], xl = 4, lg = 6, md = 6, sm = 10, xs = 10),
                    dbc.Col(id = 'peso_prom_muestreo_anterior_col', children = [
                        html.H5(id = 'peso_prom_muestreo_anterior'),
                    ], xl = 4, lg = 6, md = 6, sm = 10, xs = 10)
                ]),
                html.Br(),

                dbc.Row([
                    rango_fecha_cre, real_ingreso, longitud_crecimiento
                ]),
            ]),
            html.Div(id = 'feeding_fields_inventario', children = [
                dbc.Row([
                    dbc.Col([
                        html.H5('INVENTARIO DEL ESTANQUE'),
                    ])
                ]),
                html.Hr(),
                dbc.Row([
                    campos(id_ = 'mortalidad', label = 'Mortalidad', ayuda = '-',
                        tipo = 'seleccion_2', xl = 2, lg = 2, md = 4, sm = 4, xs = 4,
                        valor = [{'label': 'Registrar', 'value': 'Si'}]),
                        #fecha_mort_anterior,     
                ]),
                dbc.Row([
                    dbc.Col(id = 'fecha_mort_anterior_col', children = [
                        html.H5(id = 'fecha_mort_anterior')
                    ], xl = 4, lg = 6, md = 6, sm = 10, xs = 10),
                    dbc.Col(id = 'ac_mort_anterior_col', children = [
                        html.H5(id = 'ac_mort_anterior')
                    ], xl = 4, lg = 6, md = 6, sm = 10, xs = 10),
                ]),
                html.Br(),
                dbc.Row([
                    rango_fecha_mort, mortalidad_ingreso, peso_mortalidad_ingreso
                ]),
                dbc.Row([
                    campos(id_ = 'translado', label = 'Traslado', ayuda = '-',
                        tipo = 'seleccion_2', xl = 2, lg = 2, md = 4, sm = 4, xs = 4,
                        valor = [{'label': 'Registrar', 'value': 'Si'}]),
                ]),
                dbc.Row([
                    dbc.Col(id = 'fecha_tras_anterior_col', children = [
                        html.H5(id = 'fecha_tras_anterior'),
                    ]),
                    #fecha_translado_ingreso, estanque_destino_ingreso
                ]),
                html.Br(),
                dbc.Row([
                    translado_ingreso,
                    vacunacion_traslado
                ]),
                dbc.Row([
                    dbc.Col([
                        html.Div(id = 'tabla_ingreso_translado', style = {'overflow': 'auto', 'white-space': 'nowrap'})
                    ], id = 'tabla_ingreso_translado_col')                
                ]),
                #html.Br(),
                dbc.Row([
                    campos(id_ = 'Pesca', label = 'Pesca', ayuda = '-',
                        tipo = 'seleccion_2', xl = 2, lg = 2, md = 4, sm = 4, xs = 4,
                        valor = [{'label': 'Registrar', 'value': 'Si'}]),  
                    # , #fecha_pesca_ingreso, pesca_numero_ingreso
                ]),
                dbc.Row([
                    dbc.Col(id = 'fecha_pesc_anterior_col', children = [
                        html.H5(id = 'fecha_pesc_anterior')
                    ], xl = 3, lg = 3, md = 5, sm = 6, xs = 8,),
                ]),
                html.Br(),
                dbc.Row([
                    numero_pesca_ingreso,
                    campos(id_ = 'visceras_pesca', label = 'VÍSCERAS', ayuda = 'PESO O PROCENTAJE ',
                        tipo = 'seleccion_2', xl = 2, lg = 2, md = 4, sm = 4, xs = 4,
                        valor = [{'label': 'PORCENTAJE', 'value': 'porcentaje'}], vl = None)
                ]),

                dbc.Row([
                    dbc.Col([
                        html.Div(id = 'tabla_ingreso_pesca', style = {'overflow': 'auto', 'white-space': 'nowrap'})
                    ], id = 'tabla_ingreso_pesca_col')                
                ]),
            ]),########
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Button('Validar seguimiento estanque', id = 'validar_seguimiento_estanque', color = 'primary')
                ], xl = 4, lg = 4, md = 5, sm = 6, xs = 6),

                dbc.Col([
                    dbc.Spinner(dbc.Alert(id = 'alert_validar_seguimiento_estanque', dismissable=True, is_open = False))
                ], xl = 8, lg = 8, md = 8, sm = 8, xs = 8)
            ]),
            html.Br(),
            dbc.Row([
                campos(id_ = 'cerrar_lote', label = '¿Cerrar lote?', ayuda = 'Si el estanque ha terminado su ciclo',
                    tipo = 'seleccion_2', xl = 8, lg = 8, md = 8, sm = 12, xs = 12,
                    valor = [{'label': 'Cerrar', 'value': 'Si'}]),
            ]),
            html.Div([
                dbc.Modal([
                    dbc.ModalHeader('Resumen Seguimiento Estanque'),
                    dbc.ModalBody(id = 'modal_se_c', children = [
                        html.Div(id = 'div_validacion_se'),
                        html.Br(),
                        html.H4('VARIABLES CALCULADAS'),
                        html.Div(id = 'sal_tabla_calculada'),
                        html.Br(),
                        html.H4('TABLA ALIMENTACIÓN'),
                        html.Div(id = 'sal_tabla_alimentacion'),
                        html.Br(),
                        html.H4('TRASLADOS'),
                        html.Div(id = 'sal_tabla_traslados'),
                        html.Br(),
                        html.H4('PESCAS'),
                        html.Div(id = 'sal_tabla_pescas'),
                        html.Br(),
                        html.Div(id = 'var_lote_liquidado'),
                        html.Br(),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button('Enviar seguimiento', id = 'enviar_seguimiento_estanque', color = 'success')
                            ], xl = 4, lg = 4, md = 5, sm = 6, xs = 6),
                            #html.Br(),
                            dbc.Col([
                                dbc.Spinner(dbc.Alert(id = 'alert_enviar_seguimiento_estanque', dismissable=True, is_open = False))
                            ], xl = 8, lg = 8, md = 8, sm = 8, xs = 8)
                        ]),
                        html.Br(),

                    ]),
                ], id = 'modal_se', scrollable = True, is_open = False, size = 'lg'),
            ]),
            dcc.Store(id = 'data_val_se'),
            dcc.Store(id = 'data_alimentacion'),
            dcc.Store(id = 'data_traslado'),
            dcc.Store(id = 'data_pesca'),
            html.Br(), html.Br() 
        ]

    elif active_tab == 'tab_configuracion':
        return [
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Button('Cambio de contraseña', id = 'collapse_button_pw',
                                outline = True, color = 'dark')
                ], xl = 6, lg = 6, md = 6, sm = 10, xs = 10)
            ]),
            html.Hr(),
            dbc.Collapse(id = 'collapse_pw', children = [
                dbc.Row([
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.Label('Contraseña actual'),
                            dbc.Input(id = 'old_pw', type = 'password', placeholder = '******'),
                            ]),
                     ], xl = 4, lg = 4, md = 5, sm = 10, xs = 10)
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.FormGroup([
                            dbc.Label('Contraseña nueva'),
                            dbc.Input(id = 'new_pw', type = 'password', placeholder = '******'),
                            dbc.FormText('Recuerde que debe contar con al menos 8 caracteres')
                        ]),
                    ], xl = 4, lg = 4, md = 5, sm = 10, xs = 10)
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button('Cambiar', id = 'cambiar_pw', color = 'warning')
                    ], xl = 2, lg = 2, md = 3, sm = 4, xs = 4),
                    dbc.Col([
                        dbc.Spinner(dbc.Alert(id = 'alert_pw', dismissable=True, is_open = False))
                    ], xl = 8, lg = 8, md = 8, sm = 8, xs = 8)
                ]),
                html.Br(),
            ]),
            
            dbc.Row([
                html.Br(),
                dbc.Col([
                    dbc.Button('Información App', id = 'collapse_button_info_app',
                                outline = True, color = 'dark')
                ], xl = 6, lg = 6, md = 6, sm = 10, xs = 10)
            ]),
            html.Br(),
            dbc.Collapse(id = 'collapse_info_app', children = [

                dbc.Row([
                    dbc.Col([
                        html.H5('Versión 06 Agosto 2022.'),
                        html.Li('Campos linea genética ingreso y vacunación agregados.'),
                        html.Li('Ajustes en base de datos para nuevas variables.'),
                        html.Li('Ajustes varios validación ingreso.'),
                        html.Li('Base de datos seguimiento, lotes, pescas y traslados reseteada, con el fin de eliminar la información de prueba y cargar información nueva que se ajuste a los parametros de la app.')
                    ]),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H5('Versión 04 Agosto 2022.'),
                        html.Li('Corrección formulas parametros calculados.'),
                        html.Li('Implementación traslados en seguimiento semanal.'),
                        html.Li('Ajustes varios seguimiento semanal y consultar información.'),
                    ]),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H5('Versión 02 Agosto 2022.'),
                        html.Li('Corrección nombre columnas tabla consulta seguimiento estanques.'),

                    ]),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H5('Versión 01 Agosto 2022.'),
                        html.Li('Corrección calculo porcentaje mortalidad seguimiento estanques.'),
                        html.Li('Campo fecha de muestreo agregado al ingreso de datos.'),
                        html.Li('Actualización automática campos tipo aireador, aireación y ciclo de cultivo para lotes existentes.'),
                        html.Li('Gráfico alimento reporte seguimiento estanques.'),
                    ]),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H5('Versión 28 Julio 2022.'),
                        html.Li('Cambio en el orden de pestañas de la app.'),
                        html.Li('Corrección error descarga reportes excel para Especialistas.'),
                        html.Li('Corrección error validación granja para la creación de unidades productivas.'),
                        html.Li('Retirar registros duplicados de base de datos, tabla alimento, pescas, seguimiento estanques.'),
                        html.Li('Ocultar campos seguimiento de alimento, crecimiento e inventario cuando el lote es nuevo.'),
                        html.Li('Ocultar campos seguimiento de alimento, crecimiento e inventario despues de enviar seguimiento.'),
                        html.Li('Cambiar valores de seguimiento de alimento, crecimiento e inventario despues de enviar seguimiento.'),
                        html.Li('Corrección dias cultivo y alimento acumulado en seguimiento alimentación.'),
                        html.Li('Corrección valor gpd en función de los días de cultivo de seguimiento al crecimiento.'),
                        html.Li('Corrección error al descargar reporte excel inventario pescas y traslados')
                    ]),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H5('Versión 26 Julio 2022.'),
                        html.Li('Corrección error en validación de seguimiento estanques sobre variables calculadas.')
                    ]),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H5('Versión 22 Julio 2022.'),
                        html.Li('Variables calculadas agregadas al ingreso de datos y resumen de seguimiento'),
                        html.Li('Cambios en base de datos, variables calculadas agregadas a tabla de seguimiento'),
                        html.Li('Cambios para visualización de tabla de seguimiento, variables calculadas agregadas'),

                    ]),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H5('Versión 17 Julio 2022.'),
                        html.Li('Campo peso visceras en pesca agregado'),
                        html.Li('Cambios en base de datos, tabla pescas: variable peso_visceras y biomasa neta agregado'),

                    ])
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H5('Versión 12 Julio 2022.'),
                        html.Li('Cambio campo longitud promedio a registro opcional'),
                        html.Li('Reporte de uso App agregado'),
                    ])
                ]),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
            ]),
        
        ]

    elif active_tab == 'tab_consultar_informacion':
        if rol == 'administrador':
            try:
                gerentes = get_data('SELECT documento_identidad, nombre_gerente FROM gerentes')
            except Exception as e:
                print(e)
                gerentes = pd.DataFrame({'documento_identidad': [None],
                        'nombre_gerente': ['Error al consultar gerentes de zona']})                                
            if gerentes.empty:
                gerentes = pd.DataFrame({'documento_identidad': [None],
                                        'nombre_gerente': ['Sin registros']})                
            else:
                gerentes.sort_values(by = ['nombre_gerente'], inplace = True)
                gerentes.reset_index(drop = True, inplace = True)
            clientes = pd.DataFrame({'nit': [None],
                                     'nombre_cliente': ['Por favor seleccione un gerente']})
            granjas = pd.DataFrame({'id_granja': [None],
                                    'nombre_granja': ['Sin registros']})
            style_gerente = {'display': 'inline'}
            style_cliente = {'display': 'inline'}
            style_granja = {'display': 'inline'}
        if rol == 'gerente' or rol == 'especialista':
            gerentes = pd.DataFrame({'documento_identidad': [doc_id],
                                     'nombre_gerente': [user]})
            try:
                clientes = get_data(f'''SELECT nit, nombre_cliente FROM clientes WHERE gerente_zona = {doc_id};''')
            except Exception as e:
                print(e)
                clientes = pd.DataFrame({'nit': [None],
                                        'nombre_cliente': ['Error al consultar clientes']})
            if clientes.empty:
                clientes = pd.DataFrame({'nit': [None],
                                        'nombre_cliente': ['Sin registros']})
            else:
                clientes.sort_values(by = ['nombre_cliente'], inplace = True)
                clientes.reset_index(drop = True, inplace = True)
            granjas = pd.DataFrame({'id_granja': [None],
                        'nombre_granja': ['Sin registros']})
            style_gerente = {'display': 'none'}
            style_cliente = {'display': 'inline'}
            style_granja = {'display': 'inline'}
        if rol == 'cliente':
            gerentes = pd.DataFrame({'documento_identidad': [None],
                                     'nombre_gerente': ['Sin registros']})
            clientes = pd.DataFrame({'nit': [doc_id],
                                     'nombre_cliente': [user]})
            try:
                granjas = get_data(f"SELECT id_granja, nombre_granja FROM granjas WHERE nit_cliente = '{doc_id}'")
            except Exception as e:
                print(e)
                granjas = pd.DataFrame({'id_granja': [None],
                            'nombre_granja': ['Error al consultar granjas']})
            if granjas.empty:
                granjas = pd.DataFrame({'id_granja': [None],
                            'nombre_granja': ['Sin registros']})
            else:
                granjas.sort_values(by = ['nombre_granja'], inplace = True)
                granjas.reset_index(drop = True, inplace = True)
            style_gerente = {'display': 'none'}
            style_cliente = {'display': 'none'}
            style_granja = {'display': 'inline'}
        
        gerentes_opt = [{'label': gerentes['nombre_gerente'][i], 'value': gerentes['documento_identidad'][i]} for i in range(gerentes.shape[0])]
        clientes_opt = [{'label': clientes['nombre_cliente'][i], 'value': clientes['nit'][i]} for i in range(clientes.shape[0])]
        granjas_opt = [{'label': granjas['nombre_granja'][i], 'value': granjas['id_granja'][i]} for i in range(granjas.shape[0])]
        
        return [
            html.Br(),
            # seguimiento semanal
            dbc.Row([
                dbc.Col([
                    dbc.Button('Seguimiento Semanal', id = 'collapse_button_ss',
                               outline = True, color = 'dark')
                ], xl = 6, lg = 6, md = 6, sm = 10, xs = 10)
            ]),
            dbc.Collapse(id = 'collapse_ss', children = [
                dcc.Store(id = 'data_gal_consulta', storage_type = 'session'),
                dcc.Store(id = 'data_reporte_1_ss', storage_type = 'session'),
                # dcc.Store(id = 'data_reporte_2_ss', storage_type = 'session'),
                dcc.Store(id = 'data_download_ss', storage_type = 'session'),
                html.Br(),

                dbc.Row([
                    campos(id_ = 'gerente_consulta', label = 'GERENTE DE ZONA', ayuda = '-',
                            tipo = 'seleccion', style_col = style_gerente,
                            valor = gerentes_opt, vl = doc_id if rol == 'gerente' else None,
                            xl = 3, lg = 3, md = 4, sm = 5, xs = 6),
                    campos(id_ = 'cliente_consulta', label = 'CLIENTE', ayuda = '-', tipo = 'seleccion',
                        valor = clientes_opt, vl = doc_id if rol == 'cliente' else None, style_col = style_cliente,
                        xl = 3, lg = 3, md = 4, sm = 5, xs = 6),
                    # campos(id_ = 'n_cliente_consulta', label = 'NOMBRE CLIENTE', ayuda = '-', tipo = 'text', style_col = style_cliente,
                    #     xl = 3, lg = 3, md = 4, sm = 5, xs = 6),
                    #galpon_consulta
                ]),
                dbc.Row([
                    campos(id_ = 'granja_consulta', label = 'GRANJA', ayuda = '-', tipo = 'seleccion_m',
                        valor = granjas_opt, style_col = style_granja, vl = None,
                        xl = 4, lg = 4, md = 6, sm = 12, xs = 12),
                    año_consulta, lote_consulta,
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button('Cargar tabla', id = 'cargar_tabla_consulta_ss', color = 'warning')
                    ], xl = 2, lg = 3, md = 5, sm = 6, xs = 6),
                    dbc.Col([
                        dbc.Spinner(dbc.Alert(id = 'alert_cargar_tabla_consulta_ss', dismissable=True, is_open = False))
                    ], xl = 6, lg = 6, md = 8, sm = 8, xs = 12)
                ]),
                Download(id="download_excel_ss"),
                html.Br(),
                html.Div([
                    dbc.Modal([
                        dbc.ModalHeader('Datos seguimiento semanal'),
                        dbc.ModalBody(id = 'modal_data_ss_c', children = [
                            dbc.Row([
                                dbc.Col([
                                    html.Div(id = 'tabla_consulta_ss', style = {'overflow': 'auto', 'white-space': 'nowrap'})
                                ])
                            ]),
                            html.Br(),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Descargar excel', id = 'descargar_tabla_consulta_ss', color = 'success')
                                ], xl = 2, lg = 3, md = 4, sm = 6, xs = 6),
                                dbc.Col([
                                    dbc.Spinner(dbc.Alert(id = 'alert_descargar_tabla_consulta_ss', dismissable=True, is_open = False))
                                ], xl = 6, lg = 6, md = 8, sm = 6, xs = 6)
                            ]),
                        ]),
                    ], id = 'modal_data_ss', scrollable = True, is_open = False, size = 'xl'),
                ]),     


                dbc.Row([
                    dbc.Col([
                        dbc.Button('Reporte seguimiento semanal', id = 'generar_reporte_1_ss', color = 'warning')
                    ], xl = 3, lg = 4, md = 5, sm = 6, xs = 6),
                ], no_gutters = True),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.Spinner(dbc.Alert(id = 'alert_generar_reporte_1_ss', dismissable=True, is_open = False))
                    ], xl = 6, lg = 6, md = 8, sm = 6, xs = 6)
                ]),
                Download(id="download_reporte_1_ss"),

                html.Div([
                    dbc.Modal([
                        dbc.ModalHeader('Reporte 1 Seguimiento Semanal'),
                        dbc.ModalBody(id = 'modal_ss_1_c', children = [
                            dbc.Row([
                                dbc.Col([
                                    html.Div(id = 'modal_ss_1_contenido')
                                ])
                            ]),
                            html.Br(),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Descargar reporte', id = 'descargar_reporte_1_ss', color = 'success')
                                ], xl = 3, lg = 3, md = 4, sm = 6, xs = 6),
                                dbc.Col([
                                    dbc.Spinner(dbc.Alert(id = 'alert_descargar_reporte_1_ss', dismissable=True, is_open = False))
                                ], xl = 6, lg = 6, md = 8, sm = 6, xs = 6)
                            #]),
                            ]),
                        ]),
                    ], id = 'modal_ss_1', scrollable = True, is_open = False, size = 'lg'),
                ]),

            html.Br(),
            ]),
            # inventario estanque
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Button('Inventario Estanque', id = 'collapse_button_lq',
                               outline = True, color = 'dark')
                ], xl = 6, lg = 6, md = 6, sm = 10, xs = 10)
            ]),
            dbc.Collapse(id = 'collapse_lq', children = [
                dcc.Store(id = 'data_gal_consulta_i', storage_type = 'session'),
                # dcc.Store(id = 'data_reporte_1_lq', storage_type = 'session'),
                # #dcc.Store(id = 'data_reporte_2_ss', storage_type = 'session'),
                dcc.Store(id = 'data_download_i', storage_type = 'session'),
                html.Br(),
                dbc.Row([
                    tabla_inventario
                ]),



                dbc.Row([
                    campos(id_ = 'gerente_consulta_i', label = 'GERENTE DE ZONA', ayuda = '-',
                            tipo = 'seleccion', style_col = style_gerente,
                            valor = gerentes_opt, vl = doc_id if rol == 'gerente' else None,
                            xl = 3, lg = 3, md = 4, sm = 5, xs = 6),
                    campos(id_ = 'cliente_consulta_i', label = 'NIT CLIENTE', ayuda = '-', tipo = 'seleccion',
                        valor = clientes_opt, vl = doc_id if rol == 'cliente' else None, style_col = style_cliente,
                        xl = 3, lg = 3, md = 4, sm = 5, xs = 6),
                    # campos(id_ = 'n_cliente_consulta', label = 'NOMBRE CLIENTE', ayuda = '-', tipo = 'text', style_col = style_cliente,
                    #     xl = 3, lg = 3, md = 4, sm = 5, xs = 6),
                    #galpon_consulta
                ]),
                dbc.Row([
                    campos(id_ = 'granja_consulta_i', label = 'GRANJA', ayuda = '-', tipo = 'seleccion_m',
                        valor = granjas_opt, style_col = style_granja, vl = None,
                        xl = 4, lg = 4, md = 6, sm = 12, xs = 12),
                    año_consulta_i, lote_consulta_i,
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button('Cargar tabla', id = 'cargar_tabla_consulta_i', color = 'warning')
                    ], xl = 2, lg = 3, md = 5, sm = 6, xs = 6),
                    dbc.Col([
                        dbc.Spinner(dbc.Alert(id = 'alert_cargar_tabla_consulta_i', dismissable=True, is_open = False))
                    ], xl = 6, lg = 6, md = 8, sm = 8, xs = 12)
                ]),
                Download(id="download_excel_i"),
                html.Br(),
                html.Div([
                    dbc.Modal([
                        dbc.ModalHeader('Datos inventario estanques'),
                        dbc.ModalBody(id = 'modal_data_i_c', children = [
                            dbc.Row([
                                dbc.Col([
                                    html.Div(id = 'tabla_consulta_i', style = {'overflow': 'auto', 'white-space': 'nowrap'})
                                ])
                            ]),
                            html.Br(),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Descargar excel', id = 'descargar_tabla_consulta_i', color = 'success')
                                ], xl = 2, lg = 3, md = 4, sm = 6, xs = 6),
                                dbc.Col([
                                    dbc.Spinner(dbc.Alert(id = 'alert_descargar_tabla_consulta_i', dismissable=True, is_open = False))
                                ], xl = 6, lg = 6, md = 8, sm = 6, xs = 6)
                            ]),
                        ]),
                    ], id = 'modal_data_i', scrollable = True, is_open = False, size = 'xl'),
                ]),     


            html.Br(),

            ]),
            html.Br(),
            # dbc.Row([
            #     dbc.Col([
            #         dbc.Button('Compromisos', id = 'collapse_button_cp',
            #                    outline = True, color = 'dark')
            #     ], xl = 6, lg = 6, md = 6, sm = 10, xs = 10)
            # ]),
            # dbc.Collapse(id = 'collapse_cp', children = [
            #     html.Br(),
            #     html.H5('Proximamente'),
            # ]),
            # html.Br(),


            html.Div(children = [

                dbc.Row([
                    dbc.Col([
                        dbc.Button('Trazabilidad de usuarios', id = 'collapse_button_trz',
                                outline = True, color = 'dark')
                    ], xl = 6, lg = 6, md = 6, sm = 10, xs = 10)
                ]),
                dbc.Collapse(id = 'collapse_trz', children = [
                    html.Br(),
                    dbc.Row([
                        #tipo_usuario,
                        campos(id_ = 'tipo_usuario', label = 'TIPO USUARIO', tipo = 'seleccion_m',
                               valor = [{'label': i, 'value': i} for i in [['Administrador', 'Especialista', 'Gerente', 'Cliente'] if rol == 'administrador' else ['Cliente'] if rol in ['especialista', 'gerente'] else [None] ][0]],
                            ayuda = '-', xl = 4, lg = 6, md = 8, sm = 12, xs = 12),
                        campos(id_ = 'accion_usuario', label = 'ACCIÓN USUARIO', tipo = 'seleccion_m',
                               valor = [{'label': i, 'value': i} for i in [acciones_trz_admin if rol == 'administrador' else acciones_trz_cliente][0]],
                               ayuda = '-', xl = 5, lg = 7, md = 10, sm = 12, xs = 12)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button('Reporte de uso', id = 'reporte_uso', color = 'warning')
                        ], xl = 2, lg = 3, md = 4, sm = 6, xs = 8),
                        dbc.Col([
                            dbc.Button('Consultar trazabilidad', id = 'consultar_trz', color = 'warning')
                        ], xl = 3, lg = 4, md = 6, sm = 8, xs = 10),
                        dbc.Col([
                            dbc.Spinner(dbc.Alert(id = 'alert_reporte_uso', dismissable=True, is_open = False))
                        ], xl = 3, lg = 3, md = 8, sm = 8, xs = 12),
                        dbc.Col([
                            dbc.Spinner(dbc.Alert(id = 'alert_consultar_trz', dismissable=True, is_open = False))
                        ], xl = 3, lg = 3, md = 8, sm = 8, xs = 12)
                    ]),
                dcc.Store(id = 'descargar_trazabilidad'),
                html.Div([
                    dbc.Modal([
                        dbc.ModalHeader('Trazabilidad de usuarios'),
                        dbc.ModalBody(id = 'modal_ver_trz', children = [
                            dbc.Row([
                                dbc.Col([
                                    html.Div(id = 'modal_ver_trz_div')
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Descargar', id = 'descargar_trz_c', color = 'success')
                                ], xl = 2, lg = 2, md = 3, sm = 4, xs = 4),
                                dbc.Col([
                                    dbc.Spinner(dbc.Alert(id = 'alert_descargar_trz', dismissable=True, is_open = False))
                                ], xl = 6, lg = 6, md = 6, sm = 8, xs = 8)
                            ])

                        ]),
                    ], id = 'modal_trz', scrollable = True, is_open = False, size = 'xl'),
                    ]),
                Download(id="download_trz"),
                dcc.Store(id = 'descargar_reporte_uso'),
                html.Div([
                    dbc.Modal([
                        dbc.ModalHeader('Reporte de uso'),
                        dbc.ModalBody(id = 'modal_ver_reporte_uso', children = [
                            dbc.Row([
                                dbc.Col([
                                    html.Div(id = 'modal_ver_reporte_uso_div')
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Descargar', id = 'descargar_reporte_uso_c', color = 'success')
                                ], xl = 2, lg = 2, md = 3, sm = 4, xs = 4),
                                dbc.Col([
                                    dbc.Spinner(dbc.Alert(id = 'alert_descargar_reporte_uso', dismissable=True, is_open = False))
                                ], xl = 6, lg = 6, md = 6, sm = 8, xs = 8)
                            ])

                        ]),
                    ], id = 'modal_reporte_uso', scrollable = True, is_open = False, size = 'xl'),
                    ]),

                Download(id="download_reporte_uso")
                ]),
                html.Br(),
            ], style = {'display': 'none'} if not rol in ['administrador'] else {'display': 'inline'})

        ]

    elif active_tab == 'tab_clientes':
        if rol == 'administrador':
            gerentes = get_data('SELECT documento_identidad, nombre_gerente FROM gerentes')
            if gerentes.empty:
                gerentes = pd.DataFrame({'documento_identidad': [None],
                                         'nombre_gerente': ['Sin registros']})
            gerentes.sort_values(axis = 0, by = ['nombre_gerente'], inplace = True)
            gerentes.reset_index(drop = True, inplace = True)
        elif rol == 'gerente' or rol == 'especialista':
            gerentes = pd.DataFrame({'documento_identidad': [doc_id],
                                        'nombre_gerente': [user.upper()]})            
        else:
            gerentes = pd.DataFrame({'documento_identidad': [None],
                                        'nombre_gerente': ['Sin registros']})
        gerentes_opt  = [{'value': gerentes['documento_identidad'][i], 'label': gerentes['nombre_gerente'][i]} for i in range(gerentes.shape[0])]
        return [
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Button('Clientes', id = 'callapse_button_mis_clientes',
                               outline = True, color = 'dark')
                ], xl = 6, lg = 6, md = 6, sm = 10, xs = 10)
            ]),
            dbc.Collapse(id = 'collapse_mis_clientes', children = [
                html.Br(),
                dbc.Row([
                    campos(id_ = 'gerente_ver_cliente', label = 'GERENTE DE ZONA', ayuda = 'Seleccione un gerente', 
                           tipo = 'seleccion_m' if rol == 'administrador' else 'seleccion', valor = gerentes_opt, 
                           vl = doc_id if rol == 'gerente' else None,
                           xl = 5, lg = 7, md = 8, sm = 10, xs = 12),
                    dbc.Col([
                        dbc.Button('Cargar', id = 'cargar_mis_clientes_ng', color = 'warning')
                    ], xl = 2, lg = 2, md = 3, sm = 4, xs = 4),
                    dbc.Col([
                        dbc.Spinner(dbc.Alert(id = 'alert_cargar_mis_clientes_ng', dismissable=True, is_open = False))
                    ], xl = 6, lg = 6, md = 6, sm = 8, xs = 8)
                ], align = 'center'),
                dcc.Store(id = 'descargar_clientes'),
                html.Div([
                    dbc.Modal([
                        dbc.ModalHeader('Clientes registrados'),
                        dbc.ModalBody(id = 'modal_ver_clientes_c', children = [
                            dbc.Row([
                                dbc.Col([
                                    html.Div(id = 'modal_ver_clientes_div')
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Descargar', id = 'descargar_mis_clientes_ng', color = 'success')
                                ], xl = 2, lg = 2, md = 3, sm = 4, xs = 4),
                                dbc.Col([
                                    dbc.Spinner(dbc.Alert(id = 'alert_descargar_mis_clientes_ng', dismissable=True, is_open = False))
                                ], xl = 6, lg = 6, md = 6, sm = 8, xs = 8)
                            ])

                        ]),
                    ], id = 'modal_ver_clientes', scrollable = True, is_open = False, size = 'xl'),
                    ]),
                Download(id="download_clientes_resgistrados"),
                html.Br(),
            ]),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Button('Crear Cliente', id = 'callapse_button_crear_cliente',
                               outline = True, color = 'dark')
                ], xl = 6, lg = 6, md = 6, sm = 10, xs = 10)
            ]),
            dbc.Collapse(id = 'collapse_crear_cliente', children = [
                html.Br(),
                dbc.Row([
                    campos(id_ = 'gerente_cliente', label = 'GERENTE DE ZONA', ayuda = '-', tipo = 'seleccion',
                      valor = gerentes_opt, vl = doc_id if rol == 'gerente' else None,
                      xl = 3, lg = 4, md = 6, sm = 6, xs = 6),
                ]),
                dbc.Row([
                    nit_cliente_ng, nombre_cliente_ng
                ]),
                dbc.Row([
                    telefono_cliente, correo_cliente
                ]),
                dbc.Row([
                    usuario_cliente_ng, pw_cliente_ng
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button('Crear cliente', id = 'crear_cliente_ng', color = 'warning')
                    ], xl = 2, lg = 2, md = 3, sm = 4, xs = 4),
                    dbc.Col([
                        dbc.Spinner(dbc.Alert(id = 'alert_crear_cliente_ng',dismissable=True, is_open = False))
                    ], xl = 8, lg = 8, md = 8, sm = 8, xs = 8)
                ]),
                html.Br()
            ]),
            html.Hr(),

        ]

    elif active_tab == 'tab_gerentes_zona':
        return [
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Button('Gerentes de zona', id = 'callapse_button_ver_gerentes',
                               outline = True, color = 'dark')
                ], xl = 6, lg = 6, md = 6, sm = 10, xs = 10)
            ]),
            dbc.Collapse(id = 'collapse_ver_gerentes', children = [
                html.Br(),
                dbc.Row([
                    # dbc.Col([
                    #     html.H5('Ver gerentes'),
                    # ], xl = 2, lg = 2, md = 3, sm = 4, xs = 4),
                    dbc.Col([
                        dbc.Button('Cargar gerentes', id = 'ver_gerentes', color = 'warning')
                    ], xl = 3, lg = 3, md = 4, sm = 6, xs = 6),
                    dbc.Col([
                        dbc.Spinner(dbc.Alert(id = 'alert_ver_gerentes',dismissable=True, is_open = False))
                    ], xl = 8, lg = 8, md = 8, sm = 8, xs = 8),              
                ], align = 'center'),
                html.Br(),
                dcc.Store(id = 'descargar_gerentes_data'),
                html.Div([
                    dbc.Modal([
                        dbc.ModalHeader('Gerentes registrados'),
                        dbc.ModalBody(id = 'modal_ver_gerentes_c', children = [
                            dbc.Row([
                                dbc.Col([
                                    html.Div(id = 'modal_ver_gerentes_div')
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Descargar', id = 'descargar_gerentes', color = 'success')
                                ], xl = 2, lg = 2, md = 3, sm = 4, xs = 4),
                                dbc.Col([
                                    dbc.Spinner(dbc.Alert(id = 'alert_descargar_gerentes',dismissable=True, is_open = False))
                                ], xl = 6, lg = 6, md = 6, sm = 8, xs = 8)
                            ])

                        ]),
                    ], id = 'modal_ver_gerentes', scrollable = True, is_open = False, size = 'xl'),
                    ]),
                Download(id="download_gerentes_resgistrados"),
                #html.Br()           
                            
            ]),

            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Button('Crear Gerente', id = 'callapse_button_crear_gerente',
                               outline = True, color = 'dark')
                ], xl = 6, lg = 6, md = 6, sm = 10, xs = 10)
            ]),
            dbc.Collapse(id = 'collapse_crear_gerente', children = [
                html.Br(),
                dbc.Row([
                    documento_gerente
                ]),
                dbc.Row([
                    nombre_gerente, pais_gerente, planta_gerente
                ]),
                dbc.Row([
                    telefono_gerente, correo_gerente
                ]),
                dbc.Row([
                    usuario_gerente, pw_gerente
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button('Crear gerente', id = 'crear_gerente', color = 'warning')
                    ], xl = 2, lg = 2, md = 3, sm = 4, xs = 4),
                    dbc.Col([
                        dbc.Spinner(dbc.Alert(id = 'alert_crear_gerente',dismissable=True, is_open = False))
                    ], xl = 8, lg = 8, md = 8, sm = 8, xs = 8)
                ]),
                html.Br()                             
            ]),
            html.Br(),
        ]

    elif active_tab == 'tab_especialistas':
        return [
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Button('Especialistas', id = 'callapse_button_ver_especialistas',
                               outline = True, color = 'dark')
                ], xl = 6, lg = 6, md = 6, sm = 10, xs = 10)
            ]),
            dbc.Collapse(id = 'collapse_ver_especialistas', children = [
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.Button('Cargar especialistas', id = 'ver_especialistas', color = 'warning')
                    ], xl = 3, lg = 3, md = 4, sm = 6, xs = 6),
                    dbc.Col([
                        dbc.Spinner(dbc.Alert(id = 'alert_ver_especialistas',dismissable=True, is_open = False))
                    ], xl = 8, lg = 8, md = 8, sm = 8, xs = 8),              
                ], align = 'center'),
                html.Br(),
                dcc.Store(id = 'descargar_especialistas_data'),
                html.Div([
                    dbc.Modal([
                        dbc.ModalHeader('Especialistas registrados'),
                        dbc.ModalBody(id = 'modal_ver_especialistas_c', children = [
                            dbc.Row([
                                dbc.Col([
                                    html.Div(id = 'modal_ver_especialistas_div')
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Descargar', id = 'descargar_especialistas', color = 'success')
                                ], xl = 2, lg = 2, md = 3, sm = 4, xs = 4),
                                dbc.Col([
                                    dbc.Spinner(dbc.Alert(id = 'alert_descargar_especialistas',dismissable=True, is_open = False))
                                ], xl = 6, lg = 6, md = 6, sm = 8, xs = 8)
                            ])

                        ]),
                    ], id = 'modal_ver_especialistas', scrollable = True, is_open = False, size = 'xl'),
                    ]),
                Download(id="download_especialistas_resgistrados"),
                #html.Br()           
                            
            ]),

            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Button('Crear Especialista', id = 'callapse_button_crear_especialista',
                               outline = True, color = 'dark')
                ], xl = 6, lg = 6, md = 6, sm = 10, xs = 10)
            ]),
            dbc.Collapse(id = 'collapse_crear_especialista', children = [
                html.Br(),
                dbc.Row([
                    documento_especialista
                ]),
                dbc.Row([
                    nombre_especialista, pais_especialista, planta_especialista
                ]),
                dbc.Row([
                    telefono_especialista, correo_especialista
                ]),
                dbc.Row([
                    usuario_especialista, pw_especialista
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button('Crear especialista', id = 'crear_especialista', color = 'warning')
                    ], xl = 2, lg = 2, md = 3, sm = 4, xs = 4),
                    dbc.Col([
                        dbc.Spinner(dbc.Alert(id = 'alert_crear_especialista',dismissable=True, is_open = False))
                    ], xl = 8, lg = 8, md = 8, sm = 8, xs = 8)
                ]),
                html.Br()                             
            ]),
            html.Br(),
        ]

    elif active_tab == 'tab_administrar_granjas':
        if rol == 'administrador':
            gerentes = get_data('SELECT documento_identidad, nombre_gerente FROM gerentes')
            clientes = pd.DataFrame({'nit': [None],
                                     'nombre_cliente': ['-']})
            granjas = pd.DataFrame({'id_granja': [None],
                                    'nombre_granja': ['Seleccione un cliente']})
            if gerentes.empty:
                gerentes = pd.DataFrame({'documento_identidad': [None],
                                         'nombre_gerente': ['Sin registros']})
            gerentes.sort_values(axis = 0, by = ['nombre_gerente'], inplace = True)
            gerentes.reset_index(drop = True, inplace = True)
            style_gerente = {'display': 'inline'}
        elif rol == 'gerente' or rol == 'especialista':
            gerentes = pd.DataFrame({'documento_identidad': [doc_id],
                                     'nombre_gerente': [user.upper()]})
            clientes = get_data(f'SELECT nit, nombre_cliente FROM clientes WHERE gerente_zona = {doc_id}')                                        
            granjas = pd.DataFrame({'id_granja': [None],
                        'nombre_granja': ['Seleccione un cliente']})
            if clientes.empty:
                clientes = pd.DataFrame({'nit': [None],
                                        'nombre_cliente': ['Sin registros']})
            clientes.sort_values(axis = 0, by = ['nombre_cliente'], inplace = True)
            clientes.reset_index(drop = True, inplace = True)
            style_gerente = {'display': 'inline'}
        elif rol == 'cliente':
            gerentes = pd.DataFrame({'documento_identidad': [None],
                                        'nombre_gerente': ['Sin registros']})
            clientes = pd.DataFrame({'nit': [doc_id],
                                    'nombre_cliente': [user.upper()]})
            granjas = get_data(f'SELECT id_granja, nombre_granja FROM granjas WHERE nit_cliente = {doc_id}')
            style_gerente = {'display': 'none'}
        gerentes_opt  = [{'value': gerentes['documento_identidad'][i], 'label': gerentes['nombre_gerente'][i]} for i in range(gerentes.shape[0])]
        clientes_opt  = [{'value': clientes['nit'][i], 'label': clientes['nombre_cliente'][i]} for i in range(clientes.shape[0])]
        granjas_opt = [{'value': granjas['id_granja'][i], 'label': granjas['nombre_granja'][i]} for i in range(granjas.shape[0])]
        return [
            html.Hr(),

            dbc.Row([
                dbc.Col([
                    dbc.Button('Mis granjas' if rol == 'cliente' else 'Granjas', 
                               id = 'callapse_button_mis_granjas', outline = True, color = 'dark')
                ], xl = 3, lg = 4, md = 6, sm = 6, xs = 6),
                dbc.Col([
                    dbc.Button('Crear granja', id = 'callapse_button_crear_granja',
                               outline = True, color = 'dark')
                ], xl = 3, lg = 4, md = 6, sm = 6, xs = 6)
            ]),
            dbc.Collapse(id = 'collapse_mis_granjas', children = [
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H4('Granjas registradas')
                    ])
                ]),
                dbc.Row([
                    campos(id_ = 'gerente_ver_granjas_nc', label = 'GERENTE DE ZONA', ayuda = 'Seleccione un gerente',
                      tipo = 'seleccion', valor = gerentes_opt, vl = doc_id if rol == 'gerente' else None,
                      xl = 3, lg = 4, md = 6, sm = 6, xs = 6, style_col = style_gerente),
                    campos(id_ = 'nit_cliente_ver_granjas', label = 'CLIENTE', ayuda = 'Seleccione un cliente', 
                           tipo = 'seleccion' if rol == 'cliente' else 'seleccion_m', valor = clientes_opt,
                           vl = doc_id if rol == 'cliente' else None,
                            xl = 3, lg = 4, md = 6, sm = 6, xs = 6),
                    dbc.Col([
                        dbc.Button('Cargar', id = 'cargar_mis_granjas_nc', color = 'warning')
                    ], xl = 2, lg = 2, md = 3, sm = 4, xs = 4),
                    dbc.Col([
                        dbc.Spinner(dbc.Alert(id = 'alert_cargar_mis_granjas_nc',dismissable=True, is_open = False))
                    ], xl = 6, lg = 6, md = 6, sm = 8, xs = 8)                    
                ], align = 'center'),
                html.Br(),
                dcc.Store(id = 'descargar_granjas'),
                html.Div([
                    dbc.Modal([
                        dbc.ModalHeader('Granjas registradas'),
                        dbc.ModalBody(id = 'modal_ver_granjas_c', children = [
                            dbc.Row([
                                dbc.Col([
                                    html.Div(id = 'modal_ver_granjas_div')
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Descargar', id = 'descargar_granjas_c', color = 'success')
                                ], xl = 2, lg = 2, md = 3, sm = 4, xs = 4),
                                dbc.Col([
                                    dbc.Spinner(dbc.Alert(id = 'alert_descargar_granjas',dismissable=True, is_open = False))
                                ], xl = 6, lg = 6, md = 6, sm = 8, xs = 8)
                            ])

                        ]),
                    ], id = 'modal_ver_granjas', scrollable = True, is_open = False, size = 'xl'),
                    ]),
                Download(id="download_granjas_resgistrados"),                
            ]),

            html.Hr(),

            # dbc.Row([

            # ]),
            dbc.Collapse(id = 'collapse_crear_granja', children = [
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H4('Crear granja')
                    ])
                ]),
                dbc.Row([
                    campos(id_ = 'gerente_nc', label = 'GERENTE DE ZONA', ayuda = 'Selecione un gerente', tipo = 'seleccion',
                      valor = gerentes_opt, vl = doc_id if rol == 'gerente' else None,
                      xl = 3, lg = 4, md = 6, sm = 6, xs = 6, style_col = style_gerente)                   
                ]),
                dbc.Row([
                    campos(id_ = 'nit_clientes_nc', label = 'CLIENTE', ayuda = 'Seleccione un cliente', 
                           tipo = 'seleccion', valor = clientes_opt, vl = doc_id if rol == 'cliente' else None,
                            xl = 3, lg = 4, md = 6, sm = 6, xs = 6),                   
                    campos(tipo = 'number', label = 'Número de granjas', ayuda = 'Ingrese el número de granjas a crear', id_ = 'numero_granjas_nc'),
                ]),
                dbc.Row([                    
                    campos(tipo = 'boton', valor = 'Cargar tabla de ingreso', id_ = 'cargar_tabla_ingreso_granjas_nc',
                           xl = 3, lg = 4, md = 5, sm = 5, xs = 6)
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.Div(id = 'tabla_ingreso_granjas_nc', style = {'overflow': 'auto', 'white-space': 'nowrap'})
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Alert(id = 'tabla_ingreso_granjas_nc_sal', is_open = False,dismissable=True)
                    ])
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.Button('Crear granja', id = 'crear_granja_no_cliente', color = 'warning')
                    ], xl = 2, lg = 2, md = 3, sm = 4, xs = 4),
                    dbc.Col([
                        dbc.Spinner(dbc.Alert(id = 'alert_crear_granja_nc',dismissable=True, is_open = False))
                    ], xl = 8, lg = 8, md = 8, sm = 8, xs = 8)
                ]),
                html.Br()
            ]),
            html.Hr(),

            dbc.Row([
                dbc.Col([
                    dbc.Button('Mis unidades productivas' if rol == 'cliente' else 'Unidades productivas', 
                               id = 'callapse_button_mis_up', outline = True, color = 'dark')
                ], xl = 3, lg = 4, md = 6, sm = 6, xs = 6),
                dbc.Col([
                    dbc.Button('Crear unidad productiva', id = 'callapse_button_crear_up',
                               outline = True, color = 'dark')
                ], xl = 3, lg = 4, md = 6, sm = 6, xs = 6)
            ]),
            dbc.Collapse(id = 'collapse_mis_up', children = [
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H4('Unidades productivas registradas')
                    ])
                ]),
                dbc.Row([
                    campos(id_ = 'gerente_ver_up_nc', label = 'GERENTE DE ZONA', ayuda = 'Seleccione un gerente',
                      tipo = 'seleccion', valor = gerentes_opt, vl = doc_id if rol == 'gerente' else None,
                      xl = 3, lg = 4, md = 6, sm = 6, xs = 6, style_col = style_gerente),
                    campos(id_ = 'nit_cliente_ver_up', label = 'CLIENTE', ayuda = 'Seleccione un cliente', 
                           tipo = 'seleccion' if rol == 'cliente' else 'seleccion_m', valor = clientes_opt,
                           vl = doc_id if rol == 'cliente' else None,
                            xl = 3, lg = 4, md = 6, sm = 6, xs = 6),
                    dbc.Col([
                        dbc.Button('Cargar', id = 'cargar_mis_up_nc', color = 'warning')
                    ], xl = 2, lg = 2, md = 3, sm = 4, xs = 4),
                    dbc.Col([
                        dbc.Spinner(dbc.Alert(id = 'alert_cargar_mis_up_nc',dismissable=True, is_open = False))
                    ], xl = 6, lg = 6, md = 6, sm = 8, xs = 8)                    
                ], align = 'center'),
                html.Br(),
                dcc.Store(id = 'descargar_up'),
                html.Div([
                    dbc.Modal([
                        dbc.ModalHeader('Unidades productivas registradas'),
                        dbc.ModalBody(id = 'modal_ver_up_c', children = [
                            dbc.Row([
                                dbc.Col([
                                    html.Div(id = 'modal_ver_up_div')
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Descargar', id = 'descargar_up_c', color = 'success')
                                ], xl = 2, lg = 2, md = 3, sm = 4, xs = 4),
                                dbc.Col([
                                    dbc.Spinner(dbc.Alert(id = 'alert_descargar_up',dismissable=True, is_open = False))
                                ], xl = 6, lg = 6, md = 6, sm = 8, xs = 8)
                            ])

                        ]),
                    ], id = 'modal_ver_up', scrollable = True, is_open = False, size = 'xl'),
                    ]),
                Download(id="download_up_resgistrados"),                
            ]),

            html.Hr(),

            # dbc.Row([

            # ]),
            dbc.Collapse(id = 'collapse_crear_up', children = [
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.H4('Crear unidad productiva')
                    ])
                ]),
                dbc.Row([
                    campos(id_ = 'gerente_nc_up', label = 'GERENTE DE ZONA', ayuda = 'Selecione un gerente', tipo = 'seleccion',
                      valor = gerentes_opt, vl = doc_id if rol == 'gerente' else None,
                      xl = 3, lg = 4, md = 6, sm = 6, xs = 6, style_col = style_gerente)                   
                ]),
                dbc.Row([
                    campos(id_ = 'nit_clientes_nc_up', label = 'CLIENTE', ayuda = 'Seleccione un cliente', 
                           tipo = 'seleccion', valor = clientes_opt, vl = doc_id if rol == 'cliente' else None,
                            xl = 3, lg = 4, md = 6, sm = 6, xs = 6),                   
                    campos(id_ = 'granja_up_nc', label = 'GRANJA', ayuda = 'Seleccione una granja', tipo = 'seleccion',
                       xl = 4, lg = 5, md = 8, sm = 10, xs = 10, valor = granjas_opt, 
                       vl = None),
                ]),
                dbc.Row([
                    campos(tipo = 'number', label = 'Número de unidades', id_ = 'numero_up', ayuda = 'Jaulas/Estanques etc.'),
                ]),
                dbc.Row([                    
                    campos(tipo = 'boton', valor = 'Cargar tabla de ingreso', id_ = 'cargar_tabla_ingreso_up_nc',
                           xl = 3, lg = 4, md = 5, sm = 5, xs = 6)
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        html.Div(id = 'tabla_ingreso_up_nc', style = {'overflow': 'auto', 'white-space': 'nowrap'})
                    ])
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Alert(id = 'tabla_ingreso_up_nc_sal', is_open = False,dismissable=True)
                    ])
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        dbc.Button('Crear unidad productiva', id = 'crear_up_no_cliente', color = 'warning')
                    ], xl = 3, lg = 3, md = 4, sm = 5, xs = 5),
                    dbc.Col([
                        dbc.Spinner(dbc.Alert(id = 'alert_crear_up_nc', dismissable=True, is_open = False))
                    ], xl = 8, lg = 8, md = 8, sm = 8, xs = 8)
                ]),
                html.Br()
            ]),


            html.Hr(),
        ]

### CALLBACKS PESTAÑA INGRESO INFORMACION

# validar información seguimiento a estanques
@app.callback([Output('alert_validar_seguimiento_estanque', 'children'),
               Output('alert_validar_seguimiento_estanque', 'color'),
               Output('alert_validar_seguimiento_estanque', 'is_open'),
               Output('modal_se', 'is_open'),
               Output('div_validacion_se', 'children'),
               Output('data_val_se', 'data'),
               Output('data_traslado', 'data'),
               Output('data_alimentacion', 'data'),
               Output('data_pesca', 'data'),
               Output('sal_tabla_traslados', 'children'),
               Output('sal_tabla_pescas', 'children'),
               Output('sal_tabla_alimentacion', 'children'),
               Output('sal_tabla_calculada', 'children')],
               Input('validar_seguimiento_estanque', 'n_clicks'),
               [State('user_info', 'data')] + [
                State(fecha_, 'date') for fecha_ in dates_in] + [
                State(i, 'value') for i in ids_ingreso] + [
                State(i, 'children') for i in ids_tabla_ingreso] + [
                State('rango_fecha_alm', 'start_date'),
                State('rango_fecha_alm', 'end_date'),
                State('rango_fecha_cre', 'start_date'),
                State('rango_fecha_cre', 'end_date'),
                State('rango_fecha_mort', 'start_date'),
                State('rango_fecha_mort', 'end_date'),
                State('cerrar_lote', 'value'),
                State('genetica_ingreso', 'value'),
                State('vacunacion_traslado', 'value')])
def validar_seguimiento_semanal(n, data, fecha_ingreso, fecha_siembra, gerente, 
                                cliente, granja, lote_nuevo, registrar_a, lote, especie, peso_siembra, talla, 
                                numero_inicial_peces, estanque, tipo_estanque, area_m2, vol_m3, 
                                aireacion, tipo_aireador, etapa_cultivo, dias_ultima_fecha,  alimento_ultima_fecha, 
                                marca_alimento, n_fuentes_alimento, seg_crecimiento, real, longitud, mortalidad, 
                                mortalidad_i,  peso_mortalidad, translado, translado_i, Pesca, 
                                numero_pesca, peso_visceras, t_alimento, t_traslado, t_pesca, fecha_alm_i,
                                fecha_alm_f, fecha_cre_i, fecha_cre_f, fecha_mort_i, fecha_mort_f, cerrar, genetica,
                                vacunacion):

    salidas = 9
    if n is None:
        raise dash.exceptions.PreventUpdate()
    usuario = pd.read_json(data, orient = 'split')
    user = usuario['nombre'].values[0]
    rol = usuario['rol_usuario'].values[0]
    doc_id = usuario['doc_id'].values[0]
    pais = usuario['pais'].values[0]

    if rol == 'administrador':
        if gerente is None:
            return ['Gerente de zona no valido', 'warning', True, False] + [no_update]*salidas
    if rol in ['gerente', 'especialista', 'administrador']:
        if cliente is None:
            return ['Nit cliente no valido', 'warning', True, False] + [no_update]*salidas
    if granja is None or granja == '':
        return ['Granja no valida', 'warning', True, False] + [no_update]*salidas
    if lote == '' or lote == None:
        return ['Lote no valido', 'warning', True, False] + [no_update]*salidas
    elif lote_nuevo == None or len(lote_nuevo) == 0:
        lote = json.loads(lote)
        if lote['value'] == '-' or lote['value'] == '':
            return ['Lote no valido', 'warning', True, False] + [no_update]*salidas
        id_lote = lote['value']
        nombre_lote = lote['label']
    else:
        f_base = datetime.strptime(fecha_ingreso, '%Y-%m-%d').date()
        id_lote = f'{f_base.year}{f_base.month}{f_base.day}{granja}{randint(0,999)}'
        nombre_lote = lote

    if estanque is None or estanque == '':
        return ['Estanque no valido', 'warning', True, False] + [no_update]*salidas

    try:
        estanque = json.loads(estanque)
        if estanque['value'] is None:
            return ['Estanque no valido', 'warning', True, False] + [no_update]*salidas
        id_estanque = estanque['value']
    except Exception as e:
        print(e)

    if especie is None:
        return ['Especie sembrada no valida', 'warning', True, False] + [no_update]*salidas

    if especie == 'TN':
        if not bool(genetica):
            return ['Linea genética no valida', 'warning', True, False] + [no_update]*salidas

    if fecha_siembra is None:
        return ['Fecha siembra no valida', 'warning', True, False] + [no_update]*salidas

    if peso_siembra is None:
        return ['Peso siembra no valido', 'warning', True, False] + [no_update]*salidas

    if talla is None:
        return ['Talla siembra no valida', 'warning', True, False] + [no_update]*salidas

    if isinstance(numero_inicial_peces, str) or numero_inicial_peces is None or numero_inicial_peces <= 0:
        return ['Nº inicial peces no valido', 'warning', True, False] + [no_update]*salidas

    if tipo_estanque is None:
        return ['Tipo estanque no valido', 'warning', True, False] + [no_update]*salidas
    
    if isinstance(area_m2, str) or area_m2 is None or area_m2 <= 0:
        return ['Área no valida', 'warning', True, False] + [no_update]*salidas

    if isinstance(vol_m3, str) or vol_m3 is None or vol_m3 <= 0:
        return ['Volumen no valido', 'warning', True, False] + [no_update]*salidas

    if tipo_aireador is None or tipo_aireador == '':
        return ['Tipo de aireador no valido', 'warning', True, False] + [no_update]*salidas
    
    if tipo_aireador != 'NINGUNO':
        if isinstance(aireacion, str) or aireacion is None or aireacion <= 0:
            return ['Aireación no valida', 'warning', True, False] + [no_update]*salidas
    else:
        aireacion = 0
    if etapa_cultivo is None or etapa_cultivo == '':
        return ['Fase de cultivo no valida', 'warning', True, False] + [no_update]*salidas

    if lote_nuevo != ['Si'] and registrar_a == ['Si']:
        if marca_alimento is None or len(marca_alimento) == 0:
            return ['Marca de alimento no valida', 'warning', True, False] + [no_update]*salidas

        if isinstance(n_fuentes_alimento, str) or n_fuentes_alimento is None or n_fuentes_alimento <= 0:
            return ['Número de fuentes de alimento no valido', 'warning', True, False] + [no_update]*salidas

        dt_alimento = cargarDatosTablaIngreso('ingreso_alimento', t_alimento, n_fuentes_alimento)
        if dt_alimento == 'Tabla sin datos':
            return ['Por favor complete la tabla de alimentación', 'warning', True, False] + [no_update]*salidas
        else:
            val_datos = validarTablaIngreso(dt_alimento, 'ingreso_alimento')
        if val_datos != 'ok':
            return [val_datos, 'warning', True, False] + [no_update]*salidas
        dt_alimento = pd.DataFrame.from_dict(dt_alimento, orient = 'index')
        dt_alimento.columns = ['tipo_alimento', 'precio_b_40_kg', 'kg_real', 'observaciones']
        dt_alimento['id_lote'] = id_lote
        dt_alimento['id_estanque'] = estanque['value']
        dt_alimento['fecha'] = fecha_ingreso
        dt_alimento['fecha_inicial'] = fecha_alm_i
        dt_alimento['fecha_final'] = fecha_alm_f
        dt_alimento = dt_alimento[['fecha', 'fecha_inicial', 'fecha_final', 'tipo_alimento', 'precio_b_40_kg', 'kg_real', 'id_lote', 'id_estanque', 'observaciones']]
        alimento = dt_alimento[['precio_b_40_kg', 'kg_real']]

    else:
        dt_alimento = pd.DataFrame()
        dt_alimento['fecha'] = [fecha_ingreso]
        dt_alimento['fecha_inicial'] = [None]
        dt_alimento['fecha_final'] = [None]
        dt_alimento['tipo_alimento'] = ['-']
        dt_alimento['precio_b_40_kg'] = [0]
        dt_alimento['kg_real'] = [0]
        dt_alimento['id_lote'] = [id_lote]
        dt_alimento['id_estanque'] = [estanque['value']]
        dt_alimento['observaciones'] = ['-']
        alimento = dt_alimento[['precio_b_40_kg', 'kg_real']]
        fecha_alm_i = None
        fecha_alm_f = None
        
    # if fecha_muestreo_a is None:
    #     return ['Fecha muestreo anterior no valida', 'warning', True, False] + [no_update]*salidas

    if seg_crecimiento == ['Si']:

        if isinstance(real, str) or real is None or real <= 0:
            return ['Peso promedio no valido', 'warning', True, False] + [no_update]*salidas
    else:
        seg_crecimiento = ['No']
        real = None
        longitud = None
        fecha_cre_i = None
        fecha_cre_f = None
        
        # if isinstance(longitud, str) or longitud is None or longitud < 0:
        #     return ['Longitud promedio no valida', 'warning', True, False] + [no_update]*salidas

    if mortalidad == ['Si']:

        if isinstance(mortalidad_i, str) or mortalidad_i is None or mortalidad_i <= 0:
            return ['Mortalidad no valida', 'warning', True, False] + [no_update]*salidas

        if isinstance(peso_mortalidad, str) or peso_mortalidad is None or peso_mortalidad <= 0:
            return ['Peso mortalidad no valida', 'warning', True, False] + [no_update]*salidas

    else:
        mortalidad = ['No']
        mortalidad_i = 0
        peso_mortalidad = 0
        fecha_mort_i = None 
        fecha_mort_f = None

    if translado == ['Si']:
        
        if isinstance(translado_i, str) or translado_i is None or translado_i <= 0:
            return ['Cantidad de traslado no valido', 'warning', True, False]  + [no_update]*salidas

        if especie in ['MR', 'TN']:
            if not bool(vacunacion):
                return ['Vacuanción traslado no valida', 'warning', True, False]  + [no_update]*salidas

        dt_traslado = cargarDatosTablaIngreso('ingreso_traslado', t_traslado, translado_i)

        if dt_traslado == 'Tabla sin datos':
            return ['Por favor complete la tabla de traslados', 'warning', True, False] + [no_update]*salidas
        else:
            val_datos = validarTablaIngreso(dt_traslado, 'ingreso_traslado')
        if val_datos != 'ok':
            return [val_datos, 'warning', True, False] + [no_update]*salidas
        dt_traslado = pd.DataFrame.from_dict(dt_traslado, orient = 'index')
        dt_traslado.columns = ['fecha', 'cantidad', 'peso_promedio', 'estanque_destino', 'observaciones']
        e_destino = dt_traslado['estanque_destino'].copy()
        dt_traslado['estanque_destino'] = e_destino.apply(lambda x: json.loads(x)['label'])
        dt_traslado['id_estanque_destino'] = e_destino.apply(lambda x: json.loads(x)['value'])
        dt_traslado['id_lote'] = id_lote
        dt_traslado['estanque_origen'] = estanque['value']
        dt_traslado['vacuna'] = vacunacion
        dt_traslado = dt_traslado[['fecha', 'cantidad', 'peso_promedio', 'vacuna', 'estanque_origen', 
                                 'estanque_destino', 'id_estanque_destino', 'id_lote', 'observaciones']]
        traslados_ = dt_traslado[['cantidad', 'peso_promedio']]
    else:
        translado = ['No']
        translado_i = 0
        dt_traslado = pd.DataFrame({'fecha': ['-'],
                                    'cantidad': [0],
                                    'peso_promedio': [0],
                                    'vacuna': [None],
                                    'estanque_origen': ['-'],
                                    'estanque_destino': ['-'],
                                    'id_estanque_destino': ['-'],
                                    'id_lote': ['-'],
                                    'observaciones': ['-']})
        traslados_ = dt_traslado[['cantidad', 'peso_promedio']]

    if Pesca == ['Si']:

        if isinstance(numero_pesca, str) or numero_pesca is None or numero_pesca <= 0:
            return ['Número de  pescas no valido', 'warning', True, False] + [no_update]*salidas

        dt_pescas = cargarDatosTablaIngreso('ingreso_pesca', t_pesca, numero_pesca)

        if dt_pescas == 'Tabla sin datos':
            return ['Por favor complete la tabla de pescas', 'warning', True, False] + [no_update]*salidas
        else:
            val_datos = validarTablaIngreso(dt_pescas, 'ingreso_pesca')
        if val_datos != 'ok':
            return [val_datos, 'warning', True, False] + [no_update]*salidas
        dt_pescas = pd.DataFrame.from_dict(dt_pescas, orient = 'index')
        dt_pescas.columns = ['fecha', 'cantidad', 'biomasa', 'peso_visceras', 'observaciones']
        dt_pescas['id_lote'] = id_lote
        dt_pescas['id_estanque'] = estanque['value']
        dt_pescas = dt_pescas[['fecha', 'cantidad', 'biomasa', 'peso_visceras', 'id_lote', 'id_estanque', 'observaciones']]

        if bool(peso_visceras):
            dt_pescas['peso_visceras'] = dt_pescas['biomasa']*dt_pescas['peso_visceras']/100

        dt_pescas['biomasa_neta'] = dt_pescas['biomasa'] - dt_pescas['peso_visceras']

    else:
        Pesca = ['No']
        numero_pesca = 0
        dt_pescas = pd.DataFrame({'fecha': ['-'],
                                 'cantidad': [0],
                                 'biomasa': [0],
                                 'peso_visceras': [0],
                                 'biomasa_neta': [0],
                                 'id_lote': ['-'],
                                 'id_estanque': ['-'],
                                 'observaciones': ['-']})    
 
    if rol in ['gerente', 'especialista']:
        gerente = doc_id      
    if rol == 'cliente':
        cliente = doc_id
    try:
        data = get_data(f'SELECT clientes.nombre_cliente, granjas.departamento_provincia, granjas.municipio, granjas.nombre_granja, gerentes.nombre_gerente, gerentes.documento_identidad FROM clientes INNER JOIN  granjas ON clientes.nit = granjas.nit_cliente INNER JOIN gerentes ON clientes.gerente_zona = gerentes.documento_identidad WHERE clientes.nit = {cliente} AND  granjas.id_granja = {granja}')
    except Exception as e:
        print(e)
        return [f'Error al consutar la información', 'warning', True, False] + [no_update]*salidas

    if rol == 'cliente':
        gerente = data['documento_identidad'].unique()[0]

    depto = data['departamento_provincia'].unique()[0]
    municipio = data['municipio'].unique()[0]
    nombre_granja = data['nombre_granja'].unique()[0]
    nombre_cliente = data['nombre_cliente'].unique()[0]        
    nombre_gerente = data['nombre_gerente'].unique()[0]
    if lote_nuevo == ['Si']:
        saldo_peces_anterior = numero_inicial_peces
        saldo_peces = saldo_peces_anterior -  mortalidad_i - dt_traslado['cantidad'].sum() - dt_pescas['cantidad'].sum()
        edad_peso = referencias(especie = especie, peso_siembra = peso_siembra, referencia = 'EDAD')
    else:
        sql = f'SELECT fecha, mortalidad, saldo_peces, edad_por_peso FROM seguimiento_estanques WHERE nit_cliente = {cliente} AND id_lote = {id_lote} AND id_estanque = {id_estanque}'

        try:
            dt_ = get_data(sql)
            if dt_.empty:
                saldo_peces_anterior = numero_inicial_peces
                saldo_peces = saldo_peces_anterior -  mortalidad_i - dt_traslado['cantidad'].sum() - dt_pescas['cantidad'].sum()
                edad_peso = referencias(especie = especie, peso_siembra = peso_siembra, referencia = 'EDAD')# get_data(sql) # mas diferencia fecha acutual y fecha registro anterior
            else:
                f_ing = dt_['fecha'].values[-1]
                saldo_peces_anterior = dt_['saldo_peces'].values[-1]
                saldo_peces = saldo_peces_anterior -  mortalidad_i - dt_traslado['cantidad'].sum() - dt_pescas['cantidad'].sum()
                try:
                    f_actual = datetime.strptime(fecha_ingreso, '%Y-%m-%d').date()
                    f_siembra = datetime.strptime(fecha_siembra, '%Y-%m-%d').date()
                    edad_peso = referencias(especie = especie, peso_siembra = peso_siembra, referencia = 'EDAD') + int((f_actual-f_siembra).days)
                    #dt_['edad_por_peso'].values[-1] + (datetime.strptime(fecha_ingreso, '%Y-%m-%d').date() - f_ing).days# get_data(sql) # mas diferencia fecha acutual y fecha registro anterior
                except Exception as e:
                    print(e)
                    edad_peso = nan
        except Exception as e:
            print(e)
            saldo_peces_anterior = nan
            saldo_peces = saldo_peces_anterior -  mortalidad_i - dt_traslado['cantidad'].sum() - dt_pescas['cantidad'].sum()
            edad_peso = nan# get_data(sql) # mas diferencia fecha acutual y fecha registro anterior

    if saldo_peces < 0:
        return [f'Saldo peces en estanque menor a 0', 'warning', True, False] + [no_update]*salidas




    try:
        data = seguimientoEstanque(gerente, cliente, depto, municipio, nombre_lote, nombre_granja, 
                                   nombre_cliente, nombre_gerente, id_lote, fecha_ingreso, fecha_siembra,
                                   granja, estanque['value'], estanque['label'], tipo_estanque, especie, 
                                   peso_siembra, talla, numero_inicial_peces, area_m2, vol_m3, tipo_aireador,
                                   real, mortalidad,  mortalidad_i, peso_mortalidad, longitud, saldo_peces, 
                                   saldo_peces_anterior, edad_peso, aireacion, etapa_cultivo, 
                                   fecha_cre_i, fecha_cre_f, fecha_mort_i, fecha_mort_f, alimento,
                                   dt_pescas['biomasa_neta'].sum(), cerrar, dt_pescas['biomasa'].sum(),
                                   dt_pescas['cantidad'].sum(), lote_nuevo, traslados_,
                                   genetica)
    except Exception as e:
        print(e)                                
        return [f'Error al consolidar la información', 'warning', True, False] + [no_update]*salidas


    try:
        data_resumen = data.copy()
        data_resumen.drop(axis = 1, labels = ['gerente_zona', 'id_granja', 'id_lote', 'id_estanque',
                                              'biomasa_inicial_kg', 'mortalidad_%', 'factor_condicion_k',
                                              'consumo_total_alimento', 'biomasa_final', 'densidad_kg_m2',
                                              'biomasa_neta', 'fca', 'sgr', 'gpd', 'numero_lotes_año',
                                              'toneladas_ha_año', 'costo_punto_conversion','costo_kg_alimento',
                                             ], inplace = True)

        data_resumen.columns = ['FECHA', 'AÑO', 'MES', 'SEMANA AÑO', 'GERENTE ZONA', 'NIT CLIENTE', 'CLIENTE', 
                                'DEPARTAMENTO', 'MUNICIPIO', 'GRANJA', 'LOTE', 'FECHA SIEMBRA', 'EDAD x PESO',
                                'ESTANQUE', 'TIPO ESTANQUE', 'ESPECIE', 'LINEA GENÉTICA', 'PESO SIEMBRA', 'TALLA', 
                                'NUMERO INICIAL PECES', 'AREA (m2)', 'VOLUMEN (m3)', 'TIPO AIREADOR', 'AIREACIÓN', 'FASE CULTIVO',
                                'FECHA INCIAL CRE', 'FECHA FINAL CRE', 'PESO PROMEDIO', 'LONGITUD PROMEDIO', 'MORTALIDAD', 'FECHA INICIAL MORT', 
                                'FECHA FINAL MORT', 'NÚMERO MORTALIDAD', 'PESO MORTALIDAD', 'SALDO PECES', 'DÍAS CULTIVO']
        
        data_calculada = data.copy()
        data_calculada = data_calculada[['biomasa_inicial_kg', 'mortalidad_%', 'factor_condicion_k',
                                         'consumo_total_alimento', 'biomasa_final', 'densidad_kg_m2',
                                         'biomasa_neta', 'fca', 'sgr', 'gpd', 'costo_punto_conversion']]

# 'numero_lotes_año', 'toneladas_ha_año', 'costo_kg_alimento' 

        data_calculada.columns = ['BIOMASA INICIAL KG', 'MORTALIDAD %', 'FACTOR CONDICIÓN K',
                                  'CONSUMO TOTAL ALIMENTO', 'BIOMASA FINAL', 'DENSIDAD KG M3',
                                  'BIOMASA NETA', 'FCA NETA', 'SGR', 'GPD gramos', 'COSTO PUNTO CONVERSIÓN']
        if not bool(cerrar):
            data_calculada.columns = ['BIOMASA INICIAL KG', 'MORTALIDAD %', 'FACTOR CONDICIÓN K',
                                    'CONSUMO TOTAL ALIMENTO', 'BIOMASA FINAL', 'DENSIDAD KG M3',
                                    'BIOMASA NETA', 'FCA', 'SGR', 'GPD gramos', 'COSTO PUNTO CONVERSIÓN']

        data_calculada = data_calculada.transpose() 
        data_calculada['Variable'] = data_calculada.index
        data_calculada.columns = ['Valor', 'Variable']
        data_calculada = data_calculada[['Variable', 'Valor']]

        data_resumen = data_resumen.transpose() 
        data_resumen['Variable'] = data_resumen.index
        data_resumen.columns = ['Valor', 'Variable']
        data_resumen = data_resumen[['Variable', 'Valor']]
        resumen = dbc.Table.from_dataframe(data_resumen, striped = True, bordered = True, hover = True)

        dt_traslado_sal = dt_traslado.copy()

        dt_traslado['estanque_destino'] = dt_traslado['id_estanque_destino']
        del dt_traslado['id_estanque_destino']

        dt_traslado_sal.drop(columns = ['id_estanque_destino', 'id_lote', 'estanque_origen'], inplace = True)
        dt_traslado_sal.columns = ['FECHA', 'CANTIDAD', 'PESO PROMEDIO', 'VACUNA', 'ESTANQUE DESTINO', 'OBSERVACIONES']
        dt_traslado['dias_cultivo'] = data['dias_cultivo'].values[0]
        dt_traslado = dt_traslado[['fecha', 'dias_cultivo', 'cantidad', 'peso_promedio', 'vacuna', 'estanque_origen', 
                                    'estanque_destino', 'id_lote', 'observaciones']]

        dt_pescas_sal = dt_pescas.copy()
        dt_pescas_sal = dt_pescas_sal[['fecha', 'cantidad', 'biomasa', 'peso_visceras', 'biomasa_neta', 'observaciones']]
        dt_pescas_sal.columns = ['FECHA', 'CANTIDAD', 'BIOMASA', 'PESO VISCERAS', 'BIOMASA NETA', 'OBSERVACIONES']
        dt_pescas['dias_cultivo'] = data['dias_cultivo'].values[0]
        dt_pescas = dt_pescas[['fecha', 'dias_cultivo', 'cantidad', 'biomasa', 'peso_visceras', 'biomasa_neta', 'id_lote', 'id_estanque', 'observaciones']]

        dt_alimento_sal = dt_alimento.copy()
        dt_alimento_sal = dt_alimento_sal[['fecha', 'fecha_inicial', 'fecha_final', 'tipo_alimento', 'precio_b_40_kg', 'kg_real', 'observaciones']]
        dt_alimento_sal.columns = ['FECHA', 'FECHA INICIAL', 'FECHA FINAL', 'TIPO ALIMENTO', 'PRECIO Bx40KG', 'KG REAL', 'OBSERVACIONES']

        dt_alimento['dias_cultivo'] = data['dias_cultivo'].values[0]
        dt_alimento = dt_alimento[['fecha', 'fecha_inicial', 'fecha_final', 'dias_cultivo', 'tipo_alimento', 'precio_b_40_kg', 'kg_real', 'id_lote', 'id_estanque', 'observaciones']]
        
        
        return [f'Información validada con éxito', 'success', True, True, [resumen], 
                data.to_json(orient = 'split', date_format = 'iso'), 
                dt_traslado.to_json(orient = 'split', date_format = 'iso'),
                dt_alimento.to_json(orient = 'split', date_format = 'iso'),
                dt_pescas.to_json(orient = 'split', date_format = 'iso'),
                dbc.Table.from_dataframe(dt_traslado_sal, striped = True, bordered = True, hover = True, responsive = True),
                dbc.Table.from_dataframe(dt_pescas_sal, striped = True, bordered = True, hover = True, responsive = True),
                dbc.Table.from_dataframe(dt_alimento_sal, striped = True, bordered = True, hover = True, responsive = True),
                dbc.Table.from_dataframe(data_calculada, striped = True, bordered = True, hover = True, responsive = True)]

    except Exception as e:
        print(e)
        return [f'Error al validar la información', 'warning', True, False] + [no_update]*salidas


# actualizar linea genetica
@app.callback([Output('genetica_ingreso_col', 'style'),
               Output('genetica_ingreso', 'options')],
               Input('especie_ingreso', 'value'))
def actualizar_linea(especie):
    if especie != 'TN':
        return [{'display': 'none'}, [{'label': 'Seleccione una especie', 'value': None}]]
    else:
        sql = f'SELECT linea FROM linea_genetica WHERE especie = "{especie}"'
        try:
            linea = get_data(sql)
            options = [{'label': i, 'value': i} for i in linea['linea']]
            return [{'display': 'inline'}, options]
            
        except Exception as e:
            print('ERROR CONSULTAR BD LINEA GENETICA', e)
    return [no_update]*2

#actualizar opciones vacunacion
@app.callback(Output('vacunacion_traslado', 'options'),
              Input('especie_ingreso', 'value'))
def actualizar_vacunacion(especie):
    if especie in ['MR', 'TN']:
        sql = f'SELECT tipo FROM vacunas WHERE especie = "{especie}"'
        try:
            vacunas = get_data(sql)

            if vacunas.empty:
                return [{'label': 'Sin registros', 'value': None}]
            else:
                return [{'label': i, 'value': i} for i in vacunas['tipo']]

        except Exception as e:
            print('ERROR AL CARGAR INFO VACUNAS', e)
        
    else:
        return [{'label': 'Seleccione una especie', 'value': None}]

# actualizar tabla variable liquidacion lote
@app.callback(Output('var_lote_liquidado', 'children'),
              Input('validar_seguimiento_estanque', 'n_clicks'),
             [State('cerrar_lote', 'value'),
              State('data_val_se', 'data')])
def UpdateTableLiq(n, cerrar, data):
    if n is None:
        return no_update
    if bool(cerrar):
        dt = pd.read_json(data, orient = 'split')

        dt = dt[['numero_lotes_año', 'toneladas_ha_año', 'costo_kg_alimento']]
        dt.columns = ['LOTES/AÑO', 'TONELADAS ha/AÑO', 'COSTO KG ALIMENTO']
        dt = dt.transpose() 
        dt['Variable'] = dt.index
        dt.columns = ['Valor', 'Variable']
        dt = dt[['Variable', 'Valor']]

        return html.Div([
            html.H4('VARIABLES LIQUIDACIÓN'),
            dbc.Table.from_dataframe(dt, striped = True, bordered = True, hover = True)
            ])
    else:  
        return ''


# desactivar ingresos despues de enviar seguimiento
@app.callback([Output('seg_alimentacion', 'value'),
               Output('seg_crecimiento', 'value'),
               Output('mortalidad', 'value'),
               Output('translado', 'value'),
               Output('Pesca', 'value'),
               Output('cerrar_lote', 'value'), 
               Output('lote_nuevo', 'value')],
               Input('enviar_seguimiento_estanque', 'n_clicks'),
               State('cerrar_lote', 'value'))
def desactivar_switch(n, cerrar):
    if n is None:
        return [[]]*6 + [no_update]
    elif bool(cerrar):
        return [[]]*6 + ['Si']
    else:
        return [[]]*6 + [no_update]


# cambiar valores alimentacion, crecimiento e inventario al enviar reporte
@app.callback([Output('marca_alimento', 'value'),
               Output('n_fuentes_alimento', 'value'),
               Output('real_ingreso', 'value'),
               Output('longitud_crecimiento', 'value'),
               Output('mortalidad_ingreso', 'value'),
               Output('peso_mortalidad_ingreso', 'value'),
               Output('translado_ingreso', 'value'),
               Output('vacunacion_traslado', 'value'),
               Output('numero_pesca_ingreso', 'value')],
               Input('enviar_seguimiento_estanque', 'n_clicks'))
def reset_values(n):
    if n is None:
        return [no_update]*9
    else:
        return [None, 1, None, None, None, None, None, 1, 1]


## enviar información seguimiento a estanques
@app.callback([Output('alert_enviar_seguimiento_estanque', 'children'),
               Output('alert_enviar_seguimiento_estanque', 'color'),
               Output('alert_enviar_seguimiento_estanque', 'is_open')],
               Input('enviar_seguimiento_estanque', 'n_clicks'),
               [State('translado', 'value'),
                State('Pesca', 'value'),
                State('lote_nuevo', 'value'),
                State ('data_val_se', 'data'),
                State('data_traslado', 'data'),
                State('data_alimentacion', 'data'),
                State('data_pesca', 'data'),
                State('cerrar_lote', 'value'),
                State('seg_alimentacion', 'value')])
def enviar_seguimiento_estanque(n, traslado, pesca, lote_nuevo, data, data_t, data_a, data_p, cerrar, registrar_am):
    if n is None:
        return [no_update]*3
    try:
        data = pd.read_json(data, orient = 'split')
        data_t = pd.read_json(data_t, orient = 'split')
        data_a = pd.read_json(data_a, orient = 'split')
        data_p = pd.read_json(data_p, orient = 'split')
        data['fecha'] = data['fecha'].apply(lambda x: x.split('T')[0])
        data_t['fecha'] = data_t['fecha'].apply(lambda x: x.split('T')[0])
        #data_a['fecha'] = data_a['fecha'].apply(lambda x: x.split('T')[0])
        data_p['fecha'] = data_p['fecha'].apply(lambda x: x.split('T')[0])


    except Exception as e:
        print(e)
        return ['Error al cargar datos', 'warning', True]

    if lote_nuevo == ['Si']:
        data_lote = data[['id_lote', 'lote', 'especie_ingreso', 'linea_genetica', 'peso_siembra',
                          'talla', 'numero_inicial_peces', 'fecha_siembra', 'id_estanque',
                          'id_granja', 'nit_cliente']].copy()
        data_lote['cerrado'] = pd.Series(['No'])
        data_lote.columns = ['id_lote', 'nombre_lote', 'especie_sembrada', 'linea_genetica', 'peso_siembra_gr', 'talla_cm',
                        'numero_inicial_peces', 'fecha_siembra', 'id_estanque', 'id_granja', 'nit_cliente',
                        'cerrado']
        try:
            insert_dataframe(data_lote, 'lotes')
        except Exception as e:
            print(e)
            return ['Error al registrar lote', 'warning', True]

    try:
        insert_dataframe(data, 'seguimiento_estanques')
        if registrar_am == ['Si']:
            insert_dataframe(data_a, 'alimento')
        if pesca == ['Si']:
            insert_dataframe(data_p, 'pescas') 
        if traslado == ['Si']:            
            result = crear_traslado(data, data_t)
            insert_dataframe(data_t, 'traslados')
        
        if cerrar == ['Si']:
            try:
                result = cerrar_lote_(lote = data['id_lote'].values[0])
                print('resultado', result)
            except Exception as e:
                print(e)
        return ['Información enviada con éxito', 'success', True]
    except Exception as e:
        print('enviar seguimiento', e)
        return ['Error al enviar la información', 'warning', True]


# ACTUALIZAR FECHAS EN FUNCION DE LA FECHA DE MUESTREO
@app.callback([Output('rango_fecha_alm', 'start_date'),
               Output('rango_fecha_alm', 'end_date'),
               Output('rango_fecha_cre', 'start_date'),
               Output('rango_fecha_cre', 'end_date'),
               Output('rango_fecha_mort', 'start_date'),
               Output('rango_fecha_mort', 'end_date'),],
               Input('fecha_ingreso', 'date'))
def update_dates(date):
    return [date]*6

## actualizar fecha ultimo muestreo y peso
@app.callback([Output('fecha_muestreo_anterior', 'children'),
               Output('peso_prom_muestreo_anterior', 'children')],
             [Input('lote_ingreso', 'value'),
              Input('lote_nuevo', 'value'),
              Input('estanque_ingreso', 'value')])
def update_fecha_ma(lote, nuevo, estanque):
    
    if nuevo == ['Si']:

        return [f'FECHA MUESTREO ANTERIOR: {datetime.today().date()}', f'PESO PROMEDIO ANTERIOR: -']

    if lote is None or lote == '':

        return ['FECHA MUESTREO ANTERIOR: -', f'PESO PROMEDIO ANTERIOR: -']

    if not bool(estanque):

        return ['FECHA MUESTREO ANTERIOR: -', f'PESO PROMEDIO ANTERIOR: -']

    try:
        lote = json.loads(lote)['value']
        estanque = json.loads(estanque)['value']

    except Exception as e:
        print(e)
        lote = 0
        return ['FECHA MUESTREO ANTERIOR: -', f'PESO PROMEDIO ANTERIOR: -']

    if not bool(lote):
        return ['FECHA MUESTREO ANTERIOR: -', f'PESO PROMEDIO ANTERIOR: -']
    
    if not bool(estanque):
        return ['FECHA MUESTREO ANTERIOR: -', f'PESO PROMEDIO ANTERIOR: -']
    
    sql = f'SELECT id, fecha, peso_promedio FROM seguimiento_estanques WHERE id_lote = {lote} AND id_estanque = {estanque} ORDER BY id DESC LIMIT 1'

    try:
        dt = get_data(sql)
        
    except Exception as e:
        print('Error muestreo anterior', e)
        return ['FECHA MUESTREO ANTERIOR: -', f'PESO PROMEDIO ANTERIOR: -']
    if dt.empty:
        return ['FECHA MUESTREO ANTERIOR: -', f'PESO PROMEDIO ANTERIOR: -']

    ps_anterior = dt.peso_promedio.values[0]
    return [f'FECHA MUESTREO ANTERIOR: {dt.fecha.values[0]}', f'PESO PROMEDIO ANTERIOR: {ps_anterior if bool(ps_anterior) else "-"}']

#actualizar fecha mortalidad anterior
@app.callback([Output('fecha_mort_anterior', 'children'),
               Output('ac_mort_anterior', 'children')],
             [Input('lote_ingreso', 'value'),
              Input('mortalidad', 'value'),
              Input('estanque_ingreso', 'value')])
def update_fecha_mort(lote, mortalidad, estanque):
    if not bool(mortalidad):
        return ['FECHA MORTALIDAD ANTERIOR: -', 'MORTALIDAD ACUMULADA: -']

    if not bool(lote):
        return ['FECHA MORTALIDAD ANTERIOR: -', 'MORTALIDAD ACUMULADA: -']

    try:
        lote = json.loads(lote)['value']
        estanque = json.loads(estanque)['value']
    except Exception as e:
        print(e)
        lote = 0

    if not bool(lote):
        return ['FECHA MORTALIDAD ANTERIOR: -', 'MORTALIDAD ACUMULADA: -']
    
    sql = f'SELECT id, fecha, numero_mortalidad FROM seguimiento_estanques WHERE id_lote = {lote} AND id_estanque = {estanque} ORDER BY id DESC'

    try:
        dt = get_data(sql)
    except Exception as e:
        print(e)
        return ['FECHA MORTALIDAD ANTERIOR: -', 'MORTALIDAD ACUMULADA: -']
    if dt.empty:
        return ['FECHA MORTALIDAD ANTERIOR: -', 'MORTALIDAD ACUMULADA: -']

    return [f'FECHA MORTALIDAD ANTERIOR: {dt.fecha.values[0]}', f'MORTALIDAD ACUMULADA: {dt.numero_mortalidad.sum()}']

#actualizar fecha traslado anterior
@app.callback(Output('fecha_tras_anterior', 'children'),
             [Input('lote_ingreso', 'value'),
              Input('translado', 'value'),
              Input('estanque_ingreso', 'value')])
def update_fecha_tras(lote, traslado, estanque):
    if not bool(traslado):
        return ['FECHA TRASLADO ANTERIOR: -']

    if not bool(lote):
        return ['FECHA TRASLADO ANTERIOR: -']

    try:
        lote = json.loads(lote)['value']
        estanque = json.loads(estanque)['value']
    except Exception as e:
        print(e)
        lote = 0

    if not bool(lote):
        return ['FECHA TRASLADO ANTERIOR: -']
    
    sql = f'SELECT id, fecha FROM traslados WHERE id_lote = {lote} AND estanque_origen = {estanque} ORDER BY id DESC LIMIT 1'
    

    try:
        dt = get_data(sql)
    except Exception as e:
        print(e)
        return ['FECHA TRASLADO ANTERIOR: -']
    if dt.empty:
        return ['FECHA TRASLADO ANTERIOR: -']

    return [f'FECHA TRASLADO ANTERIOR: {dt.fecha.values[0]}']


#actualizar fecha pesca anterior
@app.callback(Output('fecha_pesc_anterior', 'children'),
             [Input('lote_ingreso', 'value'),
              Input('Pesca', 'value'),
              Input('estanque_ingreso', 'value')])
def update_fecha_pesca(lote, pesca, estanque):
    if not bool(pesca):
        return ['FECHA PESCA ANTERIOR: -']

    if not bool(lote):
        return ['FECHA PESCA ANTERIOR: -']

    try:
        lote = json.loads(lote)['value']
        estanque = json.loads(estanque)['value']
    except Exception as e:
        print(e)
        lote = 0

    if not bool(lote):
        return ['FECHA PESCA ANTERIOR: -']
    
    sql = f'SELECT id, fecha FROM pescas WHERE id_lote = {lote} AND id_estanque = {estanque} ORDER BY id DESC LIMIT 1'

    try:
        dt = get_data(sql)
    except Exception as e:
        print(e)
        return ['FECHA PESCA ANTERIOR: -']
    if dt.empty:
        return ['FECHA PESCA ANTERIOR: -']

    return [f'FECHA PESCA ANTERIOR: {dt.fecha.values[0]}']


### actualizacion dias desde ultimo registro y cantidad alimento
@app.callback([Output('dias_ultima_fecha', 'children'),
               Output('alimento_ultima_fecha', 'children')],
              [Input('lote_ingreso', 'value'),
               Input('lote_nuevo', 'value'),
               Input('estanque_ingreso', 'value'),
               Input('fecha_ingreso', 'date')])
def alimento_ult_fecha(lote, nuevo, estanque, fecha_ingreso):

    if nuevo == ['Si']:
        return ['DÍAS CULTIVO CONSOLIDADO: -', 'KG ALIMENTO CONSOLIDADO: -']

    if lote is None or lote == '':
        return ['DÍAS CULTIVO CONSOLIDADO: -', 'KG ALIMENTO CONSOLIDADO: -']

    try:
        lote = json.loads(lote)['value']
        estanque = json.loads(estanque)['value']
    except Exception as e:
        print(e)
        lote = 0
        estanque = 0

    if lote is None or lote == '':
        return ['DÍAS CULTIVO CONSOLIDADO: -', 'KG ALIMENTO CONSOLIDADO: -']

    try:
        sql = f'SELECT fecha_final, kg_real FROM alimento WHERE id_lote = {lote} AND id_estanque = {estanque}' # AND fecha IN (SELECT MAX(fecha)
        sql_2 = f'SELECT fecha_siembra FROM lotes WHERE id_lote = {lote}'
        dt = get_data(sql)
        dt_fecha_siem = get_data(sql_2)
    except Exception as e:
        print(e)
        return ['DÍAS CULTIVO CONSOLIDADO: -', 'KG ALIMENTO CONSOLIDADO: -']

    if dt.empty:
        kg_alimento = 0
        f_ultima = datetime.today().date()
    else:
        f_max = dt['fecha_final'].values[-1]
        f_ultima = datetime.strptime(str(f_max), '%Y-%m-%d').date()
        #f_min = datetime.strptime(str(dt['fecha_final'].values[0]), '%Y-%m-%d').date()
        kg_alimento = round(dt['kg_real'].sum(), 2)
    if dt_fecha_siem.empty:
        dias = 0
    else:
        f_ingreso = datetime.strptime(fecha_ingreso, '%Y-%m-%d').date()
        f_siembra = dt_fecha_siem['fecha_siembra'].values[0]

        try:
            dias = int((f_ingreso - f_siembra).days)
            if dias < 0:
                dias = 0
        except Exception as e:
            print(e)
            dias = None



    return [f'DÍAS CULTIVO CONSOLIDADO: {dias}', f'KG ALIMENTO CONSOLIDADO: {kg_alimento}']    

# callback, actualizar tipo aireador, aireacion y fase de cultivo
@app.callback([Output('tipo_aireador_ingreso', 'value'),
               Output('aireacion_ingreso', 'value'),
               Output('etapa_cultivo_ingreso', 'value')],
               Input('estanque_ingreso', 'value'),
               [State('lote_ingreso', 'value'),
                State('lote_nuevo', 'value')],)
def actualizar_aaf(estanque, lote, nuevo):
    if not bool(estanque):
        return [None]*3
    if bool(nuevo):
        return [None]*3
    else:
        if lote is None or lote == '':
            return [None]*3
        id_lote = json.loads(lote)['value']
        id_estanque = json.loads(estanque)['value']
        try:
            sql = f'SELECT id, tipo_aireador, aireacion, fase_cultivo FROM seguimiento_estanques WHERE id_lote = {id_lote} AND id_estanque = {id_estanque} ORDER BY id DESC LIMIT 1'
            dt = get_data(sql)

            if dt.empty:
                return [None]*3    
            else:
                return [dt['tipo_aireador'][0], dt['aireacion'][0], dt['fase_cultivo'][0]]
        except Exception as e:
            print('ERROR actualizar_aaf', e)
            return [None]*3

## callback tipo_alimento_ingreso
@app.callback(Output('tipo_alimento_ingreso', 'options'),
              Input('marca_alimento', 'value'))
def tipo_alimento(n):
    if n is None or len(n) == 0:
        return None
    labels = list()
    values = list()
    for i in n:
        values.extend(marcas_alimento[i])
        labels.extend(list(map(lambda x: x + ' ' + i, marcas_alimento[i])))

    return [{'label': l, 'value': v} for l, v in zip(labels, values)]

# CALLBACK OCULTAR CAMPO VALOR AIREACION 
@app.callback(Output('aireacion_ingreso_col', 'style'),
              Input('tipo_aireador_ingreso', 'value'))
def hidden_aireador(tipo):
    if tipo == None:
        return {'display': 'inline'}
    if tipo == 'NINGUNO':
        return {'display': 'none'}
    else:
        return {'display': 'inline'}

# callback actualizar campos peso y talla cuando lote es nuevo
# @app.callback([Output('real_ingreso', 'value'),
#                Output('longitud_crecimiento', 'value')],
#                [Input('peso_siembra_ingreso', 'value'),
#                 Input('talla_ingreso', 'value'),
#                 Input('lote_nuevo', 'value'),
#                 Input('enviar_seguimiento_estanque', 'n_clicks')])
# def updata_fields(peso, talla, nuevo, n):
#     if nuevo == ['Si']:
#         return [peso, talla]
#     else:
#         return [None, None]

# callback ocultar campos alimentacion
@app.callback([Output('feeding_fields_alimentacion', 'style'),
               Output('feeding_fields_crecimiento', 'style'),
               Output('feeding_fields_inventario', 'style')],
              Input('lote_nuevo', 'value'))
def hidden_feeding_fields(nuevo):
    if nuevo == ['Si']:
        return [{'display': 'none'}]*3
    else:
        return [{'display': 'inline'}]*3

# callback ocultar campos alimentacion 2
@app.callback(Output('feeding_fields_2', 'style'),
              Input('seg_alimentacion', 'value'))
def hidden_feeding_fields_2(registrar):
    if registrar != ['Si']:
        return {'display': 'none'}
    else:
        return {'display': 'inline'}

# calback cambiar valor registrar alimentacion cuando lote es nuevo
# @app.callback(Output('seg_alimentacion', 'value'),
#               Input('lote_nuevo', 'value'))
# def changeValue(lote):
#     if lote == ['Si']:
#         return None
#     else:
#         return no_update

### CALLBACKS PESTAÑA CONSULTAR INFORMACION

### SEGUIMIENTO SEMANAL
## reporte
## generar reporte 1 ss
@app.callback([Output('alert_generar_reporte_1_ss', 'children'),
               Output('alert_generar_reporte_1_ss', 'color'),
               Output('alert_generar_reporte_1_ss', 'is_open'),
               Output('modal_ss_1', 'is_open'),
               Output('modal_ss_1_contenido', 'children'),
               Output('data_reporte_1_ss', 'data')],
               Input('generar_reporte_1_ss', 'n_clicks'),
               [State('user_info', 'data')] + [State(i, 'value') for i in ids_consulta_ss])
def gen_reporte_1(n, data, gerente, nit_cliente, granja, año, lote):
    if n is None:
        raise dash.exceptions.PreventUpdate()
    user = pd.read_json(data, orient = 'split')
    rol = user['rol_usuario'].values[0]
    doc_id = user['doc_id'].values[0]
    pais = user['pais'].values[0]
    usuario = user['nombre'].values[0]
    if rol == 'administrador':
        if gerente is None or gerente == '':
            return ['Gerente de Zona no  valido', 'warning', True, no_update, no_update, no_update]
    if rol in ['gerente', 'especialista'] or rol == 'administrador':
        if nit_cliente is None or nit_cliente == '':
            return ['Cliente no  valido', 'warning', True, no_update, no_update, no_update]
    if rol in ['gerente', 'especialista']:
        gerente = doc_id
    if rol == 'cliente':
        nit_cliente = doc_id
    if rol == 'administrador':
        nit_cliente = json.loads(nit_cliente)['value']
        #gerente = pd.read_json(data2, orient = 'split')['gerente_zona'].unique[0]
    ids = [granja, año, lote]
    ids_label = ['Granja', 'Año', 'Lote']
    for i in range(len(ids)):
        if isinstance(ids[i], str) or ids[i] is None or ids[i] == [None] or len(ids[i]) == 0:
            return [f'{ids_label[i]} no valida', 'warning', True, no_update, no_update, no_update]
    año_sql = '('
    for i in año:
        año_sql = año_sql + str(i)
        if int(i) == año[-1]:
            año_sql = año_sql + ')'
        else:
            año_sql = año_sql + ','
    
    granja_sql = '('
    for i in granja:
        granja_sql = granja_sql + str(i)
        if int(i) == granja[-1]:
            granja_sql = granja_sql + ')'
        else:
            granja_sql = granja_sql + ','
    
    lote_sql = '('
    for i in lote:
        lote_sql = lote_sql + str(i)
        if int(i) == lote[-1]:
            lote_sql = lote_sql + ')'
        else:
            lote_sql = lote_sql + ','

    sql = f'''SELECT * FROM seguimiento_estanques WHERE nit_cliente = {nit_cliente} AND id_granja IN {granja_sql} AND id_lote IN {lote_sql};'''

    data = get_data(sql)
    if data.empty:
        return ['Sin registros', 'warning', True, False, no_update, no_update]

    try:
        fecha = datetime.today().date()
        trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Generar reporte seguimiento estanque')
    except Exception as e:
        print(e)        
    return ['Información consultada con éxito', 'success', True, True, ss_report_1(data, nit_cliente, usuario, granja, año, lote), data.to_json(date_format='iso', orient = 'split')]
# 
#dbc.Table.from_dataframe(data, striped = True, bordered = True, hover = True)



# cargar tabla reporte seguimiento semanal
@app.callback([Output('alert_cargar_tabla_consulta_ss', 'children'),
               Output('alert_cargar_tabla_consulta_ss', 'color'),
               Output('alert_cargar_tabla_consulta_ss', 'is_open'),
               Output('tabla_consulta_ss', 'children'),
               Output('modal_data_ss', 'is_open'),
               Output('data_download_ss', 'data')],
               Input('cargar_tabla_consulta_ss', 'n_clicks'),
              [State('user_info', 'data')] + [State(i, 'value') for i in ids_consulta_ss])
def cargar_tabla_ss(n, data, gerente, nit_cliente, granja, año, lote):
    if n is None:
        raise dash.exceptions.PreventUpdate()
    user = pd.read_json(data, orient = 'split')
    rol = user['rol_usuario'].values[0]
    usuario = user['nombre'].values[0]
    doc_id = user['doc_id'].values[0]
    pais = user['pais'].values[0]
    if rol == 'administrador':
        if gerente is None or gerente == '':
            return ['Gerente de Zona no  valido', 'warning', True, no_update, no_update, no_update]
    if rol == 'gerente' or rol == 'administrador':
        if nit_cliente is None or nit_cliente == '':
            return ['Cliente no  valido', 'warning', True, no_update, no_update, no_update]
    if rol == 'gerente':
        gerente = doc_id
    if rol == 'cliente':
        nit_cliente = doc_id
    else:
        nit_cliente = json.loads(nit_cliente)
        if rol == 'administrador':
            nit_cliente = nit_cliente['value']
        else:
            nit_cliente = nit_cliente
        #gerente = pd.read_json(data2, orient = 'split')['gerente_zona'].unique[0]
    ids = [granja, año, lote]
    ids_label = ['Granja', 'Año', 'Lote']
    for i in range(len(ids)):
        if isinstance(ids[i], str) or ids[i] is None or ids[i] == [None] or len(ids[i]) == 0:
            return [f'{ids_label[i]} no valida', 'warning', True, no_update, no_update, no_update]
    año_sql = '('
    for i in año:
        año_sql = año_sql + str(i)
        if int(i) == año[-1]:
            año_sql = año_sql + ')'
        else:
            año_sql = año_sql + ','
    
    granja_sql = '('
    for i in granja:
        granja_sql = granja_sql + str(i)
        if int(i) == granja[-1]:
            granja_sql = granja_sql + ')'
        else:
            granja_sql = granja_sql + ','
    
    lote_sql = '('
    for i in lote:
        lote_sql = lote_sql + str(i)
        if int(i) == lote[-1]:
            lote_sql = lote_sql + ')'
        else:
            lote_sql = lote_sql + ','

    # if comparacion == '25% MEJORES CLIENTES ITALCOL':
    #     sql = f'''SELECT seguimiento_semanal.*, clientes.pais FROM seguimiento_semanal INNER JOIN clientes ON  clientes.nit = seguimiento_semanal.nit_cliente WHERE clientes.pais = '{pais}' AND seguimiento_semanal.año IN {año_sql};'''
    # else:
    sql = f'''SELECT * FROM seguimiento_estanques WHERE nit_cliente = {nit_cliente} AND id_granja IN {granja_sql} AND id_lote IN {lote_sql};'''
    try:
        data = get_data(sql)
        # if comparacion == '25% MEJORES CLIENTES ITALCOL':
        #     data.drop('pais', axis = 1, inplace = True)
        #     data_filter = data.loc[data['nit_cliente'].isin([int(nit_cliente)])&
        #                             data['id_granja'].isin(granja) &
        #                             data['año'].isin(año) &
        #                             data['id_lote'].isin(lote) &
        #                             data['linea'].isin(linea) &
        #                             data['sexo'].isin(sexo) &
        #                             data['edad_dias'].isin(edad)].drop(['id', 'gerente_zona', 'id_granja', 'id_lote', 'id_galpon'], axis = 1)
        data_resumen = data.copy()
        if data_resumen.empty:
            return ['Sin registros', 'warning', True, no_update, False, no_update]
        data_resumen.drop(['id', 'gerente_zona', 'id_granja', 'id_lote', 'id_estanque', 'mortalidad'], axis = 1, inplace = True)
        data_resumen.columns = ['FECHA', 'AÑO', 'MES', 'SEMANA AÑO', 'GERENTE', 'NIT CLIENTE', 
                                'CLIENTE', 'DEPARTAMENTO', 'MUNICIPIO', 'GRANJA', 'LOTE', 
                                'FECHA SIEMBRA', 'EDAD POR PESO', 'ESTANQUE', 
                                'TIPO ESTANQUE', 'ESPECIE', 'LINEA GENÉTICA', 'PESO SIEMBRA', 'TALLA', 'NUMERO INICIAL DE PECES', 
                                'AREA m2', 'VOLUMEN m3', 'TIPO AIREADOR','AIREACIÓN', 'FASE CULTIVO', 
                                'FECHA INICIAL CRE', 'FECHA FINAL CRE', 'PESO PROMEDIO (g)', 
                                'LONGITUD PROMEDIO (cm)', 'FECHA INICIAL MORT', 'FECHA FINAL MORT', 'MORTALIDAD',
                                'PESO MORTALIDAD (kg)', 'SALDO PECES', 'DIAS CULTIVO',
                                'BIOMASA INICIAL KG', 'MORTALIDAD %', 'FACTOR CONDICIÓN K',
                                'CONSUMO TOTAL ALIMENTO', 'BIOMASA FINAL', 'DENSIDAD KG M2',
                                'BIOMASA NETA', 'FCA', 'SGR', 'GPD', 'NÚMERO LOTES AÑO',
                                'TONELADAS ha AÑO', 'COSTO PUNTO CONVERSIÓN', 'COSTO KG ALIMENTO']
        #table = dashtable(archivo = data_resumen, tipo = 'ss')
        table = dbc.Table.from_dataframe(data_resumen, striped = True, bordered = True, hover = True)    
        try:
            fecha = datetime.today().date()
            trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Consultar Excel seguimiento estanques')
        except Exception as e:
            print(e)        
        return ['Información consultada con éxito', 'success', True, table, True, data_resumen.to_json(date_format = 'iso', orient = 'split')]
    except Exception as e:
        print(e)
        return ['Error al consultar la información', 'warning', True, no_update, no_update, no_update]

# actualizar campo cliente en funcion de gerente
@app.callback(Output('cliente_consulta', 'options'),
              Input('gerente_consulta', 'value'),
              State('user_info', 'data'))
def clienteGerente_(gerente, data):
    usuario = pd.read_json(data, orient = 'split')
    rol = usuario['rol_usuario'].values[0]
    if gerente is None and rol == 'administrador':
        return [{'label': 'Por favor seleccione un gerente', 'value': ''}]
    if rol == 'administrador':
        sql = f'''SELECT nit, nombre_cliente FROM clientes WHERE gerente_zona = '{gerente}';'''
        try:
            clientes = get_data(sql) 
        except Exception as e:
            print(e)
            return [{'label': 'Error al consultar clientes', 'value': ''}]
        if clientes.empty:
            return [{'label': 'Sin registros en clientes', 'value': ''}]
        clientes.sort_values(by = ['nombre_cliente'], inplace = True)
        clientes.reset_index(drop = True, inplace = True)
        return [{"label": clientes["nombre_cliente"][i], "value": '{' + f'"label": "{clientes["nombre_cliente"][i]}", "value": "{clientes["nit"][i]}"' + '}'} for i in range(clientes['nit'].shape[0])]
    else:
        return no_update


# actualizar campo granja en funcion de cliente
@app.callback(Output('granja_consulta', 'options'),
              Input('cliente_consulta', 'value'),
              State('user_info', 'data'))
def granjaCliente_(cliente, data):
    usuario = pd.read_json(data, orient = 'split')
    rol = usuario['rol_usuario'].values[0]
    doc_id = usuario['doc_id'].values[0]
    if rol == 'cliente':
        return no_update
    if cliente is None or cliente == '':
        return [{'label': 'Por favor seleccione un cliente', 'value': ''}]
    cliente = json.loads(cliente)
    if rol == 'administrador':
        cliente = cliente['value']
    else:
        cliente = cliente
    sql = f'''SELECT id_granja, granja FROM seguimiento_estanques WHERE nit_cliente = {cliente};'''
    try:
        granjas = get_data(sql)
    except Exception as e:
        print(e)
        return [{'label': 'Error al consultar granjas', 'value': ''}]
    if granjas.empty:
        return [{'label': 'Sin registros de granjas', 'value': ''}]
    granjas.drop_duplicates(inplace = True)
    granjas.sort_values(by = ['granja'], inplace = True)
    granjas.reset_index(drop = True, inplace = True)
    return [{"label": granjas["granja"][i], "value": granjas["id_granja"][i]} for i in range(granjas.shape[0])]
            
# actualizar año
@app.callback([Output('año_consulta', 'options'),
               Output('data_gal_consulta', 'data')],
              Input('granja_consulta', 'value'),
              [State('cliente_consulta', 'value'),
               State('user_info', 'data')])
def updateYear(granja, cliente, data):
    if granja == None or granja == [None] or granja == '' or len(granja) == 0:
        return [[{'label': 'Por favor seleccione una granja', 'value': ''}], no_update]
    usuario = pd.read_json(data, orient = 'split')
    rol = usuario['rol_usuario'].values[0]
    doc_id = usuario['doc_id'].values[0]
    if rol == 'cliente':
        cliente = doc_id
    else:
        cliente = json.loads(cliente)
        if rol == 'administrador':
            cliente = cliente['value']
        else:
            cliente = cliente
    granja_sql = '('
    for i in granja:
        granja_sql = granja_sql + str(i)
        if int(i) == granja[-1]:
            granja_sql = granja_sql + ')'
        else:
            granja_sql = granja_sql + ','
    sql = f'SELECT DISTINCT año, id_granja, id_lote, lote  FROM seguimiento_estanques WHERE nit_cliente = {cliente} AND id_granja IN {granja_sql}'
    try:
        data_año = get_data(sql)
    except Exception as e:
        print(e)
        return [[{'label': 'Error al consultar años', 'value': ''}], no_update]
    if data_año.empty:
        return [[{'label': 'Sin registros', 'value': ''}], no_update]
    #data_año.drop_duplicates(axis = 1, inplace = True)
    data_año.sort_values(by = ['año'], inplace = True)
    data_año.reset_index(drop = True, inplace = True)
    years = data_año['año'].unique()
    return [[{'label': i, 'value': i} for i in years], data_año.to_json(date_format='iso', orient = 'split')]

## actualizar lote
@app.callback(Output('lote_consulta', 'options'),
             Input('año_consulta', 'value'),
             State('data_gal_consulta', 'data'))
def update_lote(año, data):
    if año is None or año == '' or len(año) == 0:
        return [{'label': 'Por favor seleccione un año', 'value': ''}]
    try:
        data_lote = pd.read_json(data, orient = 'split')
    except Exception as e:
        print(e)
        return [{'label': 'Error al consular datos', 'value': ''}]
    lotes = data_lote.loc[data_lote['año'].isin(año)][['id_lote', 'lote']]
    lotes.drop_duplicates(inplace = True)
    lotes.reset_index(drop = True, inplace = True)
    return [{'label': lotes['lote'][i], 'value': lotes['id_lote'][i]} for i in range(lotes.shape[0])]


## DESCARGAR EXCEL SEGUIMIENTO SEMANAL
@app.callback([Output('download_excel_ss', 'data'),
               Output('alert_descargar_tabla_consulta_ss', 'children'),
               Output('alert_descargar_tabla_consulta_ss', 'color'),
               Output('alert_descargar_tabla_consulta_ss', 'is_open'),],
              Input('descargar_tabla_consulta_ss', 'n_clicks'),
             [State('data_download_ss', 'data'),
              State('cliente_consulta', 'value'),
              State('user_info', 'data')])
def downloadExcelSs(n, data, nit, data_user):
    if n is None:
        raise dash.exceptions.PreventUpdate()    
    user = pd.read_json(data_user, orient = 'split')
    rol = user['rol_usuario'].values[0]
    doc_id = user['doc_id'].values[0]
    if rol == 'cliente':
        nit = doc_id
    else:
        try:
            nit = json.loads(nit)
            nit = nit['label']
        except Exception as e:
            print('json load nit:', e)

    ###################
    try:
        dt = pd.read_json(data, orient = 'split')
        dt.fillna('', inplace = True)
        dt['FECHA'] = dt['FECHA'].apply(lambda x: x.split('T')[0])
        dt['FECHA SIEMBRA'] = dt['FECHA SIEMBRA'].apply(lambda x: x.split('T')[0])
        try:
            fecha = datetime.today().date()
            trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Descargar Excel seguimiento estanques')
            try:
                dt['FECHA INICIAL CRE'] = dt['FECHA INICIAL CRE'].apply(lambda x: str(x).split('T')[0])
                dt['FECHA FINAL CRE'] = dt['FECHA FINAL CRE'].apply(lambda x: str(x).split('T')[0])
            except Exception:
                print('ERROR FECHA CRECIMIENTO DESCARGAR EXCEL', e)

            try:
                dt['FECHA INICIAL MORT'] = dt['FECHA INICIAL MORT'].apply(lambda x: str(x).split('T')[0])
                dt['FECHA FINAL MORT'] = dt['FECHA FINAL MORT'].apply(lambda x: str(x).split('T')[0])
            except Exception:
                print('ERROR FECHA MORTALIDAD DESCARGAR EXCEL', e)

        except Exception as e:
            print(e)
        return [downloadExcel(dt, archivo = f'Seguimiento_semanal_{nit}.xlsx'), 'Descargando ...', 'success', True]
    
    except Exception as e:
        print(e)
        return [no_update, 'Error al cargar la información', 'warning', True]
    

#### INVENTARIO ESTANQUE

# cargar tabla reporte inventario estanque
@app.callback([Output('alert_cargar_tabla_consulta_i', 'children'),
               Output('alert_cargar_tabla_consulta_i', 'color'),
               Output('alert_cargar_tabla_consulta_i', 'is_open'),
               Output('tabla_consulta_i', 'children'),
               Output('modal_data_i', 'is_open'),
               Output('data_download_i', 'data')],
               Input('cargar_tabla_consulta_i', 'n_clicks'),
              [State('user_info', 'data')] + [State(i, 'value') for i in ids_consulta_i])
def cargar_tabla_i(n, data, tabla_inventario, gerente, nit_cliente, granja, año, lote):
    if n is None:
        raise dash.exceptions.PreventUpdate()
    user = pd.read_json(data, orient = 'split')
    rol = user['rol_usuario'].values[0]
    usuario = user['nombre'].values[0]
    doc_id = user['doc_id'].values[0]
    pais = user['pais'].values[0]
    if tabla_inventario == None or tabla_inventario == '':
        return ['Inventario no valido', 'warning', True, no_update, no_update, no_update]
    if rol == 'administrador':
        if gerente is None or gerente == '':
            return ['Gerente de Zona no  valido', 'warning', True, no_update, no_update, no_update]
    if rol == 'gerente' or rol == 'administrador':
        if nit_cliente is None or nit_cliente == '':
            return ['Cliente no  valido', 'warning', True, no_update, no_update, no_update]
    if rol == 'gerente':
        gerente = doc_id
    if rol == 'cliente':
        nit_cliente = doc_id
    else:
        nit_cliente = json.loads(nit_cliente)
        #gerente = pd.read_json(data2, orient = 'split')['gerente_zona'].unique[0]
    ids = [granja, año, lote]
    ids_label = ['Granja', 'Año', 'Lote']
    for i in range(len(ids)):
        if isinstance(ids[i], str) or ids[i] is None or ids[i] == [None] or len(ids[i]) == 0:
            return [f'{ids_label[i]} no valida', 'warning', True, no_update, no_update, no_update]
    año_sql = '('
    for i in año:
        año_sql = año_sql + str(i)
        if int(i) == año[-1]:
            año_sql = año_sql + ')'
        else:
            año_sql = año_sql + ','
    
    granja_sql = '('
    for i in granja:
        granja_sql = granja_sql + str(i)
        if int(i) == granja[-1]:
            granja_sql = granja_sql + ')'
        else:
            granja_sql = granja_sql + ','
    
    lote_sql = '('
    for i in lote:
        lote_sql = lote_sql + str(i)
        if int(i) == lote[-1]:
            lote_sql = lote_sql + ')'
        else:
            lote_sql = lote_sql + ','

    # if comparacion == '25% MEJORES CLIENTES ITALCOL':
    #     sql = f'''SELECT seguimiento_semanal.*, clientes.pais FROM seguimiento_semanal INNER JOIN clientes ON  clientes.nit = seguimiento_semanal.nit_cliente WHERE clientes.pais = '{pais}' AND seguimiento_semanal.año IN {año_sql};'''
    # else:
    if tabla_inventario == 'ALIMENTO':
        sql = f'''SELECT DISTINCT alimento.*, lotes.nombre_lote, unidades_productivas.nombre_estanque, granjas.nombre_granja FROM alimento INNER JOIN lotes ON lotes.id_lote = alimento.id_lote INNER JOIN unidades_productivas ON unidades_productivas.id_estanque = alimento.id_estanque INNER JOIN  granjas ON granjas.id_granja = lotes.id_granja WHERE alimento.id_lote IN {lote_sql};'''
    if tabla_inventario == 'PESCAS':
        sql = f'''SELECT DISTINCT pescas.*, lotes.nombre_lote, unidades_productivas.nombre_estanque, granjas.nombre_granja FROM pescas INNER JOIN lotes ON lotes.id_lote = pescas.id_lote INNER JOIN unidades_productivas ON unidades_productivas.id_estanque = pescas.id_estanque INNER JOIN  granjas ON granjas.id_granja = lotes.id_granja WHERE pescas.id_lote IN {lote_sql};'''
    if tabla_inventario == 'TRASLADOS':
        sql = f'''SELECT DISTINCT traslados.*, lotes.nombre_lote, granjas.nombre_granja FROM traslados INNER JOIN lotes ON lotes.id_lote = traslados.id_lote INNER JOIN   granjas ON granjas.id_granja = lotes.id_granja WHERE traslados.id_lote IN {lote_sql};'''
        sql_2 = f'''SELECT id_estanque, nombre_estanque FROM unidades_productivas WHERE id_granja IN {granja_sql}'''
    try:
        data = get_data(sql)
        # if comparacion == '25% MEJORES CLIENTES ITALCOL':
        #     data.drop('pais', axis = 1, inplace = True)
        #     data_filter = data.loc[data['nit_cliente'].isin([int(nit_cliente)])&
        #                             data['id_granja'].isin(granja) &
        #                             data['año'].isin(año) &
        #                             data['id_lote'].isin(lote) &
        #                             data['linea'].isin(linea) &
        #                             data['sexo'].isin(sexo) &
        #                             data['edad_dias'].isin(edad)].drop(['id', 'gerente_zona', 'id_granja', 'id_lote', 'id_galpon'], axis = 1)
        if tabla_inventario == 'TRASLADOS':
            estanques = get_data(sql_2)
            if estanques.empty:
                return ['Sin registros de estanques', 'warning', True, no_update, False, no_update]
        data_resumen = data.copy()
        if data_resumen.empty:
            return ['Sin registros', 'warning', True, no_update, False, no_update]
        
        if tabla_inventario == 'ALIMENTO':
            data_resumen.drop(['id', 'id_lote', 'id_estanque'], axis = 1, inplace = True)
            data_resumen = data_resumen[['fecha', 'fecha_inicial', 'fecha_final', 'dias_cultivo', 'tipo_alimento', 'precio_b_40_kg',
                                         'kg_real', 'nombre_estanque',  'nombre_lote', 'nombre_granja',
                                         'observaciones']]
            data_resumen.columns = ['FECHA', 'FECHA INICIAL', 'FECHA FINAL', 'DIAS CULTIVO', 'TIPO ALIMENTO', 'PRECIO Bx40 KG',
                                    'KG REAL', 'ESTANQUE', 'LOTE', 'GRANJA', 'OBSERVACIONES']    
        if tabla_inventario == 'PESCAS':
            data_resumen.drop(['id', 'id_lote', 'id_estanque'], axis = 1, inplace = True)
            data_resumen = data_resumen[['fecha', 'dias_cultivo', 'cantidad', 'biomasa', 'peso_visceras', 'biomasa_neta',
                                         'nombre_estanque',  'nombre_lote', 'nombre_granja',
                                         'observaciones']]
            data_resumen.columns = ['FECHA', 'DIAS CULTIVO', 'CANTIDAD', 'BIOMASA (Kg)', 'PESO VISCERAS', 'BIOMASA NETA',
                                    'ESTANQUE',  'LOTE', 'GRANJA', 'OBSERVACIONES']   
        if tabla_inventario == 'TRASLADOS':
            data_resumen.drop(['id', 'id_lote'], axis = 1, inplace = True)
            data_resumen = data_resumen[['fecha', 'dias_cultivo', 'cantidad', 'peso_promedio', 'vacuna',
                                         'estanque_origen', 'estanque_destino', 'nombre_lote', 'nombre_granja',
                                         'observaciones']]
            data_resumen.columns = ['FECHA', 'DIAS CULTIVO', 'CANTIDAD', 'PESO PROMEDIO (Kg)', 'VACUNA',
                                    'ESTANQUE ORIGEN', 'ESTANQUE DESTINO', 'LOTE', 'GRANJA',
                                    'OBSERVACIONES']
            replace_estanque = dict()
            for k, v in zip(estanques['id_estanque'], estanques['nombre_estanque']):            
                replace_estanque[k] = v
            data_resumen['ESTANQUE ORIGEN'].replace(replace_estanque, inplace = True)
            data_resumen['ESTANQUE DESTINO'].replace(replace_estanque, inplace = True)
        #table = dashtable(archivo = data_resumen, tipo = 'ss')
        table = dbc.Table.from_dataframe(data_resumen, striped = True, bordered = True, hover = True)
        try:
            fecha = datetime.today().date()
            trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Consultar Excel inventario estanques')
        except Exception as e:
            print(e)        
        return ['Información consultada con éxito', 'success', True, table, True, data_resumen.to_json(date_format = 'iso', orient = 'split')]
    except Exception as e:
        print(e)
        return ['Error al consultar la información', 'warning', True, no_update, no_update, no_update]

# actualizar campo cliente en funcion de gerente
@app.callback(Output('cliente_consulta_i', 'options'),
              Input('gerente_consulta_i', 'value'),
              State('user_info', 'data'))
def clienteGerente_i(gerente, data):
    usuario = pd.read_json(data, orient = 'split')
    rol = usuario['rol_usuario'].values[0]
    if gerente is None and rol == 'administrador':
        return [{'label': 'Por favor seleccione un gerente', 'value': ''}]
    if rol == 'administrador':
        sql = f'''SELECT nit, nombre_cliente FROM clientes WHERE gerente_zona = '{gerente}';'''
        try:
            clientes = get_data(sql) 
        except Exception as e:
            print(e)
            return [{'label': 'Error al consultar clientes', 'value': ''}]
        if clientes.empty:
            return [{'label': 'Sin registros en clientes', 'value': ''}]
        clientes.sort_values(by = ['nombre_cliente'], inplace = True)
        clientes.reset_index(drop = True, inplace = True)
        return [{"label": clientes["nombre_cliente"][i], "value": '{' + f'"label": "{clientes["nombre_cliente"][i]}", "value": "{clientes["nit"][i]}"' + '}'} for i in range(clientes['nit'].shape[0])]
    else:
        return no_update


# actualizar campo granja en funcion de cliente
@app.callback(Output('granja_consulta_i', 'options'),
              Input('cliente_consulta_i', 'value'),
              State('user_info', 'data'))
def granjaCliente_i(cliente, data):
    usuario = pd.read_json(data, orient = 'split')
    rol = usuario['rol_usuario'].values[0]
    doc_id = usuario['doc_id'].values[0]
    if rol == 'cliente':
        return no_update
    if cliente is None or cliente == '':
        return [{'label': 'Por favor seleccione un cliente', 'value': ''}]
    cliente = json.loads(cliente)
    if rol == 'administrador':
        cliente = cliente['value']
    print(cliente)
    sql = f'''SELECT id_granja, granja FROM seguimiento_estanques WHERE nit_cliente = {cliente};'''
    try:
        granjas = get_data(sql)
    except Exception as e:
        print(e)
        return [{'label': 'Error al consultar granjas', 'value': ''}]
    if granjas.empty:
        return [{'label': 'Sin registros de granjas', 'value': ''}]
    granjas.drop_duplicates(inplace = True)
    granjas.sort_values(by = ['granja'], inplace = True)
    granjas.reset_index(drop = True, inplace = True)
    return [{"label": granjas["granja"][i], "value": granjas["id_granja"][i]} for i in range(granjas.shape[0])]
            
# actualizar año
@app.callback([Output('año_consulta_i', 'options'),
               Output('data_gal_consulta_i', 'data')],
              Input('granja_consulta_i', 'value'),
              [State('cliente_consulta_i', 'value'),
               State('user_info', 'data')])
def updateYear_i(granja, cliente, data):
    if granja == None or granja == [None] or granja == '' or len(granja) == 0:
        return [[{'label': 'Por favor seleccione una granja', 'value': ''}], no_update]
    usuario = pd.read_json(data, orient = 'split')
    rol = usuario['rol_usuario'].values[0]
    doc_id = usuario['doc_id'].values[0]
    if rol == 'cliente':
        cliente = doc_id
    else:
        cliente = json.loads(cliente)
        if rol == 'administrador':
            cliente = cliente['value']
        else:
            cliente = cliente
    granja_sql = '('
    for i in granja:
        granja_sql = granja_sql + str(i)
        if int(i) == granja[-1]:
            granja_sql = granja_sql + ')'
        else:
            granja_sql = granja_sql + ','
    sql = f'SELECT DISTINCT año, id_granja, id_lote, lote  FROM seguimiento_estanques WHERE nit_cliente = {cliente} AND id_granja IN {granja_sql}'
    try:
        data_año = get_data(sql)
    except Exception as e:
        print(e)
        return [[{'label': 'Error al consultar años', 'value': ''}], no_update]
    if data_año.empty:
        return [[{'label': 'Sin registros', 'value': ''}], no_update]
    #data_año.drop_duplicates(axis = 1, inplace = True)
    data_año.sort_values(by = ['año'], inplace = True)
    data_año.reset_index(drop = True, inplace = True)
    years = data_año['año'].unique()
    return [[{'label': i, 'value': i} for i in years], data_año.to_json(date_format='iso', orient = 'split')]

## actualizar lote
@app.callback(Output('lote_consulta_i', 'options'),
             Input('año_consulta_i', 'value'),
             State('data_gal_consulta_i', 'data'))
def update_lote_i(año, data):
    if año is None or año == '' or len(año) == 0:
        return [{'label': 'Por favor seleccione un año', 'value': ''}]
    try:
        data_lote = pd.read_json(data, orient = 'split')
    except Exception as e:
        print(e)
        return [{'label': 'Error al consular datos', 'value': ''}]
    lotes = data_lote.loc[data_lote['año'].isin(año)][['id_lote', 'lote']]
    lotes.drop_duplicates(inplace = True)
    lotes.reset_index(drop = True, inplace = True)
    return [{'label': lotes['lote'][i], 'value': lotes['id_lote'][i]} for i in range(lotes.shape[0])]


## DESCARGAR EXCEL SEGUIMIENTO SEMANAL
@app.callback([Output('download_excel_i', 'data'),
               Output('alert_descargar_tabla_consulta_i', 'children'),
               Output('alert_descargar_tabla_consulta_i', 'color'),
               Output('alert_descargar_tabla_consulta_i', 'is_open'),],
              Input('descargar_tabla_consulta_i', 'n_clicks'),
             [State('data_download_i', 'data'),
              State('cliente_consulta_i', 'value'),
              State('user_info', 'data'),
              State('tabla_inventario', 'value')])
def downloadExceli(n, data, nit, data_user, inventario):
    if n is None:
        raise dash.exceptions.PreventUpdate()    
    user = pd.read_json(data_user, orient = 'split')
    rol = user['rol_usuario'].values[0]
    doc_id = user['doc_id'].values[0]

    if rol == 'cliente':
        nit = doc_id
    else:
        try:
            nit = json.loads(nit)
            nit = nit['label']
        except Exception as e:
            print('Cargar json nit inventarios', e)
    try:
        dt = pd.read_json(data, orient = 'split')
        dt['FECHA'] = dt['FECHA'].apply(lambda x: x.split('T')[0])
        try:
            dt['FECHA INICIAL'] = dt['FECHA INICIAL'].apply(lambda x: x.split('T')[0])
            dt['FECHA FINAL'] = dt['FECHA FINAL'].apply(lambda x: x.split('T')[0])
        except Exception as e:
            print(e)   
        try:
            fecha = datetime.today().date()
            trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Descargar Excel inventario estanques')
        except Exception as e:
            print(e)
        return [downloadExcel(dt, archivo = f'Inventario_{inventario}_{nit}.xlsx'), 'Descargando ...', 'success', True]
    except Exception as e:
        print(e)
        return [no_update, 'Error al cargar la información', 'warning', True]

## reporte uso
@app.callback([Output('alert_reporte_uso', 'children'),
               Output('alert_reporte_uso', 'color'),
               Output('alert_reporte_uso', 'is_open'),
               Output('modal_reporte_uso', 'is_open'),
               Output('modal_ver_reporte_uso_div', 'children'),
               Output('descargar_reporte_uso', 'data')],
               Input('reporte_uso', 'n_clicks'))
def ver_reporte_uso(n):
    if n is None:
        return [no_update, 'warning', False, False, '', no_update]
    try:
        data = reporte_resumen_uso()
    except Exception as e:
        print(e)
        return ['Error al consultar', 'warning', True, False, '', no_update]

    table = dbc.Table.from_dataframe(data, striped = True, bordered = True, hover = True, responsive = True)

    return ['Información consultada con éxito', 'success', True, True, table, data.to_json(orient = 'split', date_format = 'iso')]


#  DESCARGAR EXCEL REPORTE USO
@app.callback([Output('download_reporte_uso', 'data'),
               Output('alert_descargar_reporte_uso', 'children'),
               Output('alert_descargar_reporte_uso', 'color'),
               Output('alert_descargar_reporte_uso', 'is_open'),],
              Input('descargar_reporte_uso_c', 'n_clicks'),
              [State('descargar_reporte_uso', 'data')])
def downloadExcelReporteUso(n, data):
    if n is None:
        return [no_update, '', 'warning', False]
    fecha = datetime.today().date()
    fecha_ = datetime.strftime(fecha, format = '%Y-%m-%d')
    if n is None:
        raise dash.exceptions.PreventUpdate()    
    try:
        dt = pd.read_json(data, orient = 'split')
        dt['Fecha registro'] = dt['Fecha registro'].apply(lambda x: x.split('T')[0])
        dt['Ultimo ingreso app'] = dt['Ultimo ingreso app'].apply(lambda x: x.split('T0')[0])
        
        try:
            fecha = datetime.today().date()
            #trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Descargar tabla compromisos')
        except Exception as e:
            print(e)
        return [downloadExcel(dt, archivo = f'Reporte_uso_{fecha_}.xlsx'), 'Descargando ...', 'success', True]
    except Exception as e:
        print(e)
        return [no_update, 'Error al cargar la información', 'warning', True]
  


# consultar trazabilidad
@app.callback([Output('alert_consultar_trz', 'children'),
               Output('alert_consultar_trz', 'color'),
               Output('alert_consultar_trz', 'is_open'),
               Output('modal_trz', 'is_open'),
               Output('modal_ver_trz_div', 'children'),
               Output('descargar_trazabilidad', 'data')],
               Input('consultar_trz', 'n_clicks'),
               [State('tipo_usuario', 'value'),
                State('accion_usuario', 'value'),
                State('user_info', 'data')])
def consultarTrz(n, tipo_usuario, accion, user_data):
    user = pd.read_json(user_data, orient = 'split')
    rol = user['rol_usuario'].values[0]
    doc_id = user['doc_id'].values[0]
    if n is None:
        raise dash.exceptions.PreventUpdate()
    if not rol in ['administrador', 'especialista', 'gerente']:
        return ['', 'warning', False, False, None, None]
    if tipo_usuario == None or len(tipo_usuario) < 1:
        return ['Tipo de usuario no valido', 'warning', True, False, None, None]
    if accion is None or len(accion) < 1:
        return ['Acción no validad', 'warning', True, False, None, None]
    
    # if 'especialista' in tipo_usuario:
    #     index = tipo_usuario.index('especialista')
    #     tipo_usuario[index] = 'gerente'

    tipo_sql = '('
    for i in tipo_usuario:
        tipo_sql = tipo_sql + "'" + i + "'"
        if i == tipo_usuario[-1]:
            tipo_sql += ')'
        else:
            tipo_sql += ','
    
    accion_sql = '('
    for i in accion:
        accion_sql = accion_sql + "'" + i + "'"
        if i == accion[-1]:
            accion_sql += ')'
        else:
            accion_sql += ','
    try:
        if rol == 'administrador':
            sql = f'SELECT usuarios.nombre, trazabilidad.tipo_usuario, trazabilidad.fecha, trazabilidad.accion FROM trazabilidad INNER JOIN usuarios ON trazabilidad.doc_id = usuarios.doc_id WHERE trazabilidad.tipo_usuario IN {tipo_sql} AND trazabilidad.accion IN {accion_sql}'
        else:
            sql = f'SELECT usuarios.nombre, trazabilidad.tipo_usuario, trazabilidad.fecha, trazabilidad.accion FROM trazabilidad INNER JOIN usuarios ON trazabilidad.doc_id = usuarios.doc_id INNER JOIN clientes ON trazabilidad.doc_id = clientes.nit WHERE trazabilidad.tipo_usuario IN {tipo_sql} AND trazabilidad.accion IN {accion_sql} AND clientes.gerente_zona = {doc_id}'
        data = get_data(sql)
    except Exception as e:
        print(e)
        return ['Error al consultar información', 'warning', True, False, None, None]

    if data.empty:
        return ['Sin registros', 'warning', True, False, None, None]
    
    data = data[['fecha', 'nombre', 'tipo_usuario', 'accion']]
    data.columns = ['FECHA', 'NOMBRE', 'TIPO USUARIO', 'ACCIÓN']
    data.sort_values(by = ['FECHA', 'ACCIÓN'], inplace = True)
    table = dbc.Table.from_dataframe(data, striped = True, bordered = True, hover = True, responsive = True)

    return ['Información consultada con éxito', 'success', True, True, table, data.to_json(orient = 'split', date_format = 'iso')]


#  DESCARGAR EXCEL TRAZABILIDAD
@app.callback([Output('download_trz', 'data'),
               Output('alert_descargar_trz', 'children'),
               Output('alert_descargar_trz', 'color'),
               Output('alert_descargar_trz', 'is_open'),],
              Input('descargar_trz_c', 'n_clicks'),
              [State('descargar_trazabilidad', 'data'),
               State('user_info', 'data')])
def downloadExcelTrz(n, data, user_data):
    user = pd.read_json(user_data, orient = 'split')
    fecha = datetime.today().date()
    fecha_ = datetime.strftime(fecha, format = '%Y-%m-%d')
    if n is None:
        raise dash.exceptions.PreventUpdate()    
    try:
        dt = pd.read_json(data, orient = 'split')
        dt['FECHA'] = dt['FECHA'].apply(lambda x: x.split('T')[0])
        try:
            fecha = datetime.today().date()
            #trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Descargar tabla compromisos')
        except Exception as e:
            print(e)
        return [downloadExcel(dt, archivo = f'tabla_trazabilidad_{fecha_}.xlsx'), 'Descargando ...', 'success', True]
    except Exception as e:
        print(e)
        return [no_update, 'Error al cargar la información', 'warning', True]
  

# actualizar campo cliente en funcion de gerente
@app.callback(Output('cliente_ingreso', 'options'),
              Input('gerente_ingreso', 'value'),
              State('user_info', 'data'))
def clienteGerente(gerente, data):
    usuario = pd.read_json(data, orient = 'split')
    rol = usuario['rol_usuario'].values[0]
    if rol == 'administrador':
        if gerente is None:
            return [{'label': 'Seleccione un gerente de zona', 'value': None}]
    else:
        raise dash.exceptions.PreventUpdate()
    try:
        clientes = get_data(f'''SELECT nit, nombre_cliente FROM clientes WHERE gerente_zona = '{gerente}';''') 
    except Exception as e:
        print(e)
        return [{'label': 'Error al consultar gerentes de zona', 'value': None}]
    if clientes.empty:
        return [{'label': 'Sin registros', 'value': None}]
    clientes.sort_values(by = ['nombre_cliente'], inplace = True)
    clientes.reset_index(drop = True, inplace = True)
    return [{'label': clientes['nombre_cliente'][i], 'value': clientes['nit'][i]} for i in range(clientes.shape[0])]

# actualizar campo granja en funcion de cliente
@app.callback(Output('granja_ingreso', 'options'),
              Input('cliente_ingreso', 'value'),
              State('user_info', 'data'))
def granjaCliente(cliente, data):
    usuario = pd.read_json(data, orient = 'split')
    rol = usuario['rol_usuario'].values[0]
    if rol != 'cliente':
        if cliente is None:
            return [{'label': 'Por favor seleccione un cliente', 'value': '-'}]
    else:
        raise dash.exceptions.PreventUpdate()
    try:
        granjas = get_data(f'''SELECT id_granja, nombre_granja FROM granjas WHERE nit_cliente = {cliente}''')
    except Exception as e:
        print(e)
        return [{'label': 'Error al consultar granjas', 'value': None}]
    if granjas.empty:
        return [{'label': 'Sin registros', 'value': None}]
    granjas.sort_values(by = ['nombre_granja'], inplace = True)
    granjas.reset_index(drop = True, inplace = True)
    return [{'label': granjas['nombre_granja'][i], 'value': granjas['id_granja'][i]} for i in range(granjas.shape[0])]


# actualizar valores lote
@app.callback(Output('lote_ingreso', 'options'),
              [Input('granja_ingreso', 'value'),
               Input('lote_nuevo', 'value')],
              [State('cliente_ingreso', 'value'),
               State('user_info', 'data')])
def lotes_(granja, nuevo, cliente, data):
    if granja is None or granja == '-' or nuevo == 'Si':
        raise dash.exceptions.PreventUpdate()
    try:
        usuario = pd.read_json(data, orient = 'split')
        rol = usuario['rol_usuario'].values[0]
    except Exception as e:
        print(e)
        return [{'label': 'Error al cargar datos de usuario', 'value': '{"value": "-", "label": "Error al cargar datos usuario"}'}]
    if rol == 'cliente':
        cliente = usuario['doc_id'].values[0]
    sql = f'SELECT DISTINCT id_lote, nombre_lote FROM lotes WHERE nit_cliente = {cliente} AND id_granja = {granja} AND cerrado != "Si"'
    try:
        lotes = get_data(sql)
    except Exception as e:
        print(e)
        return [{'label': 'Error al consultar lotes', 'value': '{"value": "-", "label": "Error al consultar lotes"}'}]
    if lotes.empty:
        return [{'label': 'Sin registros de lotes', 'value': '{"value": "-", "label": "Sin registros de lotes"}'}]
    lotes.sort_values(by = ['nombre_lote'], inplace = True)
    lotes.reset_index(drop = True, inplace = True)
    return [{'label': lotes['nombre_lote'][i], 'value':'{'+ f'"label": "{lotes["nombre_lote"][i]}", "value": "{lotes["id_lote"][i]}"'+'}'} for i in range(lotes.shape[0])]


# cambiar campo lote
@app.callback(Output('lote_ingreso_col', 'children'),
              Input('lote_nuevo', 'value'))
def cambio_lote(nuevo):
    if nuevo == None:
        raise dash.exceptions.PreventUpdate()
    if len(nuevo) == 0:
        return [
            dbc.FormGroup([
                dbc.Label('LOTE'),
                dbc.Select(id = 'lote_ingreso',
                           options = [{'label': 'Sin registros', 'value': '{"value": "-", "label": "Sin registros"}'}]),
                dbc.FormText('-')
                ])
        ]
    else:
        return [
            dbc.FormGroup([
                dbc.Label('LOTE'),
                dbc.Input(id = 'lote_ingreso',type = 'text',
                          debounce = True),
                dbc.FormText('-')
                ])
        ]



# cargar informacion estanque ingreso
@app.callback(Output('estanque_ingreso', 'options'),
              Input('lote_ingreso', 'value'),
              [State('cliente_ingreso', 'value'),
               State('granja_ingreso', 'value'),
               State('user_info', 'data')])
def cargar_estanque(lote, cliente, granja, data):

    try:
        usuario = pd.read_json(data, orient = 'split')
        rol = usuario['rol_usuario'].values[0]
    except Exception as e:
        print(e)
        
    if rol == 'cliente':
        cliente = usuario['doc_id'].values[0]

    if not bool(lote):
        return [{'label': 'Selecciones lote ingreso', 'value': None}]
    else:
        try:
            id_lote = json.loads(lote)['value']
            sql = f'SELECT lotes.id_estanque, unidades_productivas.nombre_estanque FROM lotes LEFT JOIN unidades_productivas ON lotes.id_estanque = unidades_productivas.id_estanque WHERE id_lote = {id_lote}'
        except:
            sql = f'SELECT unidades_productivas.id_estanque, unidades_productivas.nombre_estanque FROM unidades_productivas WHERE id_granja = {granja} AND nit_cliente = {cliente}'
        
    try:
        estanques = get_data(sql)
    except Exception as e:
        print(e)
        return [{'label': 'Error al consultar estanques', 'value': None}]

    if estanques.empty:
        return [{'label': 'Sin registros de estanques', 'value': None}]
    
    estanques.sort_index(ascending = False, inplace = True)

    opciones = [{'label': i, 'value': '{"label": "' + f'{i}' + '", "value": "' + f'{j}' + '"}'} for i, j in zip(estanques['nombre_estanque'], estanques['id_estanque'])]

    return opciones

# cargar informacion ingreso
@app.callback([Output('fecha_siembra_ingreso', 'date'),
               Output('especie_ingreso', 'value'),
               Output('peso_siembra_ingreso', 'value'),
               Output('talla_ingreso', 'value'),
               Output('numero_inicial_peces_ingreso', 'value'),
               Output('genetica_ingreso', 'value')],
               Input('estanque_ingreso', 'value'),
               [State('lote_ingreso', 'value'),
                State('cliente_ingreso', 'value'),
                State('granja_ingreso', 'value'),
                State('lote_nuevo', 'value'),
                State('user_info', 'data')])
def cargarInfoLote(estanque, lote, cliente, granja, nuevo, data):
    if lote is None or lote == '' or nuevo == ['Si']:
        return [datetime.today().date()] + [None]*5
    if not bool(estanque):
        return [datetime.today().date()] + [None]*5
    else:
        try:
            estanque_info = json.loads(estanque)
            id_estanque = estanque_info['value']
        except Exception as e:
            print('Error al leer estanque', e)
            return [datetime.today().date()] + [None]*5
    try:
        usuario = pd.read_json(data, orient = 'split')
        rol = usuario['rol_usuario'].values[0]
    except Exception as e:
        print(e)
        return [datetime.today().date()] + [None]*5
    if rol == 'cliente':
        cliente = usuario['doc_id'].values[0]
    lote = json.loads(lote)['value']
    sql = f'SELECT lotes.fecha_siembra, lotes.especie_sembrada, lotes.linea_genetica, lotes.peso_siembra_gr, lotes.talla_cm, lotes.numero_inicial_peces, lotes.id_estanque, unidades_productivas.nombre_estanque FROM lotes INNER JOIN unidades_productivas ON lotes.id_estanque = unidades_productivas.id_estanque WHERE lotes.nit_cliente = {cliente} AND lotes.id_granja = {granja} AND lotes.id_lote = {lote} AND lotes.id_estanque = {id_estanque}'
    try:
        lote_info = get_data(sql)
    except Exception as e:
        print(e)
        return [datetime.today().date()] + [None]*5
    if lote_info.empty:
        return [datetime.today().date()] + [None]*5
    
    #id_estanque = lote_info['id_estanque'].values[0]
    nombre_estanque = lote_info['nombre_estanque'].values[0]

    return [lote_info['fecha_siembra'].values[0], lote_info['especie_sembrada'].values[0], lote_info['peso_siembra_gr'].values[0],
            lote_info['talla_cm'].values[0], lote_info['numero_inicial_peces'].values[0], lote_info['linea_genetica'].values[0]]



################
## ocultar campos pesca
@app.callback([Output('fecha_pesc_anterior_col', 'style'),
               Output('numero_pesca_ingreso_col', 'style'),
               Output('tabla_ingreso_pesca_col', 'style'),
               Output('visceras_pesca_col', 'style')],
              Input('Pesca', 'value'))
def hiddenPesca(n):
    if n is None or len(n) == 0:
        return [{'display': 'none'}]*4
    else:
        return [{'display': 'inline'}]*4

### cargar tabla ingreso pesca
@app.callback(Output('tabla_ingreso_pesca', 'children'),
              [Input('numero_pesca_ingreso', 'value'),
               Input('visceras_pesca', 'value')])
def cargarIngresoPesca(n, visceras):
    
    if isinstance(n, str) or n is None or n < 1:
        return no_update
    else:
        return crearTablaIngreso('ingreso_pesca', n, visceras = visceras)

## ocultar campos seguimiento al crecimiento
@app.callback([Output('fecha_muestreo_anterior_col', 'style'),
               Output('peso_prom_muestreo_anterior_col', 'style'),
               Output('real_ingreso_col', 'style'),
               Output('longitud_crecimiento_col', 'style'),
               Output('rango_fecha_cre_col', 'style')],
              Input('seg_crecimiento', 'value'))
def hiddenSegCrec(n):
    if n is None or len(n) == 0:
        return [{'display': 'none'}]*5
    else:
        return [{'display': 'inline'}]*5

## ocultar campos translado
@app.callback([Output('fecha_tras_anterior_col', 'style'),
               Output('translado_ingreso_col', 'style'),
               Output('tabla_ingreso_translado_col', 'style'),
               Output('vacunacion_traslado_col', 'style')],
              [Input('translado', 'value'),
               Input('especie_ingreso', 'value')])
def hiddenTranslado(n, especie):
    if not bool(n):
        return [{'display': 'none'}]*4
    else:
        if especie in ['MR', 'TN']:
            return [{'display': 'inline'}]*4
        else:
            return [{'display': 'inline'}]*3 + [{'display': 'none'}]

### cargar tabla ingreso translado
@app.callback(Output('tabla_ingreso_translado', 'children'),
              Input('translado_ingreso', 'value'),
              Input('granja_ingreso', 'value'))
def cargarIngresoTranslado(n, granja):
    if granja is None:
        return no_update

    if isinstance(n, str) or n is None or n < 1:
        return no_update
    else:
        sql = f'SELECT id_estanque, nombre_estanque FROM unidades_productivas WHERE id_granja = {granja}'
        try:
            estanques = get_data(sql)
        except Exception as e:
            print('ERROR CARGAR ESTANQUES TABLA TRASLADOS', e)
        
        if estanques.empty:
            options = [{'label': i, 'value':  '{"label": ' +  f'"{i}", ' + '"value": ' + f'"{j}"' + '}'} for i, j in zip('SIN ESTANUQES', None)]
            return crearTablaIngreso('ingreso_translado', n, options)
        else:
            options = [{'label': i, 'value': '{"label": ' +  f'"{i}", ' + '"value": ' + f'"{j}"' + '}'} for i, j in zip(estanques['nombre_estanque'], estanques['id_estanque'])]
            return crearTablaIngreso('ingreso_translado', n, options)


        options = [{'label': i, 'value': j} for i, j in zip()]
        return crearTablaIngreso('ingreso_translado', n, options)

## ocultar campos mortalidad
@app.callback([Output('fecha_mort_anterior_col', 'style'),
               Output('mortalidad_ingreso_col', 'style'),
               Output('peso_mortalidad_ingreso_col', 'style'),
               Output('rango_fecha_mort_col', 'style'),
               Output('ac_mort_anterior_col', 'style')],
              Input('mortalidad', 'value'))
def hiddenMortalidad(n):
    if n != ['Si']:
        return [{'display': 'none'}]*5
    else:
        return [{'display': 'inline'}]*5

# ocultar campos cuando el lote es nuevo
@app.callback([Output('dias_ultima_fecha_col', 'style'),
               Output('alimento_ultima_fecha_col', 'style')],
               Input('lote_nuevo', 'value'))
def camposLoteNuevo(n):
    if n is None or len(n) == 0:
        return [{'display': 'inline'}]*2
    else:
        return [{'display': 'none'}]*2

### cargar tabla ingreso alimentacion
@app.callback(Output('tabla_ingreso_alimento', 'children'),
              Input('n_fuentes_alimento', 'value'),
              Input('tipo_alimento_ingreso', 'options'))
def cargarIngresoAlimentacion(n, tipo_alimento_ingreso):
    if isinstance(n, str) or n is None or n < 1:
        return no_update
    else:
        return crearTablaIngreso('ingreso_alimento', n, tipo_alimento_ingreso)


# cargar informacion de estanque ingreso
@app.callback([Output('tipo_estanque_ingreso', 'value'),
               Output('area_m2_ingreso', 'value'),
               Output('vol_m3_ingreso', 'value')],
              [Input('estanque_ingreso', 'value'),
               Input('granja_ingreso', 'value'),])
               #Input('lote_ingreso', 'value')])
def cargarDatosEstanque(unidad, granja):
    if unidad is None or unidad == '':
        return [None]*3
    print(unidad)
    try:
        estanque = json.loads(unidad)
    except Exception as e:
        print(e)
        estanque = {'value': unidad}

    try:
        sql = f'SELECT tipo_sistema, area_m2, volumen_m3 FROM unidades_productivas WHERE id_estanque = {estanque["value"]}'
        data = get_data(sql)
    except Exception as e:
        print(e)
        return [None]   *3
    if data.empty:
        return [None]   *3

    return [data['tipo_sistema'].values[-1], data['area_m2'].values[-1], data['volumen_m3'].values[-1]]


## cargar estanques destino ingreso
@app.callback(Output('estanque_destino_ingreso', 'options'),
              Input('granja_ingreso', 'value'),
              [State('cliente_ingreso', 'value'),
               State('user_info', 'data')])
def cargarEstanquesD(granja, cliente, data):
    usuario = pd.read_json(data, orient = 'split')
    rol = usuario['rol_usuario'].values[0]
    doc_id = usuario['doc_id'].values[0]
    if granja is None or granja == '-':
        return [{'label': 'Seleccione una granja', 'value': '-'}]
    if rol == 'cliente':
        cliente = doc_id
    try:
        sql = f'SELECT DISTINCT id_estanque, nombre_estanque FROM unidades_productivas WHERE nit_cliente = {cliente} AND id_granja = {granja}'
        data = get_data(sql)
    except Exception as e:
        print(e)
        return [{'value': '-', 'label': 'Error al consultar estanques'}]

    if data.empty:
        return [{'value': '-', 'label': 'Sin registros de estanques'}]


    return [{"value": '{' + f'"value": "{data["id_estanque"][i]}", "label": "{data["nombre_estanque"][i]}"' + '}', "label": data["nombre_estanque"][i]} for i in range(data.shape[0])] + [{'label': '-', "value": '{' + f'"value": "0", "label": "-"' + '}'}]


# cargar granjas unidad productiva
@app.callback(Output('granja_up_nc', 'options'),
              Input('nit_clientes_nc_up', 'value'))
def nombreClienteNitUp(nit):
    if nit is None:
        return [{'label': 'Seleccione un cliente', 'value': None}]
    try:
        granjas = get_data(f'''SELECT id_granja, nombre_granja FROM granjas WHERE nit_cliente = '{nit}';''')
    except Exception as e:
        print(e)
        return [{'label': 'Error al consultar granjas', 'value': None}]
    if granjas.empty:
        return [{'label': 'Sin registros en granjas', 'value': None}]
    granjas.sort_values(axis = 0, by = ['nombre_granja'], inplace = True)
    granjas.reset_index(drop = True, inplace = True)
    return [{'label': granjas['nombre_granja'][i], 'value': granjas['id_granja'][i]} for i in range(granjas.shape[0])]


# cargar tabla ingreso granjas no cliente
@app.callback([Output('tabla_ingreso_granjas_nc', 'children'),
               Output('tabla_ingreso_granjas_nc_sal', 'children'),
               Output('tabla_ingreso_granjas_nc_sal', 'color'),
               Output('tabla_ingreso_granjas_nc_sal', 'is_open')],
              Input('cargar_tabla_ingreso_granjas_nc', 'n_clicks'),
              [State('numero_granjas_nc', 'value'),
               State('gerente_nc', 'value'),
               State('nit_clientes_nc', 'value'),
               State('user_info', 'data')])
def cargarTablaGranjasNC(n, granjas, gerente, nit, data):
    usuario = pd.read_json(data, orient = 'split')
    rol = usuario['rol_usuario'].values[0]    
    if n is None:
        raise dash.exceptions.PreventUpdate()
    if rol != 'cliente':
        if gerente is None:
            return [None, 'Gerente de zona no valido', 'warning', True]
    if nit is None:
        return [None, 'Cliente no valido', 'warning', True]
    if isinstance(granjas, str) or granjas is None or granjas <= 0:
       return [None, 'Número de granjas no valido', 'warning', True]

    return [crearTablaIngreso('granjas', granjas), 'Tabla cargada con éxito', 'success', True]


# cargar tabla ingreso mis unidades productivas
@app.callback([Output('tabla_ingreso_up_nc', 'children'),
               Output('tabla_ingreso_up_nc_sal', 'children'),
               Output('tabla_ingreso_up_nc_sal', 'color'),
               Output('tabla_ingreso_up_nc_sal', 'is_open')],
              Input('cargar_tabla_ingreso_up_nc', 'n_clicks'),
              [State('numero_up', 'value'),
               State('gerente_nc_up', 'value'),
               State('nit_clientes_nc_up', 'value'),
               State('granja_up_nc', 'value'),
               State('user_info', 'data')])
def cargarTablaUp(n, unidades, gerente, nit, granja, data):
    usuario = pd.read_json(data, orient = 'split')
    rol = usuario['rol_usuario'].values[0]    
    if n is None:
        raise dash.exceptions.PreventUpdate()
    if rol != 'cliente':
        if gerente is None:
            return [None, 'Gerente de zona no valido', 'warning', True]
    if nit is None:
        return [None, 'Cliente no valido', 'warning', True]
    if granja is None:
        return [None, 'Granja no valida', 'warning', True]
    if isinstance(unidades, str) or unidades is None or unidades <= 0:
       return [None, 'Número de unidades no valido', 'warning', True]

    return [crearTablaIngreso('up', unidades), 'Tabla cargada con éxito', 'success', True]



# cargar tabla mis unidades productivas
@app.callback([Output('alert_cargar_mis_up_nc', 'children'),
               Output('alert_cargar_mis_up_nc', 'color'),
               Output('alert_cargar_mis_up_nc', 'is_open'),
               Output('modal_ver_up_div', 'children'),
               Output('modal_ver_up', 'is_open'),
               Output('descargar_up', 'data')],
               Input('cargar_mis_up_nc', 'n_clicks'),
               [State('user_info', 'data'),
                State('gerente_ver_up_nc', 'value'),
                State('nit_cliente_ver_up', 'value')])
def cargarMisUp(n, data, gerente, nit):
    if n is None:
        raise dash.exceptions.PreventUpdate()
    user = pd.read_json(data, orient = 'split')
    doc_id = user['doc_id'].values[0]
    rol = user['rol_usuario'].values[0]
    if rol in ['administrador', 'gerente']:
        if gerente is None:
            return ['Gerente de zona no valido', 'warning', True, no_update, no_update, no_update]
    if nit is None:
        return ['Nit de cliente no valido', 'warning', True, no_update, no_update, no_update]
    
    if rol == 'cliente':
        sql = f'''SELECT unidades_productivas.fecha, unidades_productivas.nombre_estanque, unidades_productivas.tipo_sistema, unidades_productivas.area_m2, unidades_productivas.volumen_m3, clientes.nombre_cliente, granjas.nombre_granja FROM unidades_productivas INNER JOIN clientes ON unidades_productivas.nit_cliente = clientes.nit INNER JOIN  granjas ON unidades_productivas.id_granja = granjas.id_granja WHERE unidades_productivas.nit_cliente = '{nit}';'''
    else:
        cliente_sql = '('
        for i in nit:
            cliente_sql = cliente_sql + str(i)
            if int(i) == nit[-1]:
                cliente_sql = cliente_sql + ')'
            else:
                cliente_sql = cliente_sql + ','
        sql = f'SELECT unidades_productivas.fecha, unidades_productivas.nombre_estanque, unidades_productivas.tipo_sistema, unidades_productivas.area_m2, unidades_productivas.volumen_m3, clientes.nombre_cliente, granjas.nombre_granja FROM unidades_productivas INNER JOIN clientes ON unidades_productivas.nit_cliente = clientes.nit INNER JOIN  granjas ON unidades_productivas.id_granja = granjas.id_granja WHERE unidades_productivas.nit_cliente IN {cliente_sql}'
    try:
        data = get_data(sql)
    except Exception as e:
        print(e)
        return ['Error al consultar la información', 'warning', True, no_update, no_update, no_update]
    if data.empty:
        return ['Cliente no cuenta con registros de unidades productivas', 'warning', True, no_update, no_update, no_update] 
    data.columns = ['FECHA REGISTRO', 'ESTANQUE', 'TIPO SISTEMA', 'AREA M2', 'VOLUMEN M3', 'CLIENTE', 'GRANJA']
    data.sort_values(axis = 0, by = ['GRANJA'], inplace = True)
    data.reset_index(drop = True, inplace = True)

    try:
        fecha = datetime.today().date()
        trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Consultar Excel unidades productivas registradas')
    except Exception as e:
        print(e)  

    return ['Información cargada con éxito', 'success', True, render_table(data), True, data.to_json(date_format = 'iso', orient = 'split')]

# descargar tabla mis unidad productiva
@app.callback([Output('alert_descargar_up', 'children'),
               Output('alert_descargar_up', 'color'),
               Output('alert_descargar_up', 'is_open'),
               Output('download_up_resgistrados', 'data')],
               Input('descargar_up_c', 'n_clicks'),
               [State('descargar_up', 'data'),
                State('user_info', 'data')])
def downloadUp(n, data, user_data):
    user = pd.read_json(user_data, orient = 'split')
    if n is None:
        raise dash.exceptions.PreventUpdate()
    try:
        dt = pd.read_json(data, orient = 'split')
        dt['FECHA REGISTRO'] = dt['FECHA REGISTRO'].apply(lambda x: x.split('T')[0])        
    except:
        return ['Error al consultar la información', 'warning', 'True', no_update]

    try:
        fecha = datetime.today().date()
        trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Descargar Excel unidades productivas registradas')
    except Exception as e:
        print(e)     

    return ['Descargando...', 'success', 'True', downloadExcel(dt, 'unidades_productivas.xlsx')]        


# cargar tabla mis granjas
@app.callback([Output('alert_cargar_mis_granjas_nc', 'children'),
               Output('alert_cargar_mis_granjas_nc', 'color'),
               Output('alert_cargar_mis_granjas_nc', 'is_open'),
               Output('modal_ver_granjas_div', 'children'),
               Output('modal_ver_granjas', 'is_open'),
               Output('descargar_granjas', 'data')],
               Input('cargar_mis_granjas_nc', 'n_clicks'),
               [State('user_info', 'data'),
                State('gerente_ver_granjas_nc', 'value'),
                State('nit_cliente_ver_granjas', 'value')])
def cargarMisgranjas(n, data, gerente, nit):
    if n is None:
        raise dash.exceptions.PreventUpdate()
    user = pd.read_json(data, orient = 'split')
    doc_id = user['doc_id'].values[0]
    rol = user['rol_usuario'].values[0]
    if rol in ['administrador', 'gerente']:
        if gerente is None:
            return ['Gerente de zona no valido', 'warning', True, no_update, no_update, no_update]
    if nit is None:
        return ['Nit de cliente no valido', 'warning', True, no_update, no_update, no_update]
    
    if rol == 'cliente':
        sql = f'''SELECT granjas.fecha, clientes.nombre_cliente, granjas.nombre_granja, granjas.departamento_provincia, granjas.municipio, granjas.vereda, granjas.altitud_msnm, granjas.latitud, granjas.longitud, granjas.observaciones FROM granjas INNER JOIN clientes ON clientes.nit = granjas.nit_cliente WHERE nit_cliente = '{nit}';'''
    else:
        cliente_sql = '('
        for i in nit:
            cliente_sql = cliente_sql + str(i)
            if int(i) == nit[-1]:
                cliente_sql = cliente_sql + ')'
            else:
                cliente_sql = cliente_sql + ','
        sql = f'''SELECT granjas.fecha, clientes.nombre_cliente, granjas.nombre_granja, granjas.departamento_provincia, granjas.municipio, granjas.vereda, granjas.altitud_msnm, granjas.latitud, granjas.longitud, granjas.observaciones FROM granjas INNER JOIN clientes ON clientes.nit = granjas.nit_cliente WHERE granjas.nit_cliente IN {cliente_sql};'''
    try:
        data = get_data(sql)
    except Exception as e:
        print(e)
        return ['Error al consultar la información', 'warning', True, no_update, no_update, no_update]
    if data.empty:
        return ['Cliente no cuenta con registros de granjas', 'warning', True, no_update, no_update, no_update] 

    data.columns = ['FECHA REGISTRO', 'CLIENTE', 'GRANJA', 'DEPARTAMENTO', 'MUNICIPIO', 'VEREDA', 'ALTITUD', 'LATITUD', 'LONGITUD', 'OBSERVACIONES']
    data.sort_values(axis = 0, by = ['GRANJA'], inplace = True)
    data.reset_index(drop = True, inplace = True)

    try:
        fecha = datetime.today().date()
        trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Consultar Excel granjas registradas')
    except Exception as e:
        print(e)  

    return ['Información cargada con éxito', 'success', True, render_table(data), True, data.to_json(date_format = 'iso', orient = 'split')]

# descargar tabla mis granjas
@app.callback([Output('alert_descargar_granjas', 'children'),
               Output('alert_descargar_granjas', 'color'),
               Output('alert_descargar_granjas', 'is_open'),
               Output('download_granjas_resgistrados', 'data')],
               Input('descargar_granjas_c', 'n_clicks'),
               [State('descargar_granjas', 'data'),
                State('user_info', 'data')])
def downloadGranjas(n, data, user_data):
    user = pd.read_json(user_data, orient = 'split')
    if n is None:
        raise dash.exceptions.PreventUpdate()
    try:
        dt = pd.read_json(data, orient = 'split')
        dt['FECHA REGISTRO'] = dt['FECHA REGISTRO'].apply(lambda x: x.split('T')[0])        
    except:
        return ['Error al consultar la información', 'warning', 'True', no_update]

    try:
        fecha = datetime.today().date()
        trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Descargar Excel granjas registradas')
    except Exception as e:
        print(e)  

    return ['Descargando...', 'success', 'True', downloadExcel(dt, 'granjas.xlsx')]        


# cargar tabla mis galpones no cliente
# @app.callback([Output('alert_cargar_mis_galpones_nc', 'children'),
#                Output('alert_cargar_mis_galpones_nc', 'color'),
#                Output('alert_cargar_mis_galpones_nc', 'is_open'),
#                Output('modal_ver_galpones_div', 'children'),
#                Output('modal_ver_galpones', 'is_open'),
#                Output('descargar_galpones', 'data')],
#                Input('cargar_mis_galpones_nc', 'n_clicks'),
#                [State('user_info', 'data'),
#                 State('gerente_ver_galpones_nc', 'value'),
#                 State('nit_cliente_ver_galpones', 'value'),
#                 State('granjas_nc', 'value')])
# def cargarMisGalpones(n, data, gerente, nit, granjas):
#     if n is None:
#         raise dash.exceptions.PreventUpdate()
#     usuario = pd.read_json(data, orient = 'split')
#     doc_id = usuario['doc_id'].values[0]
#     rol = usuario['rol_usuario'].values[0]
#     if rol in ['administrador', 'gerente']:
#         if gerente is None:
#             return ['Gerente de zona no valido', 'warning', True, no_update, no_update, no_update]
#     if nit is None:
#         return ['Nit de cliente no valido', 'warning', True, no_update, no_update, no_update]
#     if granjas is None or len(granjas) < 1:
#         return ['Granja no valida', 'warning', True, no_update, no_update, no_update]
#     granja_sql = '('
#     for i in granjas:
#         granja_sql = granja_sql + str(i)
#         if int(i) == granjas[-1]:
#             granja_sql = granja_sql + ')'
#         else:
#             granja_sql = granja_sql + ','
#     sql = f'''SELECT galpones.fecha, galpones.nombre_galpon, galpones.temperatura, galpones.humedad, galpones.tipo_galpon, galpones.tipo_comedero, galpones.numero_comederos, galpones.tipo_bebedero, galpones.numero_bebederos, granjas.nombre_granja FROM galpones INNER JOIN granjas ON galpones.id_granja = granjas.id_granja WHERE galpones.id_granja IN {granja_sql};'''
#     try:
#         data = get_data(sql)
#     except Exception as e:
#         print(e)
#         return ['Error al consultar la información', 'warning', True, no_update, no_update, no_update]
#     if data.empty:
#         return ['Granja no cuenta con registros de galpones', 'warning', True, no_update, no_update, no_update] 
#     data.columns = ['FECHA REGISTRO', 'GALPON', 'TEMPERATURA', 'HUMEDAD', 'TIPO GALPON', 'TIPO COMEDERO', '# COMEDEROS', 'TIPO BEBEDERO', '# BEBEDEROS',  'GRANJA']
#     data.sort_values(axis = 0, by = ['GALPON'], inplace = True)
#     data.reset_index(drop = True, inplace = True)
#     return ['Información cargada con éxito', 'success', True, render_table(data), True, data.to_json(date_format = 'iso', orient = 'split')]

# descargar tabla mis galpones
# @app.callback([Output('alert_descargar_galpones', 'children'),
#                Output('alert_descargar_galpones', 'color'),
#                Output('alert_descargar_galpones', 'is_open'),
#                Output('download_galpones_resgistrados', 'data')],
#                Input('descargar_galpones_c', 'n_clicks'),
#                State('descargar_galpones', 'data'))
# def downloadGalpones(n, data):
#     if n is None:
#         raise dash.exceptions.PreventUpdate()
#     try:
#         dt = pd.read_json(data, orient = 'split')
#         dt['FECHA REGISTRO'] = dt['FECHA REGISTRO'].apply(lambda x: x.split('T')[0])
#     except:
#         return ['Error al consultar la información', 'warning', 'True', no_update]

#     return ['Descargando...', 'success', 'True', downloadExcel(dt, 'galpones.xlsx')]        




# cargar tabla mis clientes no gerente
@app.callback([Output('alert_cargar_mis_clientes_ng', 'children'),
               Output('alert_cargar_mis_clientes_ng', 'color'),
               Output('alert_cargar_mis_clientes_ng', 'is_open'),
               Output('modal_ver_clientes', 'is_open'),
               Output('modal_ver_clientes_div', 'children'),
               Output('descargar_clientes', 'data')],
               Input('cargar_mis_clientes_ng', 'n_clicks'),
               [State('user_info', 'data'),
                State('gerente_ver_cliente', 'value')])
def cargarMisClientes(n, data, gerente):
    if n is None:
        raise dash.exceptions.PreventUpdate()
    usuario = pd.read_json(data, orient = 'split')
    rol = usuario['rol_usuario'].values[0]
    user = usuario['nombre'].values[0]
    doc_id = usuario['doc_id'].values[0]
    try:
        if gerente is None:
            return ['Gerente de zona no valido', 'warning', True, no_update, no_update, no_update]
        
        if rol == 'administrador':
            gerente_sql = '('
            for i in gerente:
                gerente_sql = gerente_sql + str(i)
                if int(i) == gerente[-1]:
                    gerente_sql = gerente_sql + ')'
                else:
                    gerente_sql = gerente_sql + ','
            sql = f'''SELECT clientes.fecha, clientes.nit, clientes.nombre_cliente, clientes.telefono, clientes.correo, gerentes.nombre_gerente FROM clientes INNER JOIN gerentes ON clientes.gerente_zona = gerentes.documento_identidad WHERE clientes.gerente_zona IN {gerente_sql};'''
        else:
            sql = f'''SELECT clientes.fecha, clientes.nit, clientes.nombre_cliente, clientes.telefono, clientes.correo, gerentes.nombre_gerente FROM clientes INNER JOIN gerentes ON clientes.gerente_zona = gerentes.documento_identidad WHERE clientes.gerente_zona = '{gerente}';'''
        try:
            data = get_data(sql)
        except Exception as e:
            print(e)
            return ['Error al cargar la información', 'warning', True, no_update, no_update, no_update]
        if data.empty:
            return ['Gerente no tiene registros de clientes', 'warning', True, no_update, no_update, no_update]
        data.columns = ['FECHA REGISTRO', 'NIT', 'CLIENTE', 'TELEFONO', 'CORREO', 'GERENTE ZONA']

        try:
            fecha = datetime.today().date()
            trazabilidad(usuario['doc_id'][0], usuario['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Consultar Excel clientes registrados')
        except Exception as e:
            print(e)   

        return ['Información cargada con éxito', 'success', True, True, render_table(data), data.to_json(date_format = 'iso', orient = 'split')]
    except Exception as e:
        print(e)
        return ['Error al cargar la información', 'success', True, no_update, no_update, no_update]

# descargar clientes registrados
@app.callback([Output('alert_descargar_mis_clientes_ng', 'children'),
               Output('alert_descargar_mis_clientes_ng', 'color'),
               Output('alert_descargar_mis_clientes_ng', 'is_open'),
               Output('download_clientes_resgistrados', 'data'),],
               Input('descargar_mis_clientes_ng', 'n_clicks'),
               [State('descargar_clientes', 'data'),
                State('user_info', 'data')])
def descargarClientes(n, data, user_data):
    user = pd.read_json(user_data, orient = 'split')
    if n is None:
        raise dash.exceptions.PreventUpdate()
    try:
        dt = pd.read_json(data, orient = 'split')
        dt['FECHA REGISTRO'] = dt['FECHA REGISTRO'].apply(lambda x: x.split('T')[0])
    except Exception as e:
        print(e)
        return ['Error al descargar la información', 'warning', True, no_update]
    try:
        fecha = datetime.today().date()
        trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Descargar Excel clientes registrados')
    except Exception as e:
        print(e)   
    return ['Descargando', 'success', True, downloadExcel(dt, 'clientes_registrados.xlsx')]


# crear tabla gerentes
@app.callback([Output('alert_ver_gerentes', 'children'),
               Output('alert_ver_gerentes', 'color'),
               Output('alert_ver_gerentes', 'is_open'),
               Output('modal_ver_gerentes', 'is_open'),
               Output('modal_ver_gerentes_div', 'children'),
               Output('descargar_gerentes_data', 'data')],
               Input('ver_gerentes', 'n_clicks'),
               State('user_info', 'data'))
def cargarTablaGerentes(n, user_data):
    user = pd.read_json(user_data, orient = 'split')
    if n is None:
        raise dash.exceptions.PreventUpdate()
    try:
        gerentes = get_data('SELECT fecha, documento_identidad, nombre_gerente, planta, telefono, correo, pais FROM gerentes WHERE especialista = 0')
    except Exception as e:
        print(e)
        return ['Error al cargar la información', 'warning', True, no_update, no_update, no_update]
    if gerentes.empty:
        return ['Sin registros', 'warning', True, no_update, no_update, no_update]
    gerentes.columns = ['FECHA REGISTRO', 'DOCUMENTO', 'NOMBRE GERENTE', 'PLANTA', 'TELEFONO', 'CORREO', 'PAIS']

    try:
        fecha = datetime.today().date()
        trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Consultar Excel gerentes registrados')
    except Exception as e:
        print(e)  

    return ['Información cargada con éxito', 'success', True, True, render_table(gerentes), gerentes.to_json(date_format = 'iso', orient = 'split')]


# crear tabla especialistas
@app.callback([Output('alert_ver_especialistas', 'children'),
               Output('alert_ver_especialistas', 'color'),
               Output('alert_ver_especialistas', 'is_open'),
               Output('modal_ver_especialistas', 'is_open'),
               Output('modal_ver_especialistas_div', 'children'),
               Output('descargar_especialistas_data', 'data')],
               Input('ver_especialistas', 'n_clicks'),
               State('user_info', 'data'))
def cargarTablaEsp(n, user_data):
    user = pd.read_json(user_data, orient = 'split')
    if n is None:
        raise dash.exceptions.PreventUpdate()
    try:
        gerentes = get_data('SELECT fecha, documento_identidad, nombre_gerente, planta, telefono, correo, pais FROM gerentes WHERE especialista = 1')
    except Exception as e:
        print(e)
        return ['Error al cargar la información', 'warning', True, no_update, no_update, no_update]
    if gerentes.empty:
        return ['Sin registros', 'warning', True, no_update, no_update, no_update]
    gerentes.columns = ['FECHA REGISTRO', 'DOCUMENTO', 'NOMBRE GERENTE', 'PLANTA', 'TELEFONO', 'CORREO', 'PAIS']

    try:
        fecha = datetime.today().date()
        trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Consultar Excel especialistas registrados')
    except Exception as e:
        print(e)  

    return ['Información cargada con éxito', 'success', True, True, render_table(gerentes), gerentes.to_json(date_format = 'iso', orient = 'split')]



# # descargar excel gerentes
@app.callback([Output('alert_descargar_gerentes', 'children'),
               Output('alert_descargar_gerentes', 'color'),
               Output('alert_descargar_gerentes', 'is_open'),
               Output('download_gerentes_resgistrados', 'data')],
               Input('descargar_gerentes', 'n_clicks'),
               [State('descargar_gerentes_data', 'data'),
                State('user_info', 'data')])
def descargarGerentes(n, data, user_data):
    user = pd.read_json(user_data, orient = 'split')
    if n is None:
        raise dash.exceptions.PreventUpdate()
    try:
        dt = pd.read_json(data, orient = 'split')
        dt['FECHA REGISTRO'] = dt['FECHA REGISTRO'].apply(lambda x: x.split('T')[0])
        try:
            fecha = datetime.today().date()
            trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Descargar Excel gerentes registrados')
        except Exception as e:
            print(e)  
        return ['Descargando...', 'success', True, downloadExcel(dt, 'Gerentes.xlsx')]
    except Exception as e:
        print(e)
        return ['Error al descargar la información', 'warning', True, no_update]
        

# # descargar excel especialistas
@app.callback([Output('alert_descargar_especialistas', 'children'),
               Output('alert_descargar_especialistas', 'color'),
               Output('alert_descargar_especialistas', 'is_open'),
               Output('download_especialistas_resgistrados', 'data')],
               Input('descargar_especialistas', 'n_clicks'),
               [State('descargar_especialistas_data', 'data'),
                State('user_info', 'data')])
def descargarEspecialistas(n, data, user_data):
    user = pd.read_json(user_data, orient = 'split')
    if n is None:
        raise dash.exceptions.PreventUpdate()
    try:
        dt = pd.read_json(data, orient = 'split')
        dt['FECHA REGISTRO'] = dt['FECHA REGISTRO'].apply(lambda x: x.split('T')[0])
        try:
            fecha = datetime.today().date()
            trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Descargar Excel especialistas registrados')
        except Exception as e:
            print(e)  
        return ['Descargando...', 'success', True, downloadExcel(dt, 'Especialistas.xlsx')]
    except Exception as e:
        print(e)
        return ['Error al descargar la información', 'warning', True, no_update]
        



# actualizar nit cliente crear granja
@app.callback(Output('nit_clientes_nc', 'options'),
              Input('gerente_nc', 'value'),
              State('user_info', 'data'))
def clientesCrearGranja(gerente, data):
    usuario = pd.read_json(data, orient = 'split')
    rol_usuario = usuario['rol_usuario'].values[0]
    if rol_usuario == 'cliente':
        raise dash.exceptions.PreventUpdate()
    if rol_usuario in ['gerente', 'administrador']:
        if gerente is None:
            return [{'label': 'Seleccione un gerente', 'value': None}]
    try:
        clientes = get_data(f'''SELECT nit, nombre_cliente FROM clientes WHERE gerente_zona = '{gerente}';''')
    except Exception as e:
        print(e)
        return [{'label': 'Error al consultar clientes', 'value': None}]
    if clientes.empty:
        return [{'label': 'Sin registros en clientes', 'value': None}]
    clientes.sort_values(axis = 0, by = ['nombre_cliente'], inplace = True)
    clientes.reset_index(drop = True, inplace = True)
    return [{'label': clientes['nombre_cliente'][i], 'value': clientes['nit'][i]} for i in range(clientes.shape[0])]


# actualizar nit cliente crear unidad productiva
@app.callback(Output('nit_clientes_nc_up', 'options'),
              Input('gerente_nc_up', 'value'),
              State('user_info', 'data'))
def clientesCrearUp(gerente, data):
    user = pd.read_json(data, orient = 'split')
    rol_usuario = user['rol_usuario'].values[0]
    if rol_usuario == 'cliente':
        raise dash.exceptions.PreventUpdate()
    if rol_usuario in ['gerente', 'administrador']:
        if gerente is None:
            return [{'label': 'Seleccione un gerente', 'value': None}]
    try:
        clientes = get_data(f'''SELECT nit, nombre_cliente FROM clientes WHERE gerente_zona = '{gerente}';''')
    except Exception as e:
        print(e)
        return [{'label': 'Error al consultar clientes', 'value': None}]
    if clientes.empty:
        return [{'label': 'Sin registros en clientes', 'value': None}]
    clientes.sort_values(axis = 0, by = ['nombre_cliente'], inplace = True)
    clientes.reset_index(drop = True, inplace = True)

    try:
        fecha = datetime.today().date()
        trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Crear unidad productiva')
    except Exception as e:
        print(e)  

    return [{'label': clientes['nombre_cliente'][i], 'value': clientes['nit'][i]} for i in range(clientes.shape[0])]

# crear_granja_no_cliente
@app.callback([Output('alert_crear_granja_nc', 'children'),
               Output('alert_crear_granja_nc', 'color'),
               Output('alert_crear_granja_nc', 'is_open'),
               Output('gerente_nc', 'value'),
               Output('nit_clientes_nc', 'value'),
               Output('numero_granjas_nc', 'value')],
               Input('confirm_crear_granja_no_cliente', 'submit_n_clicks'),
               [State('user_info', 'data')] + [State(i, 'value') for i in ids_granjas_nc] + [State('tabla_ingreso_granjas_nc', 'children')])
def crearGranjaNoCliente(n, data, gerente, nit, granjas, tabla):
    usuario = pd.read_json(data, orient = 'split')
    rol_usuario = usuario['rol_usuario'].values[0]
    doc_id = usuario['doc_id'].values[0]
    user = usuario['nombre'].values[0]
    divipola = pd.read_csv('Datos/Divipola.csv')
    if n is None:
        raise dash.exceptions.PreventUpdate()
    if rol_usuario in ['administrador', 'gerente']:
        if gerente is None:
            return ['Gerente de zona no valido', 'warning', True, gerente, nit, granjas]
    if nit is None:
        return ['Cliente no valido', 'warning', True, gerente, nit, granjas]
    if isinstance(granjas, str) or granjas is None or granjas <= 0:
        return ['Número de granjas no valido', 'warning', True, gerente, nit, granjas]
    datos_tabla = cargarDatosTablaIngreso('granjas', tabla, granjas)
    if datos_tabla == 'Tabla sin datos':
        return ['Por favor complete la tabla de ingreso', 'warning', True, gerente, nit, granjas]
    else:
        val_datos = validarTablaIngreso(datos_tabla, 'granjas')
    if val_datos != 'ok':
        return [val_datos, 'warning', True, gerente, nit, granjas]
    if rol_usuario == 'cliente':
        try:
            gerente_ = get_data(f'SELECT gerente_zona FROM clientes WHERE nit = {nit}')
            gerente = gerente_['gerente_zona'].values[0]
        except Exception as e:
            print(e)
            return ['Error al consultar gerente de zona', 'warning', True, gerente, nit, granjas]

    data = pd.DataFrame.from_dict(datos_tabla, orient = 'index')
    data.columns = ['nombre_granja', 'departamento_provincia', 'municipio', 'vereda', 'altitud_msnm', 'latitud', 'longitud', 'observaciones']
    data['nit_cliente'] = nit
    data['gerente_zona'] = gerente
    data['id_granja'] = [randint(100000, 999999) for _ in range(data.shape[0])]

    if len(data['id_granja'].unique()) != data.shape[0]:
        return ['Por favor intente nuevamente', 'warning', True, gerente, nit, granjas]
    data['creador'] = doc_id
    data = data[['id_granja', 'nombre_granja', 'departamento_provincia', 'municipio', 'vereda', 'altitud_msnm', 'latitud', 'longitud', 'observaciones', 'nit_cliente', 'gerente_zona',  'creador']]
    data['fecha'] = [datetime.today().date().strftime('%Y-%m-%d')]*data.shape[0]

    try:
        id_sql = '('
        for i in data['id_granja']:
            id_sql = id_sql + str(i)
            if int(i) == data['id_granja'].values[-1]:
                id_sql = id_sql + ')'
            else:
                id_sql = id_sql + ','
        granjas_val = ifExist(f'SELECT EXISTS (SELECT * FROM granjas WHERE id_granja IN {id_sql});')
        if granjas_val[0] == 1:
            return ['Por favor intente nuevamente', 'warning', True, gerente, nit, granjas]
        granja_sql = '('
        for i in data['nombre_granja']:
            granja_sql = granja_sql + "'" + str(i) + "'"
            if str(i) == data['nombre_granja'].values[-1]:
                granja_sql = granja_sql + ')'
            else:
                granja_sql = granja_sql + ','            
        granjas_val = ifExist(f'SELECT EXISTS (SELECT * FROM granjas WHERE nit_cliente = {nit} AND nombre_granja IN {granja_sql});')
        if granjas_val[0] == 1:
            return ['Nombre de granja ya registrado', 'warning', True, gerente, nit, granjas]
    except Exception as e:
        return ['Error al consultar validación con granjas registradas', 'warning', True, gerente, nit, granjas]
        
    try:
        insert_dataframe(data, 'granjas')
        try:
            fecha = datetime.today().date()
            trazabilidad(usuario['doc_id'][0], usuario['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Crear granja')
        except Exception as e:
            print(e)
        return ['Granja creada con éxito', 'success', True, None, None, None]
    except Exception as e:
        print(e)
        return ['Error al crear la granja, por favor intente mas tarde', 'warning', True, gerente, nit, granjas]



# crear unidad productiva 
@app.callback([Output('alert_crear_up_nc', 'children'),
               Output('alert_crear_up_nc', 'color'),
               Output('alert_crear_up_nc', 'is_open'),
               Output('gerente_nc_up', 'value'),
               Output('nit_clientes_nc_up', 'value'),
               Output('numero_up', 'value')],
               Input('crear_up_no_cliente', 'n_clicks'),
               [State('user_info', 'data')] + [State(i, 'value') for i in ids_up_nc] + [State('tabla_ingreso_up_nc', 'children')])
def crearUp(n, data, gerente, nit, granja, unidades, tabla):
    usuario = pd.read_json(data, orient = 'split')
    rol_usuario = usuario['rol_usuario'].values[0]
    doc_id = usuario['doc_id'].values[0]
    user = usuario['nombre'].values[0]
    divipola = pd.read_csv('Datos/Divipola.csv')
    if n is None:
        raise dash.exceptions.PreventUpdate()
    if rol_usuario in ['administrador', 'gerente', 'especialista']:
        if gerente is None:
            return ['Gerente de zona no valido', 'warning', True, gerente, nit, unidades]
    if nit is None:
        return ['Cliente no valido', 'warning', True, gerente, nit, unidades]

    if granja is None or granja == 0 or granja == 'Sin registros en granjas':
        return ['Granja no valida', 'warning', True, gerente, nit, unidades]
  
    if isinstance(unidades, str) or unidades is None or unidades <= 0:
        return ['Número de unidades no valido', 'warning', True, gerente, nit, unidades]
    datos_tabla = cargarDatosTablaIngreso('up', tabla, unidades)
    if datos_tabla == 'Tabla sin datos':
        return ['Por favor complete la tabla de ingreso', 'warning', True, gerente, nit, unidades]
    else:
        val_datos = validarTablaIngreso(datos_tabla, 'up')
    if val_datos != 'ok':
        return [val_datos, 'warning', True, gerente, nit, unidades]
    if rol_usuario == 'cliente':
        try:
            gerente_ = get_data(f'SELECT gerente_zona FROM clientes WHERE nit = {nit}')
            gerente = gerente_['gerente_zona'].values[0]
        except Exception as e:
            print(e)
            return ['Error al consultar gerente de zona', 'warning', True, gerente, nit, unidades]

    data = pd.DataFrame.from_dict(datos_tabla, orient = 'index')
    data.columns = ['nombre_estanque', 'tipo_sistema', 'area_m2', 'volumen_m3']
    data['id_granja'] = granja
    data['nit_cliente'] = nit
    data['gerente_zona'] = gerente
    data['id_estanque'] = [datetime.today().date().strftime('%Y%m%d') + str(randint(10000, 99999)) for _ in range(data.shape[0])]
    

    if len(data['id_estanque'].unique()) != data.shape[0]:
        return ['Por favor intente nuevamente', 'warning', True, gerente, nit, unidades]
    data['creador'] = doc_id
    data = data[['id_estanque', 'nombre_estanque', 'tipo_sistema', 'area_m2', 'volumen_m3', 'id_granja', 'nit_cliente', 'gerente_zona',  'creador']]
    data['fecha'] = [datetime.today().date().strftime('%Y-%m-%d')]*data.shape[0]


    try:
        id_sql = '('
        for i in data['id_estanque']:
            id_sql = id_sql + str(i)
            if i == data['id_estanque'].values[-1]:
                id_sql = id_sql + ')'
            else:
                id_sql = id_sql + ','
        estanque_val = ifExist(f'SELECT EXISTS (SELECT * FROM unidades_productivas WHERE id_estanque IN {id_sql});')
        if estanque_val[0] == 1:
            return ['Por favor intente nuevamente', 'warning', True, gerente, nit, unidades]
        estanque_sql = '('
        for i in data['nombre_estanque']:
            estanque_sql = estanque_sql + "'" + str(i) + "'"
            if i == data['nombre_estanque'].values[-1]:
                estanque_sql = estanque_sql + ')'
            else:
                estanque_sql = estanque_sql + ','            
        granjas_val = ifExist(f'SELECT EXISTS (SELECT * FROM unidades_productivas WHERE nit_cliente = {nit} AND nombre_estanque IN {estanque_sql});')
        if granjas_val[0] == 1:
            return ['Nombre del estanque ya registrado', 'warning', True, gerente, nit, unidades]
    except Exception as e:
        print(e)
        return ['Error al consultar validación con estanques registrados', 'warning', True, gerente, nit, unidades]

    # if 0 in data['id_granja'].values:
    #     return ['Error al validar granja, por favor actualice la página', 'warning', True, gerente, nit, unidades]
    try:
        insert_dataframe(data, 'unidades_productivas')
        try:
            fecha = datetime.today().date()
            trazabilidad(usuario['doc_id'][0], usuario['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Crear unidad productiva')
        except Exception as e:
            print(e)   
        return ['Unidad productiva creada con éxito', 'success', True, None, None, None]
    except Exception as e:
        print(e)
        return ['Error al crear unidad productiva, por favor intente mas tarde', 'warning', True, gerente, nit, unidades]




# agregar galpon
# @app.callback([Output('alert_agregar_galpon_nc', 'children'),
#                Output('alert_agregar_galpon_nc', 'color'),
#                Output('alert_agregar_galpon_nc', 'is_open'),
#                Output('gerente_galpon_nc', 'value'),
#                Output('nit_clientes_galpon_nc', 'value'),
#                Output('granja_galpon_nc', 'value'),
#                Output('numero_galpones_nc', 'value')],
#                Input('confirm_agregar_galpon_nc', 'submit_n_clicks'),
#                [State('user_info', 'data')] + [State(i, 'value') for i in ids_agregar_galpon_nc] + [State('tabla_ingreso_galpones_nc', 'children')])
# def agregarGalpon(n, data, gerente, nit_cliente, granja, galpones, tabla):
#     if n is None:
#         raise dash.exceptions.PreventUpdate()
#     usuario = pd.read_json(data, orient = 'split')
#     rol_usuario = usuario['rol_usuario'].values[0]
#     doc_id = usuario['doc_id'].values[0]
#     user = usuario['nombre'].values[0]
#     divipola = pd.read_csv('Datos/Divipola.csv')
#     if rol_usuario in ['administrador', 'gerente']:
#         if gerente is None:
#             return ['Gerente de zona no valido', 'warning', True, gerente, nit_cliente, granja, galpones]
#     if nit_cliente is None:
#         return ['Nit cliente no valido', 'warning', True, gerente, nit_cliente, granja, galpones]
#     if granja is None:
#         return ['Granja no valida, por favor eliga una granja para agregar un galpón', 'warning', True, 
#                  gerente, nit_cliente, granja, galpones]
#     if isinstance(galpones, str) or galpones is None or galpones <=0:
#         return ['Número de galpones no valido', 'warning', True,  gerente, nit_cliente, granja, galpones]        
#     # if galpon is None or galpon == '':
#     #     return ['Identificador del galpón no valido', 'warning', True, gerente, nit_cliente, granja]
#     # galpones = get_data(f'''SELECT nombre_galpon FROM galpones WHERE nit_cliente = '{nit_cliente}' AND nombre_granja = '{granja}'; ''')
#     # if False if galpones.shape[0] == 0 else galpon in galpones['nombre_galpon'].values:
#     #     return ['Galpón ya registrado en la granja seleccionada', 'warning', True, gerente, 
#     #              nit_cliente]
#     datos_tabla = cargarDatosTablaIngreso('galpones', tabla, galpones)
#     if datos_tabla == 'Tabla sin datos':
#         return ['Por favor complete la tabla de ingreso', 'warning', True, gerente, nit_cliente, granja, galpones]
#     else:
#         val_datos = validarTablaIngreso(datos_tabla, 'galpones')
#     if val_datos != 'ok':
#         return [val_datos, 'warning', True, gerente, nit_cliente, granja, galpones]
#     if rol_usuario == 'cliente':
#         try:
#             gerente_ = get_data(f'SELECT gerente_zona FROM clientes WHERE nit = {nit_cliente}')
#             gerente = gerente_['gerente_zona'].values[0]
#         except Exception as e:
#             print(e)
#             return ['Error al consultar gerente de zona', 'warning', True, gerente, nit_cliente, granja, galpones]                
#     data = pd.DataFrame.from_dict(datos_tabla, orient = 'index')
#     data.columns = ['nombre_galpon', 'temperatura', 'humedad', 'tipo_galpon', 'tipo_comedero', 'tipo_bebedero', 'numero_bebederos', 'numero_comederos',]
#     data['nit_cliente'] = nit_cliente
#     data['id_galpon'] = [randint(100000, 999999) for _ in range(data.shape[0])]
#     data['gerente_zona'] = gerente
#     if len(data['id_galpon'].unique()) != data.shape[0]:
#         return ['Por favor intente nuevamente', 'warning', True, gerente, nit_cliente, granja, galpones]    
#     data['id_granja'] = granja
#     data['creador'] = usuario['doc_id'].values[0]
#     data = data[['id_galpon', 'nombre_galpon', 'temperatura', 'humedad', 'tipo_galpon', 'tipo_comedero', 'tipo_bebedero', 'numero_bebederos', 'numero_comederos', 'id_granja', 'nit_cliente', 'gerente_zona', 'creador']]
#     data['fecha'] = datetime.today().date().strftime('%Y-%m-%d')
    
#     try:
#         id_sql = '('
#         for i in data['id_galpon']:
#             id_sql = id_sql + str(i)
#             if int(i) == data['id_galpon'].values[-1]:
#                 id_sql = id_sql + ')'
#             else:
#                 id_sql = id_sql + ','
#         galpon_val = ifExist(f'SELECT EXISTS (SELECT * FROM galpones WHERE id_galpon IN {id_sql});')
#         if galpon_val[0] == 1:
#             return ['Por favor intente nuevamente', 'warning', True, gerente, nit_cliente, granja, galpones]
#         galpon_sql = '('
#         for i in data['nombre_galpon']:
#             galpon_sql = galpon_sql + "'" + str(i) + "'"
#             if str(i) == data['nombre_galpon'].values[-1]:
#                 galpon_sql = galpon_sql + ')'
#             else:
#                 galpon_sql = galpon_sql + ','            
#         galpon_val = ifExist(f'SELECT EXISTS (SELECT * FROM galpones WHERE nit_cliente = {nit_cliente} AND id_granja = {granja} AND nombre_galpon IN {galpon_sql});')
#         if galpon_val[0] == 1:
#             return ['Nombre de galpon ya registrado', 'warning', True, gerente, nit_cliente, granja, galpones]

#         pass
#     except Exception as e:
#         return ['Error al consultar validación con galpones registrados', 'warning', True, gerente, nit_cliente, granja, galpones]    
    
#     try:
#         insert_dataframe(data, 'galpones')
#         return ['Galpón agregado con éxito', 'success', True, None, None, None, None]
#     except Exception as e:
#         print(e)
#         return ['Galpón no agregado, por favor intente más tarde', 'warning', True, gerente, nit_cliente, galpones, galpones]

#     # return [f'{n}, {granja}, {galpon}, {temperatura}, {humedad}, {tipo_galpon}, {tipo_comedero}, {tipo_bebedero}', 'success', True]

# crear gerente
@app.callback([Output('alert_crear_gerente', 'children'),
               Output('alert_crear_gerente', 'color'),
               Output('alert_crear_gerente', 'is_open'),
               Output('documento_gerente', 'value'),
               Output('nombre_gerente', 'value'),
               Output('pais_gerente', 'value'),
               Output('planta_gerente', 'value'),
               Output('telefono_gerente', 'value'),
               Output('correo_gerente', 'value'),],
               #Output('pw_gerente', 'value')], 
              Input('confirm_crear_gerente', 'submit_n_clicks'),
              [State('user_info', 'data')] + [State(i, 'value') for i in ids_crear_gerente])
def creargerente(n, data, documento, nombre, pais, planta, telefono, correo, usuario, pw):
    if n is None:
        raise dash.exceptions.PreventUpdate()
    user = pd.read_json(data, orient = 'split')
    doc_id = user['doc_id'].values[0]
    if isinstance(documento, str) or documento is None:
        return ['Documento no valido', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    documentos = get_data('SELECT doc_id FROM usuarios')
    if False if documentos.shape[0] == 0 else documento in documentos['doc_id'].values:
        return ['Documento de identidad ya registrado', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    if nombre is None or nombre == '':
        return ['Nombre del Gerente no valido', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    if len(nombre.split()) < 2:
        return ['Por favor ingrese nombre y apellido del gerente', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    if pais is None or pais == '':
        return ['Pais no valido', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    if planta is None or planta == '':
        return ['Planta no valida', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    if telefono is None or len(telefono)<10:
        return ['Telefono de contacto no valido', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    if correo is None or not ('@' in correo) or not ('.com' in correo):
        return ['Correo electronico no valido', 'warning', True, documento, nombre, pais, planta, telefono, correo]    
    if usuario is None or usuario == '' or len(usuario.split()) != 1:
        return ['Nombre de usuario no valido', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    if usuario in get_data('SELECT usuario FROM usuarios')['usuario'].values:
        return ['Nombre de usuario ya registrado', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    if pw is None or pw == '' or len(str(pw)) < 8:
        return ['Contraseña de usuario no valida, recuerde que debe contar con al menos 8 caracteres', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    
    try:
        crear_usuario(usuario = usuario, rol = 'gerente', doc_id = documento, nombre = nombre, pw = pw, pais = pais)
        crear_gerente(nombre = nombre, documento = documento, planta = planta, pais = pais, especialista = 0, creador = user['nombre'].values[0], correo = correo, telefono = telefono)
        
        try:
            fecha = datetime.today().date()
            trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Crear gerente')
        except Exception as e:
            print(e)

        return ['Gerente creado con éxito', 'success', True, None, None, None, None, None, None]
    except Exception as e:
        print(e)
        return ['Gerente no creado, por favor intente mas tarde', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    
## actualizar campo usuario en funcion del correo, crear gerente
@app.callback(Output('usuario_gerente', 'value'),
              Input('correo_gerente', 'value'))
def usuarioCorreo(correo):
    if correo is None or not ('@' in correo):
        return None
    if '@' in correo:
        return correo.split('@')[0]
    else:
        return None

## actualizar campo usuario en funcion del correo, crear especialista
@app.callback(Output('usuario_especialista', 'value'),
              Input('correo_especialista', 'value'))
def usuarioCorreoE(correo):
    if correo is None or not ('@' in correo):
        return None
    if '@' in correo:
        return correo.split('@')[0]
    else:
        return None


# crear especialista
@app.callback([Output('alert_crear_especialista', 'children'),
               Output('alert_crear_especialista', 'color'),
               Output('alert_crear_especialista', 'is_open'),
               Output('documento_especialista', 'value'),
               Output('nombre_especialista', 'value'),
               Output('pais_especialista', 'value'),
               Output('planta_especialista', 'value'),
               Output('telefono_especialista', 'value'),
               Output('correo_especialista', 'value'),],
               #Output('pw_especialista', 'value')], 
              Input('confirm_crear_especialista', 'submit_n_clicks'),
              [State('user_info', 'data')] + [State(i, 'value') for i in ids_crear_especialista])
def crearEspecialista(n, data, documento, nombre, pais, planta, telefono, correo, usuario, pw):
    if n is None:
        raise dash.exceptions.PreventUpdate()
    user = pd.read_json(data, orient = 'split')
    doc_id = user['doc_id'].values[0]
    if isinstance(documento, str) or documento is None:
        return ['Documento no valido', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    documentos = get_data('SELECT doc_id FROM usuarios')
    if False if documentos.shape[0] == 0 else documento in documentos['doc_id'].values:
        return ['Documento de identidad ya registrado', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    if nombre is None or nombre == '':
        return ['Nombre del Gerente no valido', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    if len(nombre.split()) < 2:
        return ['Por favor ingrese nombre y apellido del gerente', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    if pais is None or pais == '':
        return ['Pais no valido', 'warning', True, documento, nombre, pais, planta, telefono, correo]    
    if planta is None or planta == '':
        return ['Planta no valida', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    if telefono is None or len(telefono)<10:
        return ['Telefono de contacto no valido', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    if correo is None or not ('@' in correo) or not ('.com' in correo):
        return ['Correo electronico no valido', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    if usuario is None or usuario == '' or len(usuario.split()) != 1:
        return ['Nombre de usuario no valido', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    if usuario in get_data('SELECT usuario FROM usuarios')['usuario'].values:
        return ['Nombre de usuario ya registrado', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    if pw is None or pw == '' or len(str(pw)) < 8:
        return ['Contraseña de usuario no valida, recuerde que debe contar con al menos 8 caracteres', 'warning', True, documento, nombre, pais, planta, telefono, correo]
    
    try:
        crear_usuario(usuario = usuario, rol = 'especialista', doc_id = documento, nombre = nombre, pw = pw, pais = pais)
        crear_gerente(nombre = nombre, documento = documento, planta = planta, pais = pais, especialista = 1, creador = user['nombre'].values[0], correo = correo, telefono = telefono)
        
        try:
            fecha = datetime.today().date()
            trazabilidad(user['doc_id'][0], user['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Crear especialista')
        except Exception as e:
            print(e)

        return ['Especialista creado con éxito', 'success', True, None, None, None, None, None, None]
    except Exception as e:
        print(e)
        return ['Especialista no creado, por favor intente mas tarde', 'warning', True, documento, nombre, pais, planta, telefono, correo]


# crear cliente no gerente
@app.callback([Output('alert_crear_cliente_ng', 'children'),
               Output('alert_crear_cliente_ng', 'color'),
               Output('alert_crear_cliente_ng', 'is_open'),
               Output('gerente_cliente', 'value'),
               Output('nit_cliente_ng', 'value'),
               Output('nombre_cliente_ng', 'value'),
               Output('telefono_cliente', 'value'),
               Output('correo_cliente', 'value'),],
               #Output('pw_cliente_ng', 'value'),],
               Input('confirm_crear_cliente_ng', 'submit_n_clicks'),
               [State('user_info', 'data')] + [State(i, 'value') for i in ids_crear_cliente_ng])
def crearcliente(n, data, gerente, nit, nombre, user, pw, telefono, correo):
    if n is None:
        raise dash.exceptions.PreventUpdate()
    usuario = pd.read_json(data, orient = 'split')
    doc_id = usuario['doc_id'].values[0]
    if gerente is None:
        return ['Gerente de zona no valido', 'warning', True, gerente, nit, nombre, telefono, correo]
    # if tipo is None:
    #     return ['Tipo de cliente no valido', 'warning', True, gerente, nit, nombre, telefono, correo]
    sql_ = f'''SELECT pais FROM gerentes WHERE documento_identidad = '{gerente}';'''
    pais = get_data(sql_)['pais'].values[0]
    if nit is None or nit == '':
        return ['Número de Nit no valido', 'warning', True, gerente, nit, nombre, telefono, correo]
    nit_ = get_data(sql = 'SELECT doc_id FROM usuarios;')
    if False if nit_.shape[0] == 0 else nit in nit_['doc_id'].values:
        return ['Número de nit ya registrado', 'warning', True, gerente, nit, nombre, telefono, correo]
    if nombre is None or nombre == '':
        return ['Nombre de cliente no valido', 'warning', True, gerente, nit, nombre, telefono, correo]
    if telefono is None or len(telefono)<10:
        return ['Telefono de contacto no valido', 'warning', True, gerente, nit, nombre, telefono, correo]
    if correo is None or not ('@' in correo) or not ('.com' in correo):
        return ['Correo electronico no valido', 'warning', True, gerente, nit, nombre, telefono, correo]
    if user is None or user == '' or len(user.split()) != 1:
        return ['Nombre de usuario no valido', 'warning', True, gerente, nit, nombre, telefono, correo]
    if user in get_data(sql = 'SELECT usuario FROM usuarios')['usuario'].values:
        return ['Nombre de usuario ya registrado', 'warning', True, gerente, nit, nombre, telefono, correo]
    if pw is None or pw == '' or len(str(pw)) < 8:
        return ['Contraseña de ingreso no valida, recuerde que debe contar con al menos 8 caracteres', 'warning', True,
                 gerente, nit, nombre, telefono, correo]
    try:
        crear_usuario(usuario = user, rol = 'cliente', doc_id = nit, nombre = nombre, pw = pw, pais = pais)
        crear_cliente(nit = nit, nombre = nombre, gerente = gerente, pais = pais, telefono = telefono, correo = correo, creador = usuario['doc_id'].values[0])

        try:
            fecha = datetime.today().date()
            trazabilidad(usuario['doc_id'][0], usuario['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Crear cliente')
        except Exception as e:
            print(e)
        return ['Cliente creado con éxito', 'success', True, None, None, None, None, None]

    except Exception as e:
        print(e)
        return ['Cliente no creado, por favor intente mas tarde', 'warning', True, gerente, nit, nombre, telefono, correo]


## actualizar campo usuario en funcion del correo, crear gerente
@app.callback(Output('usuario_cliente_ng', 'value'),
              Input('correo_cliente', 'value'))
def usuarioCorreo(correo):
    if correo is None or not ('@' in correo):
        return None
    if '@' in correo:
        return correo.split('@')[0]
    else:
        return None

## municipios en funcion de depto
@app.callback(Output('municipio_granja', 'options'),
              Input('depto_granja', 'value'))
def mun_depto(depto):
    if depto is None:
        return no_update
    divipola = pd.read_csv('Datos/Divipola.csv')
    municipios = divipola[divipola['Departamento'].isin(depto)]['Municipio']

    return [{'label': i, 'value': i} for i in municipios.sort_values()]

# cargar nits agregar galpon no cliente
# @app.callback(Output('nit_clientes_galpon_nc', 'options'),
#               Input('gerente_galpon_nc', 'value'),
#               State('user_info', 'data'))
# def cargatnitGerente(gerente, data):
#     usuario = pd.read_json(data, orient = 'split')
#     rol = usuario['rol_usuario'].values[0]
#     if rol == 'cliente':
#         raise dash.exceptions.PreventUpdate()
#     if rol in ['administrador', 'gerente']:
#         if gerente is None:
#             return [{'label': 'Seleccione un gerente', 'value': None}]
#     try:
#         nit = get_data(f'''SELECT nit, nombre_cliente FROM clientes WHERE gerente_zona = '{gerente}';''')
#     except Exception as e:
#         print(e)
#         return [{'label': 'Error al consultar clientes', 'value': None}]
#     if nit.empty:
#         return [{'label': 'Sin registros en clientes clientes', 'value': None}]
#     nit.sort_values(axis = 0, by = ['nombre_cliente'], inplace = True)
#     nit.reset_index(drop = True, inplace = True)
#     return [{'label': nit['nombre_cliente'][i], 'value': nit['nit'][i]} for i in range(nit.shape[0])]

# cargar granjas agregar galpon no cliente
# @app.callback(Output('granja_galpon_nc', 'options'),
#               Input('nit_clientes_galpon_nc', 'value'))
# def nombreClienteNit(nit):
#     if nit is None:
#         return [{'label': 'Seleccione un cliente', 'value': None}]
#     try:
#         granjas = get_data(f'''SELECT id_granja, nombre_granja FROM granjas WHERE nit_cliente = '{nit}';''')
#     except Exception as e:
#         print(e)
#         return [{'label': 'Error al consultar granjas', 'value': None}]
#     if granjas.empty:
#         return [{'label': 'Sin registros en granjas', 'value': None}]
#     granjas.sort_values(axis = 0, by = ['nombre_granja'], inplace = True)
#     granjas.reset_index(drop = True, inplace = True)
#     return [{'label': granjas['nombre_granja'][i], 'value': granjas['id_granja'][i]} for i in range(granjas.shape[0])]


# cargar nit ver granja no cliente
@app.callback(Output('nit_cliente_ver_granjas', 'options'),
              Input('gerente_ver_granjas_nc', 'value'),
              State('user_info', 'data'))
def nirClienteVerGranja(gerente, data):
    user = pd.read_json(data, orient = 'split')
    doc_id = user['doc_id'].values[0]
    rol = user['rol_usuario'].values[0]
    if rol == 'cliente':
        raise dash.exceptions.PreventUpdate()
    else:
        if gerente is None:
            return [{'label': 'Seleccione un gerente', 'value': None}]
    try:
        clientes = get_data(f'''SELECT nit, nombre_cliente FROM clientes WHERE gerente_zona = '{gerente}';''')
    except Exception as e:
        print(e)
        return [{'label': 'Error al consultar', 'value': None}]
    if clientes.empty:
        return [{'label': 'Sin registros', 'value': None}]


    return [{'label': clientes['nombre_cliente'][i], 'value': clientes['nit'][i]} for i in range(clientes.shape[0])]

# cargar nit ver unidades productivas
@app.callback(Output('nit_cliente_ver_up', 'options'),
              Input('gerente_ver_up_nc', 'value'),
              State('user_info', 'data'))
def nitClienteVerUp(gerente, data):
    usuario = pd.read_json(data, orient = 'split')
    doc_id = usuario['doc_id'].values[0]
    rol = usuario['rol_usuario'].values[0]
    if rol == 'cliente':
        raise dash.exceptions.PreventUpdate()
    else:
        if gerente is None:
            return [{'label': 'Seleccione un gerente', 'value': None}]
    try:
        clientes = get_data(f'''SELECT nit, nombre_cliente FROM clientes WHERE gerente_zona = '{gerente}';''')
    except Exception as e:
        print(e)
        return [{'label': 'Error al consultar', 'value': None}]
    if clientes.empty:
        return [{'label': 'Sin registros', 'value': None}]
    return [{'label': clientes['nombre_cliente'][i], 'value': clientes['nit'][i]} for i in range(clientes.shape[0])]


# cargar nit ver GALPON no cliente
# @app.callback(Output('nit_cliente_ver_galpones', 'options'),
#               Input('gerente_ver_galpones_nc', 'value'),
#               State('user_info', 'data'))
# def nirClienteVerGalpon(gerente, data):
#     usuario = pd.read_json(data, orient = 'split')
#     doc_id = usuario['doc_id'].values[0]
#     rol = usuario['rol_usuario'].values[0]
#     if rol == 'cliente':
#         raise dash.exceptions.PreventUpdate()
#     else:
#         if gerente is None:
#             return [{'label': 'Seleccione un gerente', 'value': None}]
#     try:
#         clientes = get_data(f'''SELECT nit, nombre_cliente FROM clientes WHERE gerente_zona = '{gerente}';''')
#     except Exception as e:
#         print(e)
#         return [{'label': 'Error al consultar', 'value': None}]
#     if clientes.empty:
#         return [{'label': 'Sin registros', 'value': None}]
#     return [{'label': clientes['nombre_cliente'][i], 'value': clientes['nit'][i]} for i in range(clientes.shape[0])]

# cargar granja ver GALPON no cliente
# @app.callback(Output('granjas_nc', 'options'),
#               Input('nit_cliente_ver_galpones', 'value'),
#               State('user_info', 'data'))
# def nitClienteVerGalpon(nit, data):
#     usuario = pd.read_json(data, orient = 'split')
#     doc_id = usuario['doc_id'].values[0]
#     rol = usuario['rol_usuario'].values[0]
#     if rol == 'cliente':
#         raise dash.exceptions.PreventUpdate()
#     else:
#         if nit is None or len(nit) < 0:
#             return [{'label': 'Seleccione un cliente', 'value': None}]
#     if rol == 'cliente':
#         sql = f'''SELECT id_granja, nombre_granja FROM granjas WHERE nit_cliente = '{nit}';'''
#     else:
#         nit_sql = '('
#         for i in nit:
#             nit_sql = nit_sql + str(i)
#             if int(i) == nit[-1]:
#                 nit_sql = nit_sql + ')'
#             else:
#                 nit_sql = nit_sql + ',' 
#         sql = f'''SELECT id_granja, nombre_granja FROM granjas WHERE nit_cliente IN {nit_sql};'''       
#     try:
#         granjas = get_data(sql)
#     except Exception as e:
#         print(e)
#         return [{'label': 'Error al consultar', 'value': None}]
#     if granjas.empty:
#         return [{'label': 'Sin registros', 'value': None}]
#     return [{'label': granjas['nombre_granja'][i], 'value': granjas['id_granja'][i]} for i in range(granjas.shape[0])]

## configurar contraseña crear cliente
@app.callback(Output('pw_cliente_ng', 'value'),
             Input('nit_cliente_ng', 'value'))
def set_password_c(n):
    if n is None or len(str(n)) == 0:
        return None
    else:
        return n


## configurar contraseña crear gerente
@app.callback(Output('pw_gerente', 'value'),
             Input('documento_gerente', 'value'))
def set_password_g(n):
    if n is None or len(str(n)) == 0:
        return None
    else:
        return n

## configurar contraseña crear especialista
@app.callback(Output('pw_especialista', 'value'),
             Input('documento_especialista', 'value'))
def set_password_e(n):
    if n is None or len(str(n)) == 0:
        return None
    else:
        return n



## collapsible reporte seguimiento semanal
@app.callback(Output('collapse_ss', 'is_open'),
              Input('collapse_button_ss', 'n_clicks'),
              State('collapse_ss', 'is_open'))
def collapsess(n, is_open):
    if n:
        return not is_open
    return is_open

## collapsible reporte liquidaciones
@app.callback(Output('collapse_lq', 'is_open'),
              Input('collapse_button_lq', 'n_clicks'),
              State('collapse_lq', 'is_open'))
def collapselq(n, is_open):
    if n:
        return not is_open
    return is_open

## collapsible reporte compromisos
@app.callback(Output('collapse_cp', 'is_open'),
              Input('collapse_button_cp', 'n_clicks'),
              State('collapse_cp', 'is_open'))
def collapsecp(n, is_open):
    if n:
        return not is_open
    return is_open

## collapsible info app
@app.callback(Output('collapse_info_app', 'is_open'),
              Input('collapse_button_info_app', 'n_clicks'),
              State('collapse_info_app', 'is_open'))
def collapse_info_app(n, is_open):
    if n:
        return not is_open
    return is_open


## collapsible pw
@app.callback(Output('collapse_pw', 'is_open'),
              Input('collapse_button_pw', 'n_clicks'),
              State('collapse_pw', 'is_open'))
def collapsepw(n, is_open):
    if n:
        return not is_open
    return is_open

## collapsible mis clientes
@app.callback(Output('collapse_mis_clientes', 'is_open'),
              Input('callapse_button_mis_clientes', 'n_clicks'),
              State('collapse_mis_clientes', 'is_open'))
def collapsemisclientes(n, is_open):
    if n:
        return not is_open
    return is_open


## collapsible crear cliente
@app.callback(Output('collapse_crear_cliente', 'is_open'),
              Input('callapse_button_crear_cliente', 'n_clicks'),
              State('collapse_crear_cliente', 'is_open'))
def collapseCrearCliente(n, is_open):
    if n:
        return not is_open
    return is_open

## collapsible crear especialista
@app.callback(Output('collapse_crear_especialista', 'is_open'),
              Input('callapse_button_crear_especialista', 'n_clicks'),
              State('collapse_crear_especialista', 'is_open'))
def collapseCrearEspecialista(n, is_open):
    if n:
        return not is_open
    return is_open


## collapsible crear gerente
@app.callback(Output('collapse_crear_gerente', 'is_open'),
              Input('callapse_button_crear_gerente', 'n_clicks'),
              State('collapse_crear_gerente', 'is_open'))
def collapseCrearGerente(n, is_open):
    if n:
        return not is_open
    return is_open

## collapsible ver especialistas
@app.callback(Output('collapse_ver_especialistas', 'is_open'),
              Input('callapse_button_ver_especialistas', 'n_clicks'),
              State('collapse_ver_especialistas', 'is_open'))
def collapseVerEspecialista(n, is_open):
    if n:
        return not is_open
    return is_open

## collapsible ver gerentes
@app.callback(Output('collapse_ver_gerentes', 'is_open'),
              Input('callapse_button_ver_gerentes', 'n_clicks'),
              State('collapse_ver_gerentes', 'is_open'))
def collapseVerGerente(n, is_open):
    if n:
        return not is_open
    return is_open

## collapsible mis granja
@app.callback(Output('collapse_mis_granjas', 'is_open'),
              Input('callapse_button_mis_granjas', 'n_clicks'),
              State('collapse_mis_granjas', 'is_open'))
def collapseMisGranjas(n, is_open):
    if n:
        return not is_open
    return is_open

## collapsible trazabilidad
@app.callback(Output('collapse_trz', 'is_open'),
              Input('collapse_button_trz', 'n_clicks'),
              State('collapse_trz', 'is_open'))
def collapse_trz(n, is_open):
    if n:
        return not is_open
    return is_open

## collapsible mis unidades productivas
@app.callback(Output('collapse_mis_up', 'is_open'),
              Input('callapse_button_mis_up', 'n_clicks'),
              State('collapse_mis_up', 'is_open'))
def collapseMisUp(n, is_open):
    if n:
        return not is_open
    return is_open

## collapsible mis galpones
# @app.callback(Output('collapse_mis_galpones', 'is_open'),
#               Input('callapse_button_mis_galpones', 'n_clicks'),
#               State('collapse_mis_galpones', 'is_open'))
# def collapsecreargerente(n, is_open):
#     if n:
#         return not is_open
#     return is_open

## collapsible crear granja
@app.callback(Output('collapse_crear_granja', 'is_open'),
              Input('callapse_button_crear_granja', 'n_clicks'),
              State('collapse_crear_granja', 'is_open'))
def collapseCrearGranja(n, is_open):
    if n:
        return not is_open
    return is_open

## collapsible crear unidad productiva
@app.callback(Output('collapse_crear_up', 'is_open'),
              Input('callapse_button_crear_up', 'n_clicks'),
              State('collapse_crear_up', 'is_open'))
def collapseCrearUp(n, is_open):
    if n:
        return not is_open
    return is_open


## collapsible agregar galpon
# @app.callback(Output('collapse_agregar_galpon', 'is_open'),
#               Input('callapse_button_agregar_galpon', 'n_clicks'),
#               State('collapse_agregar_galpon', 'is_open'))
# def collapseAgregarGalpon(n, is_open):
#     if n:
#         return not is_open
#     return is_open

# cambiar planta por pais gerente
@app.callback(Output('planta_gerente', 'options'),
              Input('pais_gerente', 'value'))
def plantas(pais):
    if pais is None:
        return no_update
    if pais == 'COLOMBIA':
        plantas = ['FUNZA', 'COTA', 'PALERMO', 'VILLAVICENCIO', 'IBAGUÉ', 'BARRANQUILLA', 'GIRÓN', 'GIRARDOTA', 'PALMIRA', 'PEREIRA']
        return [{'label': i, 'value': i} for i in plantas]
    
    if pais == 'ECUADOR':
        plantas = ['ECUADOR']
        return [{'label': i, 'value': i} for i in plantas]        

    if pais == 'PANAMÁ':
        plantas = ['PANAMÁ']
        return [{'label': i, 'value': i} for i in plantas]  

# cambiar planta por pais especialista
@app.callback(Output('planta_especialista', 'options'),
              Input('pais_especialista', 'value'))
def plantas_e(pais):
    if pais is None:
        return no_update
    if pais == 'COLOMBIA':
        plantas = ['FUNZA', 'COTA', 'PALERMO', 'VILLAVICENCIO', 'IBAGUÉ', 'BARRANQUILLA', 'GIRÓN', 'GIRARDOTA', 'PALMIRA', 'PEREIRA']
        return [{'label': i, 'value': i} for i in plantas]
    
    if pais == 'ECUADOR':
        plantas = ['ECUADOR']
        return [{'label': i, 'value': i} for i in plantas]        

    if pais == 'PANAMÁ':
        plantas = ['PANAMÁ']
        return [{'label': i, 'value': i} for i in plantas]  


## cambiar constraseña
@app.callback([Output('alert_pw', 'children'),
               Output('alert_pw', 'color'),
               Output('alert_pw', 'is_open')],
              Input('confirm_pw', 'submit_n_clicks'),
              [State('old_pw', 'value'),
               State('new_pw', 'value'),
               State('user_info', 'data')])
def cambio_contraseña(n, old, new, data):
    usuario = pd.read_json(data, orient = 'split')
    if n is None:
        raise dash.exceptions.PreventUpdate()
    if old is None or old == '' :
        return ['Contraseña actual en blanco, por favor verifique', 'danger', True]
    if old is None or old == '' or new is None or new == '':
        return ['Contraseña nueva en blanco, por favor verifique', 'danger', True]
    if len(new) < 8:
        return ['Recuerde que la contraseña debe contar con 8 caracteres como mínimo', 'danger', True]
    if old != get_data(f"SELECT contraseña FROM usuarios WHERE usuario = '{usuario['usuario'].values[0]}'")['contraseña'].values[0]:
        return ['Contraseña actual no coincide, por favor verifique', 'danger', True]
    try:
        change_pw(new_pw = new, user = usuario['usuario'].values[0])

        try:
            fecha = datetime.today().date()
            trazabilidad(usuario['doc_id'][0], usuario['rol_usuario'][0], datetime.strftime(fecha, '%Y-%m-%d'), 'Cambio de contraseña')
        except Exception as e:
            print(e)  

        return ['Contraseña restablecida con éxito', 'success', True]
    except:
        return ['Error al cambiar la contraseña', 'danger', True]




###############################################################################
# run app
###############################################################################

if __name__ == "__main__":

    app.server.run(
        debug=True,
        #host='127.0.0.1',
        host='0.0.0.0', 
        port = port
    )
