import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html 
from datetime import datetime, date
import pandas as pd


def campos(id_ = '', label = '', ayuda = '', tipo = '', plh = '', valor = '',
           xl = 2, lg = 2, md = 4, sm = 5, xs = 6, vl = '', style_ = {'padding-left': '1px'}, 
           style_col = {}, s_date = '', f_date = ''):
    if tipo == 'text' or tipo == 'number':
        text_input = dbc.Col(id = id_ + '_col', children = [
            dbc.FormGroup(id = id_ + '_sal', children = [
                dbc.Label(id = id_ + '_label', children = label),
                dbc.Input(id = id_, placeholder = plh, type = tipo,
                          debounce = True, value = valor),
                dbc.FormText(id = id_ + '_ayuda', children = ayuda)
                ], style = style_)
            ], xl = xl, lg = lg, md = md, sm = sm, xs = xs, style = style_col)
        return text_input

    if tipo == 'pw':
        text_input = dbc.Col(id = id_ + '_col', children = [
            dbc.FormGroup(id = id_ + '_sal', children = [
                dbc.Label(id = id_ + '_label', children = label),
                dbc.Input(id = id_, placeholder = plh, type = 'password',
                          debounce = True, value = valor),
                dbc.FormText(id = id_ + '_ayuda', children = ayuda)
                ], style = style_)
            ], xl = xl, lg = lg, md = md, sm = sm, xs = xs,
            style = style_col)
        return text_input

    if tipo == 'date':
        text_input = dbc.Col(id = id_ + '_col', children = [
            dbc.FormGroup(
                [
                dbc.Label(label),
                dcc.DatePickerSingle(id = id_, date = valor, style = style_,
                                     display_format='YYYY/MM/DD'),
                dbc.FormText(ayuda, style = {'padding-left': '3px'})
                ], style = style_)
            ], xl = xl, lg = lg, md = md, sm = sm, xs = xs,
            style = style_col)
        return text_input

    if tipo == 'date_2':
        text_input = dbc.Col(id = id_ + '_col', children = [
            dbc.FormGroup(
                [
                dbc.Label(label),
                dcc.DatePickerRange(
                    id = id_,
                    month_format = 'MMMM Y',
                    end_date_placeholder_text = 'MMMM Y',
                    start_date = s_date,
                    end_date = f_date,
                    display_format='YYYY/MM/DD'
                ),
                # dcc.DatePickerSingle(id = id_, date = valor, style = style_,
                #                      display_format='YYYY/MM/DD'),
                dbc.FormText(ayuda, style = {'padding-left': '3px'})
                ], style = style_)
            ], xl = xl, lg = lg, md = md, sm = sm, xs = xs,
            style = style_col)
        return text_input

    if tipo == 'slider':
        text_input = dbc.Col(id = id_ + '_col', children = [
            dbc.FormGroup(
                [
                dbc.Label(label),
                dcc.Slider(id = id_, min = 1, max = 49, value = 10,
                           #marks = {i: str(i) for i in range(1, 10)},
                           tooltip = {'always_visible': True}),
                dbc.FormText(ayuda)
                ], style = style_)
            ], xl = xl, lg = lg, md = md, sm = sm, xs = xs,
            style = style_col)
        return text_input

    if tipo == 'seleccion':
        text_input = dbc.Col(id = id_ + '_col', children = [
            dbc.FormGroup(
                [
                dbc.Label(label),
                dbc.Select(id = id_,
                           options = valor,
                           value = vl),
                dbc.FormText(ayuda)
                ], style = style_)
            ], xl = xl, lg = lg, md = md, sm = sm, xs = xs,
            style = style_col)
        return text_input

    if tipo == 'seleccion_m':
        text_input = dbc.Col([
            dbc.FormGroup(
                [
                dbc.Label(label),
                dcc.Dropdown(id = id_,
                           options = valor,
                           multi = True,
                           value = vl),
                dbc.FormText(ayuda)
                ], style = style_)
            ], xl = xl, lg = lg, md = md, sm = sm, xs = xs,
            style = style_col)
        return text_input

    if tipo == 'depto':
        deptos = pd.read_csv('Datos/Divipola.csv')
        text_input = dbc.Col([
            dbc.FormGroup(
                [
                dbc.Label(label),
                dcc.Dropdown(id = id_,
                           options = [{'label': i, 'value': i} for i in deptos['Departamento'].unique()],
                           multi = True
                           ),
                dbc.FormText(ayuda)
                ], style = style_)
            ], xl = xl, lg = lg, md = md, sm = sm, xs = xs,
            style = style_col)
        return text_input

    if tipo == 'seleccion_2':
        text_input = dbc.Col(id = id_ + '_col', children = [
            dbc.FormGroup(
                [
                dbc.Label(label),
                dbc.Checklist(id = id_,
                           options = valor,
                           switch=True),
                dbc.FormText(ayuda)
                ]), #style = {'padding-left': '15px'})
            ], xl = xl, lg = lg, md = md, sm = sm, xs = xs)
        return text_input

    if tipo == 'text_area':
        text_input = dbc.Col([
            dbc.FormGroup(
                [
                dbc.Label(label),
                dbc.Textarea(id = id_, bs_size = 'sm',
                             placeholder = 'Por favor ingrese sus observaciones'),
                dbc.FormText(ayuda)
                ], style = style_)
            ], xl = xl, lg = lg, md = md, sm = sm, xs = xs,
            style = style_col)
        return text_input

    if tipo == 'boton':
        input = dbc.Col([
                    dbc.Button(valor, id = id_)
                ], xl = xl, lg = lg, md = md, sm = sm, xs = xs,
                style = style_col)
        return input


tipo_estanque = ['ALEVINAJE', 'JUVENILES', 'PRE-ENGORDE', 'ENGORDE']
especies = {'MR': 'TILAPIA ROJA',
            'TN': 'TILAPIA NILOTICA',
            'TR': 'TRUCHA',
            'CH': 'CACHAMA',
            'BB': 'BAGRE BASSA',
            'CV': 'CAMARÓN VANNA'}

aireadores = ['BLOWER', 'INYECTOR', 'PALETAS', 'SPLASH', 'VENTURI', 'NINGUNO']

marcas_alimento = {
    'CONTEGRAL': ['Tilapias Iniciación', 'Maxi-Peces 38', 'Maxi-Peces 32',
                'Maxi-Peces 28', 'Peces 25', 'Truchas iniciación',
                'Maxi-Truchas 45', 'Truchas 40 SP', 'Truchas 40 CP'],
    'SOLLA': ['Mojarras 45%', 'Mojarras38%', 'Mojarras 32%', 'Mojarras 24%',
            'SollaPeces 20%', 'Mojarras 32% Reproductores', 'Truchas 50%',
            'Truchas 43%', 'Truchas 40% CC'],
    'AGRINAL': ['Tilapia Reversión', 'Tilapia 45', 'Tilapia 38', 'Tilapia 30',
                'Tilapia 24', 'Trucha48 Iniciación', 'Truchas 45%', 'Truchas 40% CP',
                'Truchas 40% SP'],
    'FINCA': ['Mojarra iniciación 40%', 'Mojarra 35%', 'Mojarra engorde 25%'], 
    'CIPA': ['Acuavit Mojarras Iniciación 45%', 'Acuavit Mojarras Prelevante 40%',
            'Acuavit Mojarras Levante 35%', 'Acuavit Mojarras 30%',
            'Acuavit Mojarras Engorde Extensivo 24%', 'Mojarras 20%',
            'Acuavit Truchas Iniciación 52%', 'Acuavit Truchas Levante 44%',
            'Acuavit Truchas Finalización 40%', 'Acuavit Truchas Finalización 40% con Pigmento',
            'Acuavit Truchas Finalización 40% con Pigmento reforzado'], 
    'RAZA': ['Aevines Tropicales 45%', 'Alevines Tropicales 42%', 'Peces Tropicales 38%',
            'Peces Tropicales Juveniles 35%', 'Peces Tropicales 32%', 'Peces Tropicales 30%',
            'Peces tropicales 25%', 'Truchas 45% sin Pigmento', 'Truchas  42% sin Pigmento',
            'Truchas  42% con Pigmento'], 
    'HACIENDA': ['Peces 24%', 'Peces 32%', 'Peces 38%',
                'Peces 45%', 'Truchas 40%', 'Truchas  44%'], 
    'ITALCOL': ['ITALREV', 'M-45% H', 'M-45% Pr E', 'M-45% E', 'M38% E - 2mm',
                'M38% E - 3mm', 'M34% E - 3mm', 'M34% E - 4mm', 'M32% E',
                'M28% E', 'M30% E', 'M24% E', 'M20% E', 'TR Inc 50%', 'TR Lev 40%',
                'TR Fin 40% Pig', 'TR Eng 40%', 'TR Fin 40% Spig', 'TIL 45% H St',
                'TIL 45% Alev', 'TIL 38% Alev', 'TIL 32% Lev', 'TIL 28% PrEn',
                'TIL 24% En', 'Camarón 35% E', 'CAM Perf 35% Grw', 'CAM Perf 28% Aqf']
    }

## campos consulta de informacion
ids_consulta_ss = ['gerente_consulta', 'cliente_consulta', 'granja_consulta', 'año_consulta', 'lote_consulta',]

ids_consulta_i = ['tabla_inventario', 'gerente_consulta_i', 'cliente_consulta_i', 'granja_consulta_i', 'año_consulta_i', 'lote_consulta_i',]

año_consulta = campos(id_ = 'año_consulta', label = 'AÑO', ayuda = '-', tipo = 'seleccion_m',
                      valor = [{'label': i, 'value': i} for i in '-'], vl = None,
                      xl = 3, lg = 3, md = 4, sm = 5, xs = 6)
lote_consulta = campos(id_ = 'lote_consulta', label = 'LOTE', ayuda = '-', tipo = 'seleccion_m',
                      valor = [{'label': i, 'value': i} for i in '-'], vl = None,
                      xl = 3, lg = 3, md = 4, sm = 5, xs = 6)

año_consulta_i = campos(id_ = 'año_consulta_i', label = 'AÑO', ayuda = '-', tipo = 'seleccion_m',
                      valor = [{'label': i, 'value': i} for i in '-'], vl = None,
                      xl = 3, lg = 3, md = 4, sm = 5, xs = 6)
lote_consulta_i = campos(id_ = 'lote_consulta_i', label = 'LOTE', ayuda = '-', tipo = 'seleccion_m',
                      valor = [{'label': i, 'value': i} for i in '-'], vl = None,
                      xl = 3, lg = 3, md = 4, sm = 5, xs = 6)

tabla_inventario = campos(id_ = 'tabla_inventario', label = 'INVENTARIO', ayuda = 'Seleccione una tabla',
                          tipo = 'seleccion', valor = [{'value': i, 'label': i} for i in ['ALIMENTO', 'PESCAS', 'TRASLADOS']], 
                          xl = 3, lg = 3, md = 4, sm = 5, xs = 6)

## campos ingreso de datos
fecha_ingreso = campos(id_ = 'fecha_ingreso', label = '', ayuda = '-', tipo = 'date',
                       valor = datetime.today().date(), style_col = {'display': 'inline'},
                       xl = 3, lg = 3, md = 4, sm = 6, xs = 8)

lote_ingreso = campos(id_ = 'lote_ingreso', label = 'LOTE', ayuda = '-', tipo = 'seleccion',
                      valor = [{'label': 'Sin registros', 'value': '{"value": "-", "label": "Sin registros"}'}])

fecha_siembra_ingreso = campos(id_ = 'fecha_siembra_ingreso', label = 'FECHA SIEMBRA', ayuda = '-', tipo = 'date',
                       valor = datetime.today().date())
                       
estanque_ingreso = campos(id_ = 'estanque_ingreso', label = 'ESTANQUE', tipo = 'seleccion', ayuda = '-',
                          valor = [{'label': i, 'value': i} for i in ['Seleccione una granja']], vl = None)
tipo_estanque_ingreso = campos(id_ = 'tipo_estanque_ingreso', label = 'TIPO ESTANQUE', ayuda = '-', vl = None,
                               tipo = 'seleccion', valor = [{'label': i, 'value': i} for i in ['ESTANQUE SEMI-INTENSIVO TRADICIONAL', 'ESTANQUE CON AIREACIÓN', 'BIOFLOC', 'IPRS', 'GEOMENBRANA CON AIREACIÓN', 'RACEWAY CONCRETO', 'RACEWAY TIERRA', 'JAULA']],
                               xl=4, lg=4, md=6, sm=8, xs=10)
especie_ingreso = campos(id_ = 'especie_ingreso', label = 'ESPECIE SEMBRADA', ayuda = '-', tipo = 'seleccion',
                         valor = [{'label': especies[i], 'value': i} for i in especies], vl = None,
                         xl = 3, lg = 4, md = 6, sm = 8, xs = 10)
genetica_ingreso = campos(id_ = 'genetica_ingreso', label = 'LINEA GENÉTICA', ayuda = 'Seleccione una linea',
                          tipo = 'seleccion', style_ = {'display': 'hidden'},
                          valor = [{'label': 'SELECCIONE UNA ESPECIE', 'value': None}], vl = None,
                          xl = 3, lg = 4, md = 6, sm = 8, xs = 10)

peso_siembra_ingreso = campos(id_ = 'peso_siembra_ingreso', label = 'PESO SIEMBRA', ayuda = 'Gramos', tipo = 'number',
                              valor = None)
talla_ingreso = campos(id_ = 'talla_ingreso', label = 'TALLA', ayuda = 'Centimetros', tipo = 'number',
                              valor = None)
numero_inicial_peces_ingreso = campos(id_ = 'numero_inicial_peces_ingreso', label = 'Nº INCIAL PECES', ayuda = 'Cantidad', tipo = 'number',
                              valor = None)
area_m2_ingreso = campos(id_ = 'area_m2_ingreso', label = 'ÁREA', ayuda = 'Metros cuadrados', tipo = 'number',
                              valor = None)
vol_m3_ingreso = campos(id_ = 'vol_m3_ingreso', label = 'VOLUMEN', ayuda = 'Metros cubicos', tipo = 'number',
                              valor = None)
aireacion_ingreso = campos(id_ = 'aireacion_ingreso', label = 'AIREACIÓN', ayuda = 'HP', tipo = 'number',
                              valor = None)
tipo_aireador_ingreso = campos(id_ = 'tipo_aireador_ingreso', label = 'TIPO AIREADOR', ayuda = '-', tipo = 'seleccion',
                               valor = [{'label': i, 'value': i} for i in aireadores])
etapa_cultivo_ingreso = campos(id_ = 'etapa_cultivo_ingreso', label = 'FASE CULTIVO', ayuda = '-', vl = None,
                               tipo = 'seleccion', valor = [{'label': i, 'value': i} for i in ['ALEVINAJE', 'LEVANTE', 'ENGORDE', 'CICLO COMPLETO',]])
prc_viseras_ingreso = campos(id_ = 'prc_viseras_ingreso', label = '% VISERAS', ayuda = '-', tipo = 'number',
                              valor = None)

# seguimiento alimentacion
# dias_ultima_fecha = campos(id_ = 'dias_ultima_fecha', label = 'DÍAS CULTIVO CONSOLIDADO', ayuda = '-',
#                            tipo = 'number', xl = 3, lg = 4, md = 6, sm = 8, xs = 8, valor = None)
# alimento_ultima_fecha = campos(id_ = 'alimento_ultima_fecha', label = 'KG ALIMENTO ACUMULADO', ayuda = 'Cantidad de alimento acumulado',
#                                tipo = 'number', valor = None, xl = 3, lg = 4, md = 8, sm = 6, xs = 8)
marca_alimento = campos(id_ = 'marca_alimento', label = 'MARCA ALIMENTO', ayuda = '-', tipo = 'seleccion_m', 
                        valor = [{'label': i, 'value': i} for i in sorted(marcas_alimento)], vl = None)

rango_fecha_alm = campos(id_ = 'rango_fecha_alm', label = 'RANGO FECHA ALIMENTACIÓN', ayuda = 'Fecha inicial - Fecha final', 
                     tipo = 'date_2', s_date = datetime.today().date(),
                     f_date = datetime.today().date(),
                     xl = 4, lg = 6, md = 8, sm = 10, xs = 12)

n_fuentes_alimento = campos(id_ = 'n_fuentes_alimento', label = 'NÚMERO DE FUENTES DE ALIMENTO USADOS', ayuda = '-',
                            tipo = 'number', valor = 1, xl = 4, lg = 4, md = 6, sm = 8, xs = 8)
tipo_alimento_ingreso = campos(id_ = 'tipo_alimento_ingreso', label = 'TIPO ALIMENTO', ayuda = '% Proteina',
                               tipo = 'seleccion', valor = None, style_col={'display': 'none'})
precio_b_ingreso = campos(id_ = 'precio_b_ingreso', label = 'PRECIO B x 40 Kg', ayuda = '-',
                               tipo = 'number', valor = None)
kg_real_ingreso = campos(id_ = 'kg_real_ingreso', label = 'Kg REAL', ayuda = '-', tipo = 'number', valor = None)

# seguimiento al crecimiento
# fecha_muestreo_anterior = campos(id_ = 'fecha_muestreo_anterior', label = 'FECHA MUESTREO ANTERIOR', ayuda = '-', tipo = 'date',
#                        valor = datetime.today().date(), xl = 3, lg = 4, md = 6, sm = 8, xs = 8)
rango_fecha_cre = campos(id_ = 'rango_fecha_cre', label = 'RANGO FECHA CRECIMIENTO', ayuda = 'Fecha inicial - Fecha final', 
                     tipo = 'date_2', s_date = datetime.today().date(),
                     f_date = datetime.today().date(),
                     xl = 4, lg = 6, md = 8, sm = 10, xs = 12)
real_ingreso = campos(id_ = 'real_ingreso', label = 'PESO PROMEDIO', ayuda = 'Gramos', tipo = 'number', valor = None)
longitud_crecimiento = campos(id_ = 'longitud_crecimiento', label = 'LONGITUD PROMEDIO', ayuda = 'Centimetros', tipo = 'number', 
                              valor = None, xl = 3, lg = 4, md = 6, sm = 8, xs = 8)

# inventario estanque
rango_fecha_mort = campos(id_ = 'rango_fecha_mort', label = 'RANGO FECHA MORTALIDAD', ayuda = 'Fecha inicial - Fecha final', 
                     tipo = 'date_2', s_date = datetime.today().date(),
                     f_date = datetime.today().date(),
                     xl = 4, lg = 6, md = 8, sm = 10, xs = 12)
mortalidad_ingreso = campos(id_ = 'mortalidad_ingreso', label = 'MORTALIDAD', ayuda = 'Número',
                            tipo = 'number', valor = None)
# fecha_mort_anterior = campos(id_ = 'fecha_mort_anterior', label = 'FECHA MORTALIDAD ANTERIOR', ayuda = '-', tipo = 'date',
#                        valor = datetime.today().date(), xl = 3, lg = 4, md = 6, sm = 8, xs = 8)
peso_mortalidad_ingreso = campos(id_ = 'peso_mortalidad_ingreso', label = 'PESO MORTALIDAD', ayuda = 'Kilogramo',
                            tipo = 'number', valor = None)
translado_ingreso = campos(id_ = 'translado_ingreso', label = 'TRASLADOS', ayuda = 'Número',
                           tipo = 'number', valor = 1)
vacunacion_traslado = campos(id_ = 'vacunacion_traslado', label = 'VACUNACIÓN', ayuda = '-',
                          tipo = 'seleccion', style_ = {'display': 'hidden'},
                          valor = [{'label': 'SELECCIONE UNA ESPECIE', 'value': None}], vl = None,
                          xl = 3, lg = 4, md = 6, sm = 8, xs = 10)
fecha_tras_anterior = campos(id_ = 'fecha_tras_anterior', label = 'FECHA TRASLADO ANTERIOR', ayuda = '-', tipo = 'date',
                       valor = datetime.today().date(), xl = 3, lg = 4, md = 6, sm = 8, xs = 8)
fecha_translado_ingreso = campos(id_ = 'fecha_translado_ingreso', label = 'FECHA TRASLADO', ayuda = '-', tipo = 'date',
                       valor = datetime.today().date())
# fecha_pesc_anterior = campos(id_ = 'fecha_pesc_anterior', label = 'FECHA TRASLADO ANTERIOR', ayuda = '-', tipo = 'date',
#                        valor = datetime.today().date(), xl = 3, lg = 4, md = 6, sm = 8, xs = 8)
fecha_pesca_ingreso = campos(id_ = 'fecha_pesca_ingreso', label = 'FECHA PESCA', ayuda = '-', tipo = 'date',
                       valor = datetime.today().date())
estanque_destino_ingreso = campos(id_ = 'estanque_destino_ingreso', label = 'ESTANQUE DESTINO', tipo = 'seleccion', ayuda = '-',
                          valor = [{'label': i, 'value': i} for i in ['Seleccione una granja']], vl = None)
numero_pesca_ingreso = campos(id_ = 'numero_pesca_ingreso', label = 'NÚMERO DE PESCAS', ayuda = 'Número',
                               tipo = 'number', valor = 1)
pesca_numero_ingreso = campos(id_ = 'pesca_numero_ingreso', label = 'Pesca', ayuda = 'Número de peces',
                               tipo = 'number', valor = None)
dates_in = ['fecha_ingreso', 'fecha_siembra_ingreso',]
ids_ingreso = ['gerente_ingreso', 'cliente_ingreso', 'granja_ingreso', 
               'lote_nuevo', 'seg_alimentacion', 'lote_ingreso', 'especie_ingreso', 'peso_siembra_ingreso',
               'talla_ingreso', 'numero_inicial_peces_ingreso', 'estanque_ingreso',
               'tipo_estanque_ingreso', 'area_m2_ingreso', 'vol_m3_ingreso',
               'aireacion_ingreso', 'tipo_aireador_ingreso', 'etapa_cultivo_ingreso', 'dias_ultima_fecha', 
               'alimento_ultima_fecha', 'marca_alimento', 'n_fuentes_alimento',
               'seg_crecimiento', 'real_ingreso', 'longitud_crecimiento', 'mortalidad', 'mortalidad_ingreso', 
               'peso_mortalidad_ingreso', 'translado', 'translado_ingreso',
               'Pesca', 'numero_pesca_ingreso', 'visceras_pesca'
               ]
ids_tabla_ingreso = ['tabla_ingreso_alimento', 'tabla_ingreso_translado', 'tabla_ingreso_pesca']
##campos creacion de clientes
nit_cliente_ng = campos(id_ = 'nit_cliente_ng', label = 'NIT DEL CLIENTE', ayuda = '-', tipo = 'number',
                     xl = 3, lg = 4, md = 6, sm = 6, xs = 6, valor = None)
telefono_cliente = campos(id_ = 'telefono_cliente', label = 'TELÉFONO CONTACTO', ayuda = '-', tipo = 'text',
                          xl = 3, lg = 4, md = 6, sm = 6, xs = 6)
correo_cliente = campos(id_ = 'correo_cliente', label = 'CORREO ELECTRÓNICO', ayuda = '-', tipo = 'text',
                          xl = 3, lg = 4, md = 6, sm = 6, xs = 6)
nombre_cliente_ng = campos(id_ = 'nombre_cliente_ng', label = 'NOMBRE DEL CLIENTE', ayuda = '-', tipo = 'text',
                        xl = 3, lg = 4, md = 6, sm = 6, xs = 6)
usuario_cliente_ng = campos(id_ = 'usuario_cliente_ng', label = 'NOMBRE DE USUARIO', 
                         ayuda = 'Use minúsculas, no use espacios.', tipo = 'text',
                         xl = 3, lg = 4, md = 6, sm = 6, xs = 6)
pw_cliente_ng = campos(id_ = 'pw_cliente_ng', label = 'CONTRASEÑA DE INGRESO', plh = '******',
                    ayuda = 'Recuerde que debe contar con al menos 8 caracteres', tipo = 'pw',
                    xl = 3, lg = 2, md = 6, sm = 6, xs = 6)

ids_crear_cliente_ng = ['gerente_cliente', 'nit_cliente_ng', 'nombre_cliente_ng', 'usuario_cliente_ng', 'pw_cliente_ng', 'telefono_cliente', 'correo_cliente']

## campos creacion de gerentes
plantas_g = ['FUNZA', 'COTA', 'PALERMO', 'VILLAVICENCIO', 'IBAGUÉ', 'BARRANQUILLA', 'GIRÓN', 'GIRARDOTA', 'PALMIRA', 'PEREIRA']
documento_gerente = campos(id_ = 'documento_gerente', label = 'DOCUMENTO DE IDENTIDAD', ayuda = '-', tipo = 'number',
                           xl = 3, lg = 4, md = 6, sm = 6, xs = 6, valor = None)
nombre_gerente = campos(id_ = 'nombre_gerente', label = 'NOMBRE DEL GERENTE', ayuda = 'Nombre y apellido', tipo = 'text',
                        xl = 4, lg = 5, md = 8, sm = 10, xs = 10)
pais_gerente = campos(id_ = 'pais_gerente', label = 'PAIS', ayuda = '-', tipo = 'seleccion',
                        valor = [{'label': i, 'value': i} for i in ['COLOMBIA', 'ECUADOR', 'PANAMÁ']],
                        xl = 3, lg = 4, md = 6, sm = 6, xs = 6, vl = None)
planta_gerente = campos(id_ = 'planta_gerente', label = 'PLANTA', ayuda = '-', tipo = 'seleccion',
                        xl = 3, lg = 4, md = 4, sm = 10, xs = 10, valor = [{'label': i, 'value': i} for i in plantas_g],
                        vl = None)

telefono_gerente = campos(id_ = 'telefono_gerente', label = 'TELÉFONO CONTACTO', ayuda = '-', tipo = 'text',
                          xl = 3, lg = 4, md = 6, sm = 6, xs = 6, vl = None)
correo_gerente = campos(id_ = 'correo_gerente', label = 'CORREO ELECTRÓNICO', ayuda = '-', tipo = 'text',
                          xl = 3, lg = 4, md = 6, sm = 6, xs = 6, vl = None)

usuario_gerente = campos(id_ = 'usuario_gerente', label = 'NOMBRE DE USUARIO', 
                         ayuda = 'Use minúsculas, no use espacios.', tipo = 'text',
                         xl = 3, lg = 4, md = 6, sm = 6, xs = 6)
pw_gerente = campos(id_ = 'pw_gerente', label = 'CONTRASEÑA DE INGRESO', plh = '******',
                    ayuda = 'Recuerde que debe contar con al menos 8 caracteres', tipo = 'pw',
                    xl = 3, lg = 2, md = 6, sm = 6, xs = 6)
ids_crear_gerente = ['documento_gerente', 'nombre_gerente', 'pais_gerente', 'planta_gerente', 'telefono_gerente', 'correo_gerente', 'usuario_gerente', 'pw_gerente']



## campos creacion de especialistas
plantas_g = ['FUNZA', 'COTA', 'PALERMO', 'VILLAVICENCIO', 'IBAGUÉ', 'BARRANQUILLA', 'GIRÓN', 'GIRARDOTA', 'PALMIRA', 'PEREIRA']
documento_especialista = campos(id_ = 'documento_especialista', label = 'DOCUMENTO DE IDENTIDAD', ayuda = '-', tipo = 'number',
                           xl = 3, lg = 4, md = 6, sm = 6, xs = 6, valor = None)
nombre_especialista = campos(id_ = 'nombre_especialista', label = 'NOMBRE DEL ESPECIALISTA', ayuda = 'Nombre y apellido', tipo = 'text',
                        xl = 4, lg = 5, md = 8, sm = 10, xs = 10)
pais_especialista = campos(id_ = 'pais_especialista', label = 'PAIS', ayuda = '-', tipo = 'seleccion',
                        valor = [{'label': i, 'value': i} for i in ['COLOMBIA', 'ECUADOR', 'PANAMÁ']],
                        xl = 3, lg = 4, md = 6, sm = 6, xs = 6, vl = None)
planta_especialista = campos(id_ = 'planta_especialista', label = 'PLANTA', ayuda = '-', tipo = 'seleccion',
                        xl = 3, lg = 4, md = 4, sm = 10, xs = 10, valor = [{'label': i, 'value': i} for i in plantas_g],
                        vl = None)

telefono_especialista = campos(id_ = 'telefono_especialista', label = 'TELÉFONO CONTACTO', ayuda = '-', tipo = 'text',
                          xl = 3, lg = 4, md = 6, sm = 6, xs = 6, vl = None)
correo_especialista = campos(id_ = 'correo_especialista', label = 'CORREO ELECTRÓNICO', ayuda = '-', tipo = 'text',
                          xl = 3, lg = 4, md = 6, sm = 6, xs = 6, vl = None)

usuario_especialista = campos(id_ = 'usuario_especialista', label = 'NOMBRE DE USUARIO', 
                         ayuda = 'Use minúsculas, no use espacios.', tipo = 'text',
                         xl = 3, lg = 4, md = 6, sm = 6, xs = 6)
pw_especialista = campos(id_ = 'pw_especialista', label = 'CONTRASEÑA DE INGRESO', plh = '******',
                    ayuda = 'Recuerde que debe contar con al menos 8 caracteres', tipo = 'pw',
                    xl = 3, lg = 2, md = 6, sm = 6, xs = 6)
ids_crear_especialista = ['documento_especialista', 'nombre_especialista', 'pais_especialista', 'planta_especialista', 'telefono_especialista', 'correo_especialista', 'usuario_especialista', 'pw_especialista']


# campos crear granja no cliente
ids_granjas_nc = ['gerente_nc', 'nit_clientes_nc', 'numero_granjas_nc']
ids_up_nc = ['gerente_nc_up', 'nit_clientes_nc_up', 'granja_up_nc', 'numero_up']


# trazabilidad
acciones_trz_admin = ['Inicio de sesión', 'Validar seguimiento estanque', 'Enviar seguimiento estanque', 
                         'Consultar Excel seguimiento estanques', 'Descargar Excel seguimiento estanques',
                         'Consultar Excel inventario estanques', 'Descargar Excel inventario estanques',
                         'Consultar Excel granjas registradas', 'Descargar Excel granjas registradas',
                        'Consultar Excel unidades productivas registradas', 'Descargar Excel unidades productivas registradas',
                        'Generar reporte seguimiento estanque', 'Descargar reporte seguimiento estanque',
                        'Crear gerente', 'Consultar Excel gerentes registrados', 'Descargar Excel gerentes registrados',
                        'Crear especialista', 'Consultar Excel especialistas registrados', 'Descargar Excel especialistas registrados', 
                        'Crear cliente', 'Consultar Excel clientes registrados', 'Descargar Excel clientes registrados', 
                        'Crear granja', 'Consultar Excel granjas registradas', 'Descargar Excel granjas registradas',
                        'Crear unidad productiva', 'Consultar Excel unidades productivas registradas', 'Descargar Excel unidades productivas registradas',
                        'Cambio de contraseña']

acciones_trz_cliente = ['Inicio de sesión', 'Validar seguimiento estanque', 'Enviar seguimiento estanque', 
                         'Consultar Excel seguimiento estanques', 'Descargar Excel seguimiento estanques',
                         'Consultar Excel inventario estanques', 'Descargar Excel inventario estanques',
                         'Consultar Excel granjas registradas', 'Descargar Excel granjas registradas',
                        'Consultar Excel unidades productivas registradas', 'Descargar Excel unidades productivas registradas',
                        'Generar reporte seguimiento estanque', 'Descargar reporte seguimiento estanque', 
                        'Crear granja', 'Consultar Excel granjas registradas', 'Descargar Excel granjas registradas',
                        'Crear unidad productiva', 'Consultar Excel unidades productivas registradas', 'Descargar Excel unidades productivas registradas',
                        'Cambio de contraseña']
#acciones_trazabilidad.sort()

# trazabilidad
# tipo_usuario = campos(id_ = 'tipo_usuario', label = 'TIPO USUARIO', tipo = 'seleccion_m',
#                       valor = [{'label': i, 'value': i} for i in ['Gerente', 'Especialista',  'Cliente', 'Administrador']],
#                       ayuda = '-', xl = 4, lg = 6, md = 8, sm = 12, xs = 12)
# accion_usuario = campos(id_ = 'accion_usuario', label = 'ACCIÓN USUARIO', tipo = 'seleccion_m',
#                       valor = [{'label': i, 'value': i} for i in acciones_trz_admin],
#                       ayuda = '-', xl = 5, lg = 7, md = 10, sm = 12, xs = 12)


# accion_usuario_cli = campos(id_ = 'accion_usuario', label = 'ACCIÓN USUARIO', tipo = 'seleccion_m',
#                       valor = [{'label': i, 'value': i} for i in acciones_trz_cliente],
#                       ayuda = '-', xl = 5, lg = 7, md = 10, sm = 12, xs = 12)
