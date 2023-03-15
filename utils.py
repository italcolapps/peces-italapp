from tkinter import N
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import os
import pandas as pd
from numpy import insert, nan, inf
from datetime import datetime
import dash_table
from dash_extensions.snippets import send_file
from dash import no_update
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import tempfile
import re
from numpy import nan, log
# local imports
from Datos.db import get_data
from Datos.insert_dataframe import insert_dataframe
from logo import logo_reporte_encoded
from Tablas import render_table



def reporte_resumen_uso():
    try:
        sql = '''SELECT gerentes.documento_identidad, gerentes.nombre_gerente, gerentes.planta, gerentes.pais, gerentes.especialista, gerentes.fecha, clientes.nit, granjas.id_granja, unidades_productivas.id_estanque, lotes.id_lote, lotes.cerrado FROM gerentes LEFT JOIN clientes ON gerentes.documento_identidad = clientes.gerente_zona LEFT JOIN granjas ON gerentes.documento_identidad = granjas.gerente_zona LEFT JOIN unidades_productivas ON gerentes.documento_identidad = unidades_productivas.gerente_zona LEFT JOIN lotes ON clientes.nit = lotes.nit_cliente'''
        sql_registros = '''SELECT gerente_zona, nit_cliente FROM seguimiento_estanques'''
        sql_ultimo_ingreso = '''SELECT doc_id, MAX(fecha) FROM AppPeces.trazabilidad WHERE tipo_usuario IN ('especialista', 'gerente', 'administrador') AND accion = 'Inicio de sesión' GROUP BY doc_id;'''
        data = get_data(sql)
        data_registros = get_data(sql_registros)
        data_ultimo_ingreso = get_data(sql_ultimo_ingreso)
    except Exception as e:
        print(e)
        return None
    
    if data.empty:
        return 'Consulta sin datos'
    
    if not data_registros.empty:
        data_registros = data_registros.groupby(by = ['gerente_zona'], as_index = False).count()

        
    data.especialista.replace({0: 'Gerente', 1: 'Especialista'}, inplace = True)
    data = data.groupby(by = ['documento_identidad', 'nombre_gerente', 'planta', 'pais', 'especialista', 'fecha'], as_index = False).nunique()
    data.sort_values(by = 'nombre_gerente', inplace = True)

    data = data.merge(data_registros, left_on = 'documento_identidad', right_on = 'gerente_zona', how = 'left').drop(columns = 'gerente_zona')
    data.rename(columns = {'nit_cliente': 'registros'}, inplace = True)
    data.registros.fillna(value = 0, inplace = True)
    
    if not data_ultimo_ingreso.empty:
        data_ultimo_ingreso.rename(columns = {'MAX(fecha)': 'fecha'}, inplace = True)
        data = data.merge(data_ultimo_ingreso, left_on = 'documento_identidad', right_on =  'doc_id', how = 'left').drop(columns = 'doc_id')
        data.fecha_y.fillna(value = 'SIN REGISTRO', inplace = True)
    data = data.loc[~data.documento_identidad.isin([111111, 123456789])]
    data.columns = ['Documento', 'Nombre', 'Planta', 'Pais',
                    'Tipo', 'Fecha registro', 'Clientes registrados', 'Granjas registradas', 'Estanques registrados', 'Lotes registrados',
                    'Lotes cerrados', '# registros seguimiento', 'Ultimo ingreso app']
    return data
        

def ss_report_1(data, cliente, creador, granja, año, lote): #, linea, sexo, edad, comparacion):
    especies_ref = {'MR': 'TILAPIA ROJA',
            'TN': 'TILAPIA NILOTICA',
            'TR': 'TRUCHA',
            'CH': 'CACHAMA',
            'BB': 'BAGRE BASSA',
            'CV': 'CAMARÓN VANNA'}
    resumen = data[(data['nit_cliente'].isin([int(cliente)])) &
                   (data['id_lote'].isin([int(i) for i in lote]))].copy()[['id', 'fecha', 
                   'nit_cliente', 'cliente', 'id_granja', 'granja', 'id_lote', 'lote', 
                   'año', 'semana_año', 'departamento_provincia', 'municipio', 'fecha_siembra', 
                   'tipo_estanque', 'especie_ingreso', 'saldo_peces', 'dias_cultivo', 'biomasa_inicial_kg', 
                   'mortalidad_%', 'factor_condicion_k', 'consumo_total_alimento', 'biomasa_final',
                   'densidad_kg_m2', 'biomasa_neta', 'fca',  'sgr', 'gpd', 'numero_lotes_año',
                   'toneladas_ha_año', 'costo_punto_conversion', 'peso_promedio', 'fecha_final_cre']]
    resumen = resumen.sort_values(by = ['id_lote', 'fecha', 'id'])

    dias_cultivo = []
    biomasa_inicial_kg = []
    mortalidad = []
    factor_condicion_k = []
    consumo_total_alimento = []
    biomasa_final = []
    densidad_kg_m2 = []
    biomasa_neta = []
    fca = []
    sgr = []
    gpd = []
    numero_lotes_año = []
    toneladas_ha_año = []
    costo_punto_conversion = []

    tablas_resumen = list()
    graficos_resumen = list() 


    resumen['consumo_total_alimento_pez'] = resumen['consumo_total_alimento']/resumen['saldo_peces']
    resumen['consumo_total_alimento_pez'].replace(inf, nan, inplace = True)
    #resumen.to_excel('text.xlsx', index = False)
    resumen = resumen.round(2)

    try:
        lote_sql = '('
        for i in lote:
            lote_sql = lote_sql + str(i)
            if i == lote[-1]:
                lote_sql = lote_sql + ')'
            else:
                lote_sql = lote_sql + ','
        sql = f'SELECT fecha_final, kg_real FROM alimento WHERE id_lote IN {lote_sql}'
        alimento = get_data(sql)
        if not alimento.empty:
            alimento = alimento.groupby(by = 'fecha_final', as_index = False).sum()
    except Exception as e:
        alimento = pd.DataFrame({'fecha_final': [],
                                 'kg_real': []})
        print('ALIMENTO LOTE REPORTE', e)


    fig_1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig_1.add_trace(
        go.Scatter(x = resumen.fecha_final_cre, y = resumen.peso_promedio,
                   
                   #text = resumen.peso_promedio, textposition = 'top left',
                   mode = 'lines+markers', name = 'Peso'), secondary_y=False,
    )
    fig_1.add_trace(
        go.Scatter(x = alimento.fecha_final, y = alimento.kg_real,
                   #text = alimento.kg_real, textposition = 'top right',
                   mode = 'lines+markers', name = 'Alimento'), secondary_y=True,
        )
    fig_1.layout.xaxis.title = "Tiempo"
    fig_1.layout.yaxis.title = "Peso (gr)"
    fig_1.layout.yaxis2.title = "Alimento (kg)"
    fig_1.update_layout(template = 'plotly_white',
                        legend=dict(orientation="h", xanchor = 'center', x = 1/2),
                        height=600,
                        width = 800,
                        font = {'size': 14},
                        title = 'Alimentación')

    graficos_resumen.append(
        dcc.Graph(
            figure = fig_1
            )
        )

    for lt in resumen.id_lote.unique():
        dt = resumen.loc[resumen.id_lote == lt]
        dias_cultivo.append(dt['dias_cultivo'].values[-1])
        biomasa_inicial_kg.append(dt['biomasa_inicial_kg'].values[-1])
        mortalidad.append(dt['mortalidad_%'].values[-1])
        factor_condicion_k.append(dt['factor_condicion_k'].values[-1])
        consumo_total_alimento.append(dt['consumo_total_alimento_pez'].sum(skipna = True))
        biomasa_final.append(dt['biomasa_final'].values[-1])
        densidad_kg_m2.append(dt['densidad_kg_m2'].values[-1])
        biomasa_neta.append(dt['biomasa_neta'].values[-1])
        fca.append(dt['fca'].values[-1])
        sgr.append(dt['sgr'].values[-1])
        gpd.append(dt['gpd'].values[-1])
        numero_lotes_año.append(dt['numero_lotes_año'].values[-1])
        toneladas_ha_año.append(dt['toneladas_ha_año'].values[-1])
        costo_punto_conversion.append(dt['costo_punto_conversion'].values[-1])
        

    data_r_t = pd.DataFrame({'Días de cultivo': dias_cultivo,
                            'Biomasa inicial (Kg)': biomasa_inicial_kg,
                            'Mortalidad (%)': mortalidad,
                            'Factor de condición (K)': factor_condicion_k,
                            'Consumo Total Alimento x pez (Kg)': consumo_total_alimento,
                            'Biomasa final': biomasa_final,
                            'Densidad (Kg/m²)': densidad_kg_m2,
                            'Biomasa Neta': biomasa_neta,
                            'FCA (Conversión)': fca,
                            '%SGR (Tasa especifica de crecimiento)': sgr,
                            'GPD (gramos/pez/dia)': gpd,
                            'Número de Lotes / año': numero_lotes_año,
                            'Toneladas Hectarea / año': toneladas_ha_año,
                            'Costo punto de conversión (centésima)/pez': costo_punto_conversion})
    #data_r_t.to_excel('TEST.xlsx', index = False)
    data_r_col = data_r_t.columns
    data_r_t = data_r_t.transpose()
    data_r_t['Variable'] = data_r_col
    lote_name = list(resumen.lote.unique()) + ['Variable/Lote']
    data_r_t.columns = lote_name
    #order_columns = list(data_r_t.columns)
    data_r_t = data_r_t[lote_name[::-1]]
    #data_r_t.rename({0: 'Valor'})

    # creando tablas de resumen por edad
    tablas_resumen.append(
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        render_table(data_r_t.round(2))
                        ])
            ]),
            ])
        ])
    )

    return [
        # imagen
        dbc.Row([
            dbc.Col([
                html.Center(children = 
                    html.Img(src=f'data:image/png;base64,{logo_reporte_encoded.decode()}',
                                style={'max-width': '85%', 'height': 'auto'})
                )
            ], xl = 12, lg = 12, md = 12, sm = 12, xs = 12)
        ]),
        html.Br(),
        # titulo
        dbc.Row([
            dbc.Col([
                html.Center(children = 
                    html.H5('INFORME PROCESO PRODUCTIVO ACUÍCOLA')
                )
            ], xl = 12, lg = 12, md = 12, sm = 12, xs = 12, align = 'center')
        ]),
        html.Br(),
        # subtitulo informacion general
        dbc.Row([
            dbc.Col([
                html.H6('INFORMACIÓN GENERAL'),
            ])
        ]),
        # tabla resumen 1
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(
                        figure = go.Figure(data = [
                            go.Table(header = dict(values = ['Fecha Reporte', 'Hora Reporte', 'Nit', 'Cliente', 'Granja'],align = 'center'),
                            cells = dict(values = [[datetime.today().date()],
                                                   [datetime.now().time().strftime('%H:%M:%S')],
                                                [resumen['nit_cliente'].unique()[0]], 
                                                [resumen['cliente'].unique()[0]], 
                                                [resumen[resumen['id_granja'].isin(granja)]['granja'].unique()]],
                                align = 'center',
                                height=35
                                ))
                        ],
                    layout = go.Layout(margin = dict(t = 0, b = 0, l = 0, r = 0), height = 60)
                    )
                    ),
                ])
            ])
        ]),
        html.Br(),
        # tabla resumen 2
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(
                        figure = go.Figure(data = [
                            go.Table(header = dict(values = ['Departamento', 'Municipio', 'Año', 'Semana Año'],align = 'center'),
                            cells = dict(values = [[resumen[resumen['año'].isin(año)]['departamento_provincia'].unique()],
                                                   [resumen[resumen['año'].isin(año)]['municipio'].unique()],
                                                   año,
                                                   [resumen[resumen['año'].isin(año)]['semana_año'].unique()]],
                                align = 'center',
                                height=35
                                ))
                        ],
                    layout = go.Layout(margin = dict(t = 0, b = 0, l = 0, r = 0), height = 60)
                    )
                    ),
                ])
            ])
        ]),
        html.Br(),
        # tabla resumen 3
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(
                        figure = go.Figure(data = [
                            go.Table(header = dict(values = ['Lote', 'Tipo Estanque', 'Especie', 'Reporte generado por:'],align = 'center'),
                            cells = dict(values = [[[resumen[resumen['id_lote'].isin(lote)]['lote'].unique()]],
                                                   [[resumen[resumen['id_lote'].isin(lote)]['tipo_estanque'].unique()]],
                                                   [especies_ref.get(i, None) for i in resumen[resumen['id_lote'].isin(lote)]['especie_ingreso'].unique()],
                                                   [creador]],
                                align = 'center',
                                height=35
                                ))
                        ],
                    layout = go.Layout(margin = dict(t = 0, b = 0, l = 0, r = 0), height = 60)
                    )
                    ),
                ])
            ])
        ]),

        html.Br(),
        # subtitulo
        dbc.Row([
            dbc.Col([
                html.H6('VARIABLES DE SEGUIMIENTO ÚLTIMO MUESTREO'),
            ])
        ]),
        html.Br(),
        # tablas resumen
        html.Div(tablas_resumen),

        html.Br(),
        dbc.Row(
            dbc.Col(
                html.H6('GRAFICOS')
            ),
        ),
        html.Br(),
        html.Div(graficos_resumen),
        html.Br(),
    ]


def lq_report_1(data, cliente, creador, granja, año, mes, comparacion):
    #edad.sort()
    #data['edad_sacrificio_ref_dias'] = data['edad_sacrificio_ref_dias'].astype(int)
    resumen = data[(data['nit_cliente'].isin([int(cliente)])) &
                   (data['año'].isin([int(i) for i in año])) &
                   (data['mes'].isin([int(i) for i in mes]))].copy()[['nit_cliente', 'cliente', 'tipo_cliente', 'id_granja', 'granja', 
                           'id_lote', 'lote', 'año', 'linea', 'sexo', 'marca_alimento', 
                           'planta_alimento', 'edad_sacrificio_dias', 'edad_sacrificio_ref_dias',
                            'peso_promedio_ave_kg', 'mortalidad_total_%', 'mortalidad_total_ref_%',
                            'conversion_alimenticia', 'conversion_alimenticia_ref',
                            'eficiencia_americana', 'eficiencia_americana_ref', 'eficiencia_europea',
                            'eficiencia_europea_ref', 'ip', 'ip_ref']]
    # data resumen para graficos
    resumen_granja = data[(data['nit_cliente'].isin([int(cliente)])) &
                          (data['año'].isin([int(i) for i in año])) &
                          (data['mes'].isin(mes))].copy()[['año', 'id_lote', 'lote', 'id_granja', 'granja', 
                                                           'mortalidad_total_%', 'mortalidad_total_ref_%',
                                                           'conversion_alimenticia', 'conversion_alimenticia_ref',
                                                           'ip', 'ip_ref', 'eficiencia_europea', 'eficiencia_europea_ref']].groupby(['año', 'id_granja', 'granja', 'id_lote', 'lote'], as_index = False).mean()
    resumen_granja.sort_values(by = ['año', 'granja','lote'], inplace = True)
    resumen_granja.reset_index(drop = True, inplace = True)
    resumen_granja = resumen_granja.round(2)

    # data resumen con edad
    resumen_granja_ed = data[(data['nit_cliente'].isin([int(cliente)])) &
                          (data['año'].isin([int(i) for i in año])) &
                          (data['mes'].isin(mes))].copy()[['año', 'id_lote', 'lote', 'id_granja', 'granja', 
                                                           'edad_sacrificio_dias', 'edad_sacrificio_ref_dias', 'peso_promedio_ave_kg']]
    
    resumen_granja_ed = resumen_granja_ed.groupby(['año', 'id_granja', 'granja', 'id_lote', 'lote'], as_index = False).mean()
    resumen_granja_ed.sort_values(by = ['año', 'granja','lote'], inplace = True)
    resumen_granja_ed.reset_index(drop = True, inplace = True)
    resumen_granja_ed = resumen_granja_ed.round(2)
    label_meses = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                   5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                   9: 'Septiembre', 10: 'Ocutubre', 11: 'Noviembre',
                   12: 'Diciembre'}
    meses_list = [label_meses[int(i)] for i in mes]
    #print(resumen_granja)
    if comparacion == '25% MEJORES CLIENTES ITALCOL':
        depto = data.loc[data['nit_cliente'].isin([int(cliente)]), 'departamento_provincia'].unique()
        data_ref = data[(data['año'].isin([int(i) for i in año])) &
                        (data['marca_alimento'] == 'ITALCOL') &
                        (data['departamento_provincia'].isin(depto))].copy()[['año', 'mortalidad_total_%', 'mortalidad_total_ref_%',
                                                                              'conversion_alimenticia', 'conversion_alimenticia_ref',
                                                                              'ip', 'ip_ref', 'eficiencia_europea', 'eficiencia_europea_ref']]
        for year in data_ref['año']:
            data_ref_año = data_ref.loc[data_ref['año'] == year]
            
            quantiles = data_ref_año.quantile([0.25, 0.75])
            

            resumen_granja.loc[resumen_granja['año'] == year, 'mortalidad_total_ref_%'] = [data_ref.loc[(data_ref['mortalidad_total_%'] < quantiles.loc[0.25]['mortalidad_total_%']) &
                                                                                           (data_ref['año'] == year), 'mortalidad_total_%'].mean()]*resumen_granja.shape[0]

            resumen_granja.loc[resumen_granja['año'] == year, 'conversion_alimenticia_ref'] = [data_ref.loc[(data_ref['conversion_alimenticia'] < quantiles.loc[0.25]['conversion_alimenticia']) &
                                                                                           (data_ref['año'] == year), 'conversion_alimenticia'].mean()]*resumen_granja.shape[0]

            resumen_granja.loc[resumen_granja['año'] == year, 'ip_ref'] = [data_ref.loc[(data_ref['ip'] < quantiles.loc[0.25]['ip']) &
                                                                                           (data_ref['año'] == year), 'ip'].mean()]*resumen_granja.shape[0]

            resumen_granja.loc[resumen_granja['año'] == year, 'eficiencia_europea_ref'] = [data_ref.loc[(data_ref['eficiencia_europea'] < quantiles.loc[0.25]['eficiencia_europea']) &
                                                                                                       (data_ref['año'] == year), 'eficiencia_europea'].mean()]*resumen_granja.shape[0]
    # grafico edad y peso promedio
    grafico_1 = make_subplots(specs=[[{'secondary_y': True}]])
    grafico_1.update_layout(barmode = 'group',
                    legend = {'orientation': 'h',
                                'xanchor': 'center', 'x': 1/2,
                                'y': -0.2},
                    template='plotly_white',
                    title_text='EDAD Y PESO',
                    xaxis_title = 'Granja',
                    yaxis_title = 'Edad (días)')
    grafico_1.update_yaxes(title_text="Peso promedio/ave (kg)", secondary_y=True)
    grafico_1.update_yaxes(range=[0, resumen_granja_ed['edad_sacrificio_dias'].max() + 20], secondary_y=False)
    grafico_1.update_yaxes(range=[0, resumen_granja_ed['peso_promedio_ave_kg'].max() + resumen_granja_ed['peso_promedio_ave_kg'].max()*0.25], secondary_y=True)
    grafico_1.add_trace(
        go.Bar(x = resumen_granja_ed['granja'], y = resumen_granja_ed['edad_sacrificio_dias'], name = 'Edad sacrificio',
            text=resumen_granja_ed['edad_sacrificio_dias'].round(), textposition='outside', marker_color='#4463F1')
    )
    # agregar barra de referencia
    # if comparacion != 'SIN COMPARAR':
    #     grafico_1.add_trace(
    #         go.Bar(x = resumen_granja_ed['granja'], y = resumen_granja_ed['edad_sacrificio_ref_dias'], name = 'Edad sacrificio referencia',
    #             text=resumen_granja_ed['edad_sacrificio_ref_dias'].round(), textposition='outside', marker_color='#ED9B45')
    #     )
    grafico_1.add_trace(
        go.Scatter(x = resumen_granja_ed['granja'], y = resumen_granja_ed['peso_promedio_ave_kg'], name = 'Peso promedio ave kg', mode = 'lines+markers+text',
                marker_size=12, line_width=4, text=resumen_granja_ed['peso_promedio_ave_kg'].round(2), textposition='top right', 
                marker_color='#E8ED4A'),
        secondary_y = True
    )
    # grafico mortalidad
    if comparacion == 'SIN COMPARAR':
        grafico_2 = px.bar(resumen_granja, x = 'mortalidad_total_%', y = 'granja', barmode = 'group', template = 'plotly_white', orientation = 'h', title = 'Mortalidad (%)', 
                        labels = {'mortalidad_total_%': 'Mortalidad %', 'granja': 'Granja'}, text = 'mortalidad_total_%')
        grafico_2.update_yaxes(type='category')
    else:
        grafico_2 = px.bar(resumen_granja, x = ['mortalidad_total_%', 'mortalidad_total_ref_%'], y = 'granja', barmode = 'group', template = 'plotly_white', orientation = 'h', title = 'Mortalidad (%)', 
                        labels = {'granja': 'Granja', 'value': 'Mortalidad (%)', 'mortalidad_total_%': 'Mortalidad'})
        grafico_2.update_xaxes(type='category')
        text_ = [resumen_granja['mortalidad_total_%'], resumen_granja['mortalidad_total_ref_%']]
        legend_text = ['Mortalidad', 'Mortalidad de referencia']
        for i, t in enumerate(text_):
            grafico_2.data[i].text = t
        for idx, name in enumerate(legend_text):
            grafico_2.data[idx].name = name
            grafico_2.data[idx].hovertemplate = name
    
    #grafico conversion alimenticia
    if comparacion == 'SIN COMPARAR':
        grafico_3 = px.bar(resumen_granja, x = 'conversion_alimenticia', y = 'granja', barmode = 'group', template = 'plotly_white', orientation = 'h', title = 'Conversión alimenticia', 
                        labels = {'conversion_alimenticia': 'CA', 'granja': 'Granja'}, text = 'conversion_alimenticia')
        grafico_3.update_yaxes(type='category')
    else:
        grafico_3 = px.bar(resumen_granja, x = ['conversion_alimenticia', 'conversion_alimenticia_ref'], y = 'granja', barmode = 'group', template = 'plotly_white', orientation = 'h', title = 'Conversión alimenticia', 
                        labels = {'granja': 'Granja', 'value': 'CA'})
        grafico_3.update_xaxes(type='category')
        text_ = [resumen_granja['conversion_alimenticia'], resumen_granja['conversion_alimenticia_ref']]
        legend_text = ['CA', 'CA de referencia']
        for i, t in enumerate(text_):
            grafico_3.data[i].text = t
        for idx, name in enumerate(legend_text):
            grafico_3.data[idx].name = name
            grafico_3.data[idx].hovertemplate = name

    # grafico ip
    print(resumen_granja[['ip', 'ip_ref']])
    if comparacion == 'SIN COMPARAR':
        grafico_4 = px.bar(resumen_granja, x = 'ip', y = 'granja', barmode = 'group', template = 'plotly_white', orientation = 'h', title = 'IP', 
                        labels = {'ip': 'IP', 'granja': 'Granja'}, text = 'ip')
        grafico_4.update_yaxes(type='category')
    else:
        grafico_4 = px.bar(resumen_granja, x = ['ip', 'ip_ref'], y = 'granja', barmode = 'group', template = 'plotly_white', orientation = 'h', title = 'IP', 
                labels = {'granja': 'Granja', 'value': 'IP'})
        grafico_4.update_xaxes(type='category')
        text_ = [resumen_granja['ip'], resumen_granja['ip_ref']]
        legend_text = ['IP', 'IP de referencia']
        for i, t in enumerate(text_):
            grafico_4.data[i].text = t
        for idx, name in enumerate(legend_text):
            grafico_4.data[idx].name = name
            grafico_4.data[idx].hovertemplate = name

    # grafico eficiencia_europea
    if comparacion == 'SIN COMPARAR':
        grafico_5 = px.bar(resumen_granja, x = 'eficiencia_europea', y = 'granja', barmode = 'group', template = 'plotly_white', orientation = 'h', 
                        title = 'Eficiencia europea', 
                        labels = {'eficiencia_europea': 'Eficiencia europea', 'granja': 'Granja'}, text = 'eficiencia_europea')
        grafico_5.update_yaxes(type='category')
    else:
        grafico_5 = px.bar(resumen_granja, x = ['eficiencia_europea', 'eficiencia_europea_ref'], y = 'granja', barmode = 'group', template = 'plotly_white', orientation = 'h', title = 'Eficiencia europea', 
                           labels = {'granja': 'Granja', 'value': 'Eficiencia europea'})
        grafico_5.update_xaxes(type='category')
        text_ = [resumen_granja['eficiencia_europea'], resumen_granja['eficiencia_europea_ref']]
        legend_text = ['Eficiencia europea', 'Eficiencia europea de referencia']
        for i, t in enumerate(text_):
            grafico_5.data[i].text = t
        for idx, name in enumerate(legend_text):
            grafico_5.data[idx].name = name
            grafico_5.data[idx].hovertemplate = name
    return [
        # imagen
        dbc.Row([
            dbc.Col([
                html.Center(children = 
                    html.Img(src=f'data:image/png;base64,{logo_reporte_encoded.decode()}',
                                style={'max-width': '60%', 'height': 'auto'})
                )
            ], xl = 12, lg = 12, md = 12, sm = 12, xs = 12)
        ]),
        html.Br(),
        # titulo
        dbc.Row([
            dbc.Col([
                html.Center(children = 
                    html.H5('REPORTE LIQUIDACIONES')
                )
            ], xl = 12, lg = 12, md = 12, sm = 12, xs = 12, align = 'center')
        ]),
        html.Br(),
        # subtitulo informacion general
        dbc.Row([
            dbc.Col([
                html.H6('INFORMACIÓN GENERAL'),
            ])
        ]),
        # tabla resumen 1
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(
                        figure = go.Figure(data = [
                            go.Table(header = dict(values = ['Fecha Reporte', 'Nit', 'Cliente', 'Tipo Cliente', 'Granja'],align = 'center'),
                            cells = dict(values = [[datetime.today().date()],
                                                [resumen['nit_cliente'].unique()[0]], 
                                                [resumen['cliente'].unique()[0]], 
                                                [resumen['tipo_cliente'].unique()[0]], 
                                                [resumen[resumen['id_granja'].isin(granja)]['granja'].unique()]],
                                align = 'center',
                                height=35
                                ))
                        ],
                    layout = go.Layout(margin = dict(t = 0, b = 0, l = 0, r = 0), height = 60)
                    )
                    ),
                ])
            ])
        ]),
        html.Br(),
        # tabla resumen 2
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(
                        figure = go.Figure(data = [
                            go.Table(header = dict(values = ['Año', 'Mes', 'Lote'],align = 'center'),
                            cells = dict(values = [año,
                                                   [meses_list],
                                                   [resumen[resumen['nit_cliente'].isin([int(cliente)])]['lote'].unique()]],
                                align = 'center',
                                height=35
                                ))
                        ],
                    layout = go.Layout(margin = dict(t = 0, b = 0, l = 0, r = 0), height = 60)
                    )
                    ),
                ])
            ])
        ]),
        html.Br(),
        # tabla resumen 3
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(
                        figure = go.Figure(data = [
                            go.Table(header = dict(values = ['Sexo', 'Linea', 'Marca Alimento', 'Planta Alimento'],align = 'center'),
                            cells = dict(values = [[resumen[resumen['nit_cliente'].isin([int(cliente)])]['sexo'].unique()],
                                                   [resumen[resumen['nit_cliente'].isin([int(cliente)])]['linea'].unique()],
                                                   [resumen[resumen['nit_cliente'].isin([int(cliente)])]['marca_alimento'].unique()],
                                                   [resumen[resumen['nit_cliente'].isin([int(cliente)])]['planta_alimento'].unique()]],
                                align = 'center',
                                height=35
                                ))
                        ],
                    layout = go.Layout(margin = dict(t = 0, b = 0, l = 0, r = 0), height = 60)
                    )
                    ),
                ])
            ])
        ]),
        html.Br(),
        # tabla resumen 4
        dbc.Row([
            dbc.Col([
                html.Div([
                    dcc.Graph(
                        figure = go.Figure(data = [
                            go.Table(header = dict(values = ['Edad sacrificio', 'Reporte generado por'],align = 'center'),
                            cells = dict(values = [[[resumen[resumen['nit_cliente'].isin([int(cliente)])]['edad_sacrificio_dias'].unique()]],
                                                   [creador]],
                                align = 'center',
                                height=35
                                ))
                        ],
                    layout = go.Layout(margin = dict(t = 0, b = 0, l = 0, r = 0), height = 60)
                    )
                    ),
                ])
            ])
        ]),
        html.Br(),
        # subtitulo
        dbc.Row(
            dbc.Col(
                html.H6('GRAFICOS')
            ),
        ),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure = grafico_1)
            ])
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure = grafico_2)
            ])
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure = grafico_3)
            ])
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure = grafico_4)
            ])
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure = grafico_5)
            ])
        ]),
        html.Br()
    ]

def downloadExcel(data, archivo):
    if isinstance(data, pd.DataFrame):
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                data.to_excel(os.path.join(tmpdir, archivo), index = False)
                return send_file(os.path.join(tmpdir, archivo))
            except Exception as e:
                print(e)
                return no_update
    else:
        return no_update

def get_granjas(nit):
    data = get_data(f'''SELECT DISTINCT nombre_granja FROM granjas WHERE nit_cliente = '{nit}';''')
    if data.shape[0] == 0:
        return ['-']
    return data['nombre_granja'].values

def titulo(texto, id_, xl = 7, lg = 7, md = 7, sm = 7, xs = 7):
    return dbc.Row(children = [
                dbc.Col([
                    html.H5(texto, id = id_)
                ], xl = xl, lg = lg, md = md, sm = sm, xs = xs)
            ])

def save_file(name, content, nombre, UPLOAD_DIRECTORY):
    """Decode and store a file uploaded with Plotly Dash."""

    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, nombre), "wb") as fp:
        fp.write(base64.decodebytes(data))

def crearTablaIngreso(tabla, filas, content_dropdown = None, visceras = None):
    if tabla is None or filas is None:
        return None
    if isinstance(filas, str) or filas is None or filas < 1:
        return 'Número de granjas no aceptado'
    if tabla == 'granjas':
        head = ['Nº', 'NOMBRE GRANJA', 'DEPTO/PROV', 'MPIO', 'VEREDA', 'ALTITUD msnm', 'LATITUD', 'LONGITUD', 'OBSERVACIONES']
        return dbc.Table([
            html.Thead(html.Tr([html.Th(label) for label in head]))
        ] + [
            html.Tbody([
                html.Tr([html.Td(str(row+1))] + [
                    html.Td(dbc.Input(type = 'text', id = f"{head[col]}_{row}", debounce = True, value = None))
                 for col in range(1, len(head) - 4)] + [
                     html.Td(dbc.Input(value = None, type = 'number', id = f"{head[j]}_{row}"))
                     for j in range(5, 8)] + [html.Td(dbc.Input(value = '-', type = 'text', id = f"{head[8]}_{row}"))]) # Tr
            for row in range(filas)]) # tbody
        ]) # dbc table
    if tabla == 'up':
        head = ['Nº', 'NOMBRE ESTANQUE', 'TIPO SISTEMA', 'ÁREA M2', 'VOLUMEN M3']
        t_up = ['ESTANQUE SEMI-INTENSIVO TRADICIONAL', 'ESTANQUE CON AIREACIÓN', 'BIOFLOC', 'IPRS', 'GEOMENBRANA CON AIREACIÓN', 'RACEWAY CONCRETO', 'RACEWAY TIERRA', 'JAULA']
        t_up.sort()
        return dbc.Table([
            html.Thead(html.Tr([html.Th(label) for label in head]))
        ] + [
            html.Tbody([
                html.Tr([html.Td(str(row+1))] + [html.Td(dbc.Input(type = 'text', id = f"{head[1]}_{row}", debounce = True, value = None))] +  
                [html.Td(dbc.Select(id = f"{head[2]}_{row}", options = [{'label': i, 'value': i} for i in t_up]))]+
                [html.Td(dbc.Input(value = None, type = 'number', id = f"{head[col]}_{row}")) for col in range(3, 5)]) # Tr
            for row in range(filas)]) # tbody
        ]) # dbc table
   
    if tabla == 'ingreso_alimento':
        head = ['Nº', 'TIPO ALIMENTO', 'PRECIO Bx40KG', 'KG REAL (ÚLTIMO PERIODO)', 'OBSERVACIONES']
        if not isinstance(content_dropdown, list):
            tipo_alimento = [{'label': 'Error al cargar contenido', 'value': None}]    
        tipo_alimento = content_dropdown
        return dbc.Table([
            html.Thead(html.Tr([html.Th(label) for label in head]))
        ] + [
            html.Tbody([
                html.Tr([html.Td(str(row+1))] + [
                    html.Td(dbc.Select(id = f"{head[1]}_{row}", options = tipo_alimento))] + [
                    html.Td(dbc.Input(type = 'number', id = f"{head[col]}_{row}", debounce = True, value = None))
                 for col in range(2, 4)] + [
                     html.Td(dbc.Input(value = '-', type = 'text', id = f"{head[4]}_{row}"))]) # Tr
            for row in range(filas)]) # tbody
        ]) # dbc table
    
    if tabla == 'ingreso_translado':
        head = ['Nº', 'FECHA', 'CANTIDAD', 'PESO PROMEDIO PEZ', 'ESTANQUE DESTINO', 'OBSERVACIONES']
        if not isinstance(content_dropdown, list):
            estanques = [{'label': 'Error al cargar contenido', 'value': None}]    
        estanques = content_dropdown
        return dbc.Table([
            html.Thead(html.Tr([html.Th(label) for label in head]))
        ] + [
            html.Tbody([
                html.Tr([html.Td(str(row+1))] + [
                    html.Td(dcc.DatePickerSingle(date = datetime.today().date(), display_format='YYYY/MM/DD', id = f"{head[1]}_{row}"))
                ] + [
                    html.Td(dbc.Input(type = 'number', id = f"{head[col]}_{row}", debounce = True, value = None))
                 for col in range(2, 4)] + [
                    html.Td(dbc.Select(id = f"{head[4]}_{row}", options = estanques))
                 ] + [
                     html.Td(dbc.Input(value = '-', type = 'text', id = f"{head[5]}_{row}"))]) # Tr
            for row in range(filas)])
         ]) # tbody
    
    if tabla == 'ingreso_pesca':
        if not bool(visceras):
            head = ['Nº', 'FECHA', 'CANTIDAD', 'BIOMASA BRUTA', 'VISCERAS (KG)', 'OBSERVACIONES']
        else:
            head = ['Nº', 'FECHA', 'CANTIDAD', 'BIOMASA BRUTA', 'VISCERAS (%)', 'OBSERVACIONES']

        return dbc.Table([
            html.Thead(html.Tr([html.Th(label) for label in head]))
            ] + [
            html.Tbody([
                html.Tr([html.Td(str(row+1))] + [
                    html.Td(dcc.DatePickerSingle(date = datetime.today().date(), display_format='YYYY/MM/DD', id = f"{head[1]}_{row}"))
                ] + [
                    html.Td(dbc.Input(type = 'number', id = f"{head[col]}_{row}", debounce = True, value = None))
                 for col in range(2, 5)] + [
                     html.Td(dbc.Input(value = '-', type = 'text', id = f"{head[4]}_{row}"))]) # Tr
            for row in range(filas)]) # tbody
        ]) # dbc table

def cargarDatosTablaIngreso(tabla, datos, filas):
    if tabla == 'granjas':
        columnas = range(1,9)
        values = {}
        for r in range(filas):
            value = []
            for c in columnas:
                try:
                    if c in [5,6,7]:
                        value.append(datos['props']['children'][1]['props']['children'][r]['props']['children'][c]['props']['children']['props']['value'])
                    else:
                        value.append(datos['props']['children'][1]['props']['children'][r]['props']['children'][c]['props']['children']['props']['value'].upper())
                except Exception as e:
                    print(e)
                    return 'Tabla sin datos'
            values[r] = value
        return values

    if tabla == 'up':
        columnas = range(1,5)
        values = {}
        for r in range(filas):
            value = []
            for c in columnas:
                try:
                    if c == 1:
                        value.append(datos['props']['children'][1]['props']['children'][r]['props']['children'][c]['props']['children']['props']['value'].upper())
                    else:
                        value.append(datos['props']['children'][1]['props']['children'][r]['props']['children'][c]['props']['children']['props']['value'])
                except Exception as e:
                    print(e)
                    return 'Tabla sin datos'
            values[r] = value
        return values

    if tabla == 'ingreso_alimento':
        columnas = range(1,5)
        values = {}
        for r in range(filas):
            value = []
            for c in columnas:
                try:
                    value.append(datos['props']['children'][1]['props']['children'][r]['props']['children'][c]['props']['children']['props']['value'])
                except Exception as e:
                    print(e)
                    return 'Tabla sin datos'
            values[r] = value
        return values

    if tabla == 'ingreso_traslado':
        columnas = range(1,6)
        values = {}
        for r in range(filas):
            value = []
            for c in columnas:
                try:
                    if c == 1:
                        value.append(datos['props']['children'][1]['props']['children'][r]['props']['children'][c]['props']['children']['props']['date'])
                    else:
                        value.append(datos['props']['children'][1]['props']['children'][r]['props']['children'][c]['props']['children']['props']['value'])
                except Exception as e:
                    print(e)
                    return 'Tabla sin datos'
            values[r] = value
        return values

    if tabla == 'ingreso_pesca':
        columnas = range(1,6)
        values = {}
        for r in range(filas):
            value = []
            for c in columnas:
                try:
                    if c == 1:
                        value.append(datos['props']['children'][1]['props']['children'][r]['props']['children'][c]['props']['children']['props']['date'])
                    else:
                        value.append(datos['props']['children'][1]['props']['children'][r]['props']['children'][c]['props']['children']['props']['value'])
                except Exception as e:
                    print(e)
                    return 'Tabla sin datos'
            values[r] = value
        return values

 # validar datos de la tabla de ingreso

    # if tabla == 'granjas':
    #     cols = ['NOMBRE GRANJA', 'DEPTO/PROV', 'MPIO', 'VEREDA', 'ALTITUD msnm', 'LATITUD', 'LONGITUD', 'OBSERVACIONES']
    #     for row in data:
    #         count = -1
    #         for column in data[row]:
    #             count += 1
    #             if count in [4,5,6]:
    #                 if isinstance(column, str) or column is None:
    #                     return f"Granja Nº  {row + 1}: {cols[count]} no valido."
    #             else:
    #                 if column is None or column == '':
    #                     return f"Granja Nº  {row + 1}: {cols[count]} no valido."
                            
    #     #return type(data[1][1])
    #     return 'ok'

    # if tabla == 'up':
    #     cols = ['NOMBRE ESTANQUE', 'TIPO SISTEMA', 'AREA M2', 'VOLUMEN M3']
    #     for row in data:
    #         count = -1
    #         for column in data[row]:
    #             count += 1
    #             if count == 0:
    #                 if column == '':
    #                     return f"Unidad Nº  {row + 1}: {cols[count]} no valido."
    #             if count in [2, 3]:
    #                 if isinstance(column, str) or column is None or column <= 0:
    #                     return f"Unidad Nº  {row + 1}: {cols[count]} no valido."
    #             else:
    #                 if column is None:
    #                     return f"Unidad Nº  {row + 1}: {cols[count]} no valido."                         
    #     return 'ok'

    # if tabla == 'ingreso_alimento':
    #     cols = ['TIPO ALIMENTO', 'PRECIO B X 40 KG', 'KG REAL (ÚLTIMO PERIODO)', 'OBSERVACIONES']
    #     for row in data:
    #         count = -1
    #         for column in data[row]:
    #             count += 1
    #             if count == 0:
    #                 if column == '' or column is None:
    #                     return f"Unidad Nº  {row + 1}: {cols[count]} no valido."
    #             if count in [1, 2]:
    #                 if isinstance(column, str) or column is None or column <= 0:
    #                     return f"Unidad Nº  {row + 1}: {cols[count]} no valido."
    #             else:
    #                 if column is None or column == '':
    #                     return f"Unidad Nº  {row + 1}: {cols[count]} no valido."                         
    #     return 'ok'

    # if tabla == 'ingreso_traslado':
    #     cols = ['FECHA', 'CANTIDAD', 'PESO PROMEDIO', 'ESTANQUE DESTINO', 'OBSERVACIONES']
    #     for row in data:
    #         count = -1
    #         for column in data[row]:
    #             count += 1
    #             if count == 0:
    #                 if column == '' or column is None:
    #                     return f"Unidad Nº  {row + 1}: {cols[count]} no valido."
    #             if count in [1, 2]:
    #                 if isinstance(column, str) or column is None or column <= 0:
    #                     return f"Unidad Nº  {row + 1}: {cols[count]} no valido."
    #             else:
    #                 if column is None or column == '':
    #                     return f"Unidad Nº  {row + 1}: {cols[count]} no valido."                         
    #     return 'ok'

    # if tabla == 'ingreso_pesca':
    #     cols = ['FECHA', 'CANTIDAD', 'BIOMASA', 'PESO VISCERAS', 'OBSERVACIONES']
    #     for row in data:
    #         count = -1
    #         for column in data[row]:
    #             count += 1
    #             if count == 0:
    #                 if column == '' or column is None:
    #                     return f"Unidad Nº  {row + 1}: {cols[count]} no valido."
    #             if count in [1, 2]:
    #                 if isinstance(column, str) or column is None or column < 0:
    #                     return f"Unidad Nº  {row + 1}: {cols[count]} no valido."
                
    #             if count == 3:
    #                 continue

    #             else:
    #                 if column is None or column == '':
    #                     return f"Unidad Nº  {row + 1}: {cols[count]} no valido."                         
    #     return 'ok'

    else:
        return 'Tabla no definida'

 # validar datos de la tabla de ingreso

def validarTablaIngreso(data, tabla):
    if tabla == 'granjas':
        cols = ['NOMBRE GRANJA', 'DEPTO/PROV', 'MPIO', 'VEREDA', 'ALTITUD msnm', 'LATITUD', 'LONGITUD', 'OBSERVACIONES']
        for row in data:
            count = -1
            for column in data[row]:
                count += 1
                if count in [4,5,6]:
                    if isinstance(column, str) or column is None:
                        return f"Granja Nº  {row + 1}: {cols[count]} no valido."
                else:
                    if column is None or column == '':
                        return f"Granja Nº  {row + 1}: {cols[count]} no valido."
                            
        #return type(data[1][1])
        return 'ok'

    if tabla == 'up':
        cols = ['NOMBRE ESTANQUE', 'TIPO SISTEMA', 'AREA M2', 'VOLUMEN M3']
        for row in data:
            count = -1
            for column in data[row]:
                count += 1
                if count == 0:
                    if column == '':
                        return f"Unidad Nº  {row + 1}: {cols[count]} no valido."
                if count in [2, 3]:
                    if isinstance(column, str) or column is None or column <= 0:
                        return f"Unidad Nº  {row + 1}: {cols[count]} no valido."
                else:
                    if column is None:
                        return f"Unidad Nº  {row + 1}: {cols[count]} no valido."                         
        return 'ok'

    if tabla == 'ingreso_alimento':
        cols = ['TIPO ALIMENTO', 'PRECIO B X 40 KG', 'KG REAL (ÚLTIMO PERIODO)', 'OBSERVACIONES']
        for row in data:
            count = -1
            for column in data[row]:
                count += 1
                if count == 0:
                    if column == '' or column is None:
                        return f"Unidad Nº  {row + 1}: {cols[count]} no valido."
                if count in [1, 2]:
                    if isinstance(column, str) or column is None or column <= 0:
                        return f"Unidad Nº  {row + 1}: {cols[count]} no valido."
                else:
                    if column is None or column == '':
                        return f"Unidad Nº  {row + 1}: {cols[count]} no valido."                         
        return 'ok'

    if tabla == 'ingreso_traslado':
        cols = ['FECHA', 'CANTIDAD', 'PESO PROMEDIO PEZ', 'ESTANQUE DESTINO', 'OBSERVACIONES']
        for row in data:
            count = -1
            for column in data[row]:
                count += 1
                if count == 0:
                    if column == '' or column is None:
                        return f"Unidad Nº  {row + 1}: {cols[count]} no valido."
                if count in [1, 2]:
                    if isinstance(column, str) or column is None or column <= 0:
                        return f"Unidad Nº  {row + 1}: {cols[count]} no valido."
                else:
                    if column is None or column == '':
                        return f"Unidad Nº  {row + 1}: {cols[count]} no valido."                         
        return 'ok'

    if tabla == 'ingreso_pesca':
        cols = ['FECHA', 'CANTIDAD', 'BIOMASA BRUTA', 'PESO VISCERAS',  'OBSERVACIONES']
        for row in data:
            count = -1
            for column in data[row]:
                count += 1
                if count == 0:
                    if column == '' or column is None:
                        return f"Unidad Nº  {row + 1}: {cols[count]} no valido."
                if count in [1, 2]:
                    if isinstance(column, str) or column is None or column <= 0:
                        return f"Unidad Nº  {row + 1}: {cols[count]} no valido."
                if count == 3:
                    if column is None:
                        continue
                    else:
                        if column <= 0:
                            return f"Unidad Nº  {row + 1}: {cols[count]} no valido."
                        else:
                            continue
                else:
                    if column is None or column == '':
                        return f"Unidad Nº  {row + 1}: {cols[count]} no valido."                         
        return 'ok'

    else:
        return 'Tabla no definida'


def crear_traslado(data, traslados):
    fca = data['fca'].values[0]
    biomasa_inicial = data['biomasa_inicial_kg'].values[0]
    id_lote = data['id_lote'].values[0]
    id_estanque = data['id_estanque'].values[0]

    sql = f'SELECT * FROM alimento WHERE id_lote = {id_lote} AND id_estanque = {id_estanque}'
    try:
        alimento_total = get_data(sql).drop(columns = 'id')

    except Exception as e:
        print('CARGAR ALIMENTO crear traslado', e)
        return 'ERROR AL CARGAR ALIMENTO'

    for e in traslados['estanque_destino'].unique():
        dt = traslados.loc[traslados['estanque_destino'] == e]
        biomasa_traslado = (dt['peso_promedio']*dt['cantidad']/1000).sum()
        alimento = (biomasa_traslado - biomasa_inicial)*fca

        lote_traslado = data[['id_lote', 'lote', 'especie_ingreso', 'linea_genetica', 'peso_siembra', 'talla', 'numero_inicial_peces', 'fecha_siembra', 'id_estanque', 'id_granja', 'nit_cliente']].copy()
        lote_traslado['peso_siembra'] = dt['peso_promedio'].values[0]
        lote_traslado['numero_inicial_peces'] = dt['cantidad'].values[0]
        lote_traslado['fecha_siembra'] = dt['fecha'].values[0]
        lote_traslado['id_estanque'] = dt['estanque_destino'].values[0]
        lote_traslado['cerrado'] = ['No']
        lote_traslado.rename(columns = {'peso_siembra': 'peso_siembra_gr', 
                                        'lote': 'nombre_lote',
                                        'especie_ingreso': 'especie_sembrada',
                                        'talla': 'talla_cm'}, inplace = True)
        try:
            insert_dataframe(lote_traslado, 'lotes')
        except Exception as e:
            print('ERROR AL INGRESAR LOTE, crear_traslado', e)
            return 'ERROR AL INGRESAR LOTE'

        sql = f'SELECT nombre_estanque, tipo_sistema, area_m2, volumen_m3 FROM unidades_productivas WHERE id_estanque = {e}'
        estanque = get_data(sql)

        if alimento_total.empty:
            try:
                data_2 = data.copy()
                data_2['fecha_siembra'] = [dt['fecha'].values[0]]
                data_2['id_estanque'] = [dt['estanque_destino'].values[0]]
                data_2['estanque'] = [estanque['nombre_estanque'].values[0]]
                data_2['tipo_estanque'] = [estanque['tipo_sistema'].values[0]]
                data_2['peso_siembra'] = [dt['peso_promedio'].values[0]]
                data_2['longitud_promedio'] = [None]
                data_2['numero_inicial_peces'] = [dt['cantidad'].values[0]]
                data_2['area_m2'] = [estanque['area_m2'].values[0]]
                data_2['vol_m3'] = [estanque['volumen_m3'].values[0]]
                data_2['tipo_aireador'] = ['NINGUNO']
                data_2['aireacion'] = [None]

                data_2['mortalidad'] = ['No']
                data_2['numero_mortalidad'] = [0]
                data_2['peso_mortalidad'] = [0]
                data_2['saldo_peces'] = [dt['cantidad'].values[0]]
                data_2['biomasa_inicial_kg'] = [biomasa_traslado]
                data_2['mortalidad_%'] = [0]
                
                data_2['consumo_total_alimento'] = [0]
                data_2['biomasa_final'] = [None]
                data_2['densidad_kg_m2'] = [None]
                data_2['biomasa_neta'] = [None]
                data_2['fca'] = [None]
                data_2['gpd'] = [None]
                data_2['numero_lotes_año'] = [None]
                data_2['toneladas_ha_año'] = [None]
                data_2['costo_punto_conversion'] = [None]
                data_2['costo_kg_alimento'] = [None]
                
                insert_dataframe(data_2, 'seguimiento_estanques')

            except Exception as e:
                print('ERROR AL INGRESAR SEGUIMIENTO, crear_traslado', e)
                return 'ERROR AL INGRESAR SEGUIMIENTO'

        else:
            porcentaje = alimento/alimento_total['kg_real'].sum()
            if porcentaje > 1:
                porcentaje = 1
            
            alimento_total_2 = alimento_total.copy()
            alimento_total_2['id_estanque'] = [e]*alimento_total_2.shape[0]
            alimento_total_2['kg_real'] = alimento_total_2['kg_real']*porcentaje

            try:
                insert_dataframe(alimento_total_2, 'alimento')
            except Exception as e:
                print('ERROR AL INGRESAR ALIMENTO, crear_traslado', e)
                return 'ERROR AL INGRESAR ALIMENTO'

            try:
                data_2 = data.copy()
                data_2['fecha_siembra'] = [dt['fecha'].values[0]]
                data_2['id_estanque'] = [dt['estanque_destino'].values[0]]
                data_2['estanque'] = [estanque['nombre_estanque'].values[0]]
                data_2['tipo_estanque'] = [estanque['tipo_sistema'].values[0]]
                data_2['peso_siembra'] = [dt['peso_promedio'].values[0]]
                data_2['longitud_promedio'] = [None]
                data_2['numero_inicial_peces'] = [dt['cantidad'].values[0]]
                data_2['area_m2'] = [estanque['area_m2'].values[0]]
                data_2['vol_m3'] = [estanque['volumen_m3'].values[0]]
                data_2['tipo_aireador'] = ['NINGUNO']
                data_2['aireacion'] = [None]

                data_2['mortalidad'] = ['No']
                data_2['numero_mortalidad'] = [0]
                data_2['peso_mortalidad'] = [0]
                data_2['saldo_peces'] = [dt['cantidad'].values[0]]
                data_2['biomasa_inicial_kg'] = [biomasa_traslado]
                data_2['mortalidad_%'] = [0]
                
                data_2['consumo_total_alimento'] = [alimento_total_2['kg_real'].sum()]
                data_2['biomasa_final'] = [None]
                data_2['densidad_kg_m2'] = [None]
                data_2['biomasa_neta'] = [None]
                data_2['fca'] = [None]
                data_2['gpd'] = [None]
                data_2['numero_lotes_año'] = [None]
                data_2['toneladas_ha_año'] = [None]
                data_2['costo_punto_conversion'] = [None]
                data_2['costo_kg_alimento'] = [None]
                
                insert_dataframe(data_2, 'seguimiento_estanques')

            except Exception as e:
                print('ERROR AL INGRESAR SEGUIMIENTO, crear_traslado', e)
                return 'ERROR AL INGRESAR SEGUIMIENTO'
            
    return 'OK'   

def seguimientoEstanque(gerente, cliente, depto, municipio, nombre_lote, nombre_granja, 
                        nombre_cliente, nombre_gerente, id_lote, fecha_ingreso, fecha_siembra,
                        granja, id_estanque, estanque, tipo_estanque, especie_ingreso, 
                        peso_siembra, talla, numero_inicial_peces, area_m2, vol_m3, tipo_aireador, 
                        real, mortalidad, mortalidad_numero, mortalidad_peso, long, saldo_peces,
                        saldo_peces_anterior, edad_peso, aireacion, fase_cultivo,
                        fecha_inicial_cre, fecha_final_cre, fecha_mort_i, fecha_mort_f, alimento,
                        biomasa_neta, cerrar, biomasa, cantidad, lote_nuevo, traslados_, genetica):

    date = datetime.strptime(fecha_ingreso, '%Y-%m-%d').date()
    data = pd.DataFrame()

    f_siembra = datetime.strptime(fecha_siembra, '%Y-%m-%d').date()
    f_siembra_estanque = datetime.strptime(fecha_siembra, '%Y-%m-%d').date()
    f_actual = datetime.strptime(fecha_ingreso, '%Y-%m-%d').date()

    try:
        sql = f'SELECT id, fecha_siembra FROM seguimiento_estanques WHERE id_lote = {id_lote} ORDER BY id LIMIT 1'
        dt_fecha_siembra = get_data(sql)
        if dt_fecha_siembra.empty:
            pass
        else:
            fecha_siembra = dt_fecha_siembra['fecha_siembra'].values[0]
            f_siembra = fecha_siembra
    except Exception as e:
        print('ERROR FECHA SIEMBRA LOTE', e)

    try:
        if bool(lote_nuevo):
            dias_cultivo_tabla = 0
        else:
            dias_cultivo_tabla = int((f_actual-f_siembra).days)
        try:
            if not fecha_final_cre is None:
                fecha_final_cre = datetime.strptime(fecha_final_cre, '%Y-%m-%d').date()
                dias_cultivo_cal_gpd = int((fecha_final_cre-f_siembra).days)
            else:
                dias_cultivo_cal_gpd = dias_cultivo_tabla
        except Exception as e:
            dias_cultivo_cal_gpd = dias_cultivo_tabla
            print('Dias cultivo calculado:', e)

    except Exception as e:
        print('DIAS CULTIVO TABLA', e)
        dias_cultivo_tabla = nan

    try:
        costo_ali = lambda x: x[0]*x[1]
        sql = f'SELECT precio_b_40_kg, kg_real FROM alimento WHERE id_lote = {id_lote} and id_estanque = {id_estanque}'
        dt_alimento = get_data(sql)
        if dt_alimento.empty:
            consumo_alimento = alimento['kg_real'].sum()
            costo_kg = (alimento['precio_b_40_kg']/40).tolist()
            kg_alimento = alimento['kg_real'].tolist()

            if sum(kg_alimento) == 0:
                costo_kg_alimento = 0
            else:
                costo_kg_alimento = sum(list(map(costo_ali, zip(costo_kg, kg_alimento))))/sum(kg_alimento)
        else:        
            consumo_alimento = dt_alimento.kg_real.sum() + alimento['kg_real'].sum()
            costo_kg = (dt_alimento['precio_b_40_kg']/40).tolist() + (alimento['precio_b_40_kg']/40).tolist()
            kg_alimento = dt_alimento['kg_real'].tolist() + alimento['kg_real'].tolist()


            if sum(kg_alimento) == 0:
                costo_kg_alimento = 0
            else:                
                costo_kg_alimento = sum(list(map(costo_ali, zip(costo_kg, kg_alimento))))/sum(kg_alimento)

    except Exception as e:
        print('Error alimento acumulado seguimiento semanal', e)
        consumo_alimento = None

    try:
        sql = f'''SELECT unidades_productivas.area_m2, pescas.biomasa, pescas.biomasa_neta, pescas.cantidad FROM
                  AppPeces.unidades_productivas INNER JOIN AppPeces.pescas ON
                  unidades_productivas.id_estanque = pescas.id_estanque WHERE
                  pescas.id_lote = {id_lote} AND pescas.id_estanque = {id_estanque};'''
        dt_biomasa = get_data(sql)
        if dt_biomasa.empty:
            ton_ha =  0
            biomasa_cosechada = 0 + biomasa
            cantidad_cosechada = 0 + cantidad
            biomasa_neta_ac = 0 + biomasa_neta
        else:
            ton_ha = (10*dt_biomasa['biomasa'].sum()/dt_biomasa['area_m2'].mean())
            biomasa_cosechada = dt_biomasa['biomasa'].sum() + biomasa
            biomasa_neta_ac = dt_biomasa['biomasa_neta'].sum() + biomasa_neta
            cantidad_cosechada = dt_biomasa['cantidad'].sum() + cantidad
            print(biomasa_neta_ac)

    except Exception as e:
        print('Error toneladas biomasa por ha seguimiento semanal', e)
        ton_ha = None

    try:
        sql = f'SELECT numero_mortalidad FROM seguimiento_estanques WHERE id_lote = {id_lote} AND id_estanque = {id_estanque};'
        mort_ = get_data(sql)
        if mort_.empty:
            mort_ = 0
        else:
            mort_ = mort_['numero_mortalidad'].sum()
    except Exception as e:
        print('SQL MORTALIDAD ANTERIOR', e)

    if real is None and biomasa is not None:
        real = 1000*biomasa/cantidad

    if cerrar == ['Si']:
        mortalidad_numero = mortalidad_numero + saldo_peces
        mortalidad_peso = 0 if mortalidad_peso is None else mortalidad_peso + 0
        saldo_peces = 0
        biomasa_final = biomasa_cosechada  + (traslados_['cantidad']*traslados_['peso_promedio']/1000).sum() # - numero_inicial_peces*peso_siembra/1000
        #biomasa_final = (saldo_peces * real/1000) + (traslados_['cantidad']*traslados_['peso_promedio']/1000).sum() if not real is None else None
    else:
        biomasa_final =  (saldo_peces * real/1000) + (traslados_['cantidad']*traslados_['peso_promedio']/1000).sum() if not real is None else None
    

    if real is not None:
        try:
            sql = f'SELECT id, fecha, peso_promedio FROM seguimiento_estanques WHERE id_lote = {id_lote} AND id_estanque = {id_estanque}'
            peso_anterior = get_data(sql)
            if peso_anterior.empty:
                peso_anterior = None
            else:
                peso_anterior.dropna(inplace = True)
                if peso_anterior.empty:
                    peso_anterior = peso_siembra
                    f_peso_anterior = f_siembra
                else:
                    peso_anterior.reset_index(drop = True, inplace = True)
                    f_peso_anterior = peso_anterior['fecha'].values[-1]
                    #f_peso_anterior = datetime.strptime(f_peso_anterior, '%Y-%m-%d').date()
                    peso_anterior = peso_anterior['peso_promedio'].values[-1]
        except Exception as e:
            print('consultar peso anterior', e)
            peso_anterior = None
    
        try:
            if peso_anterior is not None:
                sgr = 100*(log(real) - log(peso_anterior))/int((f_actual-f_peso_anterior).days)
            else:
                sgr = None
        except Exception as e:
            print('Calculo sgr', e)
            sgr = None
    else:
        sgr = None

    try:
        sql = f'SELECT id, biomasa_inicial_kg FROM seguimiento_estanques WHERE id_lote = {id_lote} ORDER BY id LIMIT 1'
        dt_biomasa = get_data(sql)
        if dt_biomasa.empty:
            biomasa_inicial = peso_siembra*numero_inicial_peces
        else:
            biomasa_inicial = dt_biomasa['biomasa_inicial_kg'].values[0]
    except Exception as e:
        print('BIOMASA INICIAL LOTE', e)
        biomasa_inicial = peso_siembra*numero_inicial_peces

    data['fecha'] = [fecha_ingreso]
    data['año'] = [date.year]
    data['mes'] = [date.month]
    data['semana_año'] = [date.isocalendar()[1]]
    data['gerente_zona'] = [gerente]
    data['nombre_gerente'] = [nombre_gerente]
    data['nit_cliente'] = [cliente]
    data['cliente'] = [nombre_cliente]
    data['departamento_provincia'] = [depto.upper()]
    data['municipio'] = [municipio.upper()]
    data['id_granja'] = [granja]
    data['granja'] = [nombre_granja]
    data['id_lote'] = id_lote
    data['lote'] = [nombre_lote]
    data['fecha_siembra'] = [f_siembra_estanque]
    #data['dias_cultivo'] = [dias_cultivo] ####################### dias a fecha de siembra
    data['edad_por_peso'] = [edad_peso] ############################ edad en tabla de referencia segun el peso de siembra
    data['id_estanque'] = [id_estanque]
    data['estanque'] = [estanque] 
    data['tipo_estanque'] = [tipo_estanque]
    data['especie_ingreso'] = [especie_ingreso]
    data['linea_genetica'] = [genetica]
    data['peso_siembra'] = [peso_siembra]
    data['talla'] = [talla]
    data['numero_inicial_peces'] = [numero_inicial_peces]
    data['area_m2'] = [area_m2]
    data['vol_m3'] = [vol_m3]
    data['tipo_aireador'] = [tipo_aireador]
    data['aireacion'] = [aireacion]
    data['fase_cultivo'] = [fase_cultivo]
    data['fecha_inicial_cre'] = [fecha_inicial_cre]
    data['fecha_final_cre'] = [fecha_final_cre]
    data['peso_promedio'] = [real]
    data['longitud_promedio'] = [long]
    data['mortalidad'] = [mortalidad]
    data['fecha_inicial_mort'] = [fecha_mort_i]
    data['fecha_final_mort'] = [fecha_mort_f]
    data['numero_mortalidad'] = [mortalidad_numero]
    data['peso_mortalidad'] = [mortalidad_peso]
    data['saldo_peces'] = [saldo_peces] #################

    ### CALCULADO

    data['dias_cultivo'] = [dias_cultivo_tabla]
    data['biomasa_inicial_kg'] = [numero_inicial_peces*peso_siembra/1000]
    data['mortalidad_%'] = [round(100*((mort_+mortalidad_numero)/numero_inicial_peces), 2)]
    data['factor_condicion_k'] = [100*real/pow(long, 3)] if (real is not None and long is not None) else [None]
    data['consumo_total_alimento'] = [consumo_alimento]
    data['biomasa_final'] = [biomasa_final]
    if not bool(cerrar):
        data['densidad_kg_m2'] = [(biomasa_final)/vol_m3] if not biomasa_final is None else [None]
    else:
        data['densidad_kg_m2'] = [0]

    if not bool(cerrar):
        data['biomasa_neta'] = [biomasa_neta]
        data['fca'] = [consumo_alimento/(biomasa_final + biomasa_cosechada  - biomasa_inicial)] if not biomasa_final is None else [None]
    else:
        data['biomasa_neta'] = [biomasa_neta_ac]
        biomasa_final = 0
        data['fca'] = [consumo_alimento/(biomasa_final + biomasa_neta_ac - biomasa_inicial)] if not biomasa_final is None else [None]
        #data['fca'] = [consumo_alimento/(biomasa_final  - biomasa_inicial)] if not biomasa_final is None else [None]
    data['sgr'] = [sgr]
    data['gpd'] = [(real-peso_siembra)/dias_cultivo_tabla] if not real is None else [None]
    data['numero_lotes_año'] = [365/dias_cultivo_tabla if dias_cultivo_tabla > 0 else 0]
    data['toneladas_ha_año'] = [ton_ha*(365/dias_cultivo_tabla) if dias_cultivo_tabla > 0 else 0]
    data['costo_punto_conversion'] = [None]
    data['costo_kg_alimento'] = [costo_kg_alimento*data['fca'].values[0] if data['fca'].values[0] is not None else None]

    # data['kg_proy'] = nan#saldo_peces_anterior * referencias(especie = especie_ingreso, referencia = 'CONSUMO (g/d)', edad = edad_peso) * (1000/7) * referencias(referencia = 'ajuste_temp', temp = 0)
    # data['kg_trans'] = nan#[nan] ################

    try:
        costo_kg_carne_a = costo_kg_alimento*data['fca'].values[0]
        costo_kg_carne_b = costo_kg_alimento*(data['fca'].values[0] + 0.1)
        diff = costo_kg_carne_b - costo_kg_carne_a
        costo_punto_conversion = diff/10
        data['costo_punto_conversion'] = [costo_punto_conversion]
    except Exception as e:
        print('Calculo costo_punto_conversion', e)
        costo_punto_conversion = None


    if  bool(cerrar):
        
        data['numero_lotes_año'] = [365/dias_cultivo_tabla]
        data['toneladas_ha_año'] = [10*(biomasa_cosechada/area_m2)*(365/dias_cultivo_tabla)]
        data['costo_kg_alimento'] = [costo_kg_alimento*data['fca'].values[0] if data['fca'].values[0] is not None else None]
    else:
        data['numero_lotes_año'] = [nan]
        data['toneladas_ha_año'] = [nan]
        data['costo_kg_alimento'] = [nan] 

    data = data.round(decimals = 2, )
    data.fillna(value=nan, inplace = True)
    return data

def liquidaciones(fecha, gerente, cliente, depto, municipio, planta, granja,
                  lote, galpon, linea, sexo, marca, aves_encasetadas, aves_muertas,
                  aves_sacrificadas, aves_decomisadas, peso_total, edad, consumo,
                  precio_promedio, divisa, observaciones, nombre_gerente, nombre_cliente,
                  tipo_cliente, nombre_granja, nombre_galpon, id_lote):
    date = datetime.strptime(fecha, '%Y-%m-%d').date()                  
    data = pd.DataFrame()
    data['fecha'] = [fecha]
    data['año'] = [date.year]
    data['mes'] = [date.month]
    data['divisa'] = [divisa]
    data['gerente_zona'] = [gerente]
    data['nombre_gerente'] = [nombre_gerente]
    data['nit_cliente'] = [cliente]
    data['cliente'] = [nombre_cliente]
    data['tipo_cliente'] = [tipo_cliente]
    data['departamento_provincia'] = [depto.upper()]
    data['municipio'] = [municipio.upper()]
    data['planta_alimento'] = [planta]
    data['id_granja'] = [granja]
    data['granja'] = [nombre_granja]
    data['id_lote'] = [id_lote]
    data['lote'] = [lote]
    data['id_galpon'] = [galpon]
    data['galpon'] = [nombre_galpon]
    data['linea'] = [linea]
    data['sexo'] = [sexo]
    data['marca_alimento']  = [marca]
    data['aves_encasetadas'] = [aves_encasetadas]
    data['aves_muertas_granja'] = [aves_muertas]
    data['aves_sacrificadas_o_vendidas'] = [aves_sacrificadas]
    data['aves_decomisadas'] = [aves_decomisadas]
    data['decomisos_%'] = [100*(aves_decomisadas/aves_sacrificadas)]
    data['sobrantes_faltantes'] = [aves_encasetadas - aves_muertas - aves_sacrificadas]
    data['precio_promedio_kg_alimento'] = [precio_promedio]
    data['edad_sacrificio_dias'] = [edad]
    data['edad_sacrificio_ref_dias'] = [referencias(tipo = 'LIQ', sexo = sexo, linea = linea, var = 'EDAD', peso_promedio= (peso_total/aves_sacrificadas))]
    data['consumo_total_alimento_kg'] = [consumo]
    data['peso_total_aves_sacrificadas_kg'] = [peso_total]
    data['conversion_alimenticia'] = [consumo/peso_total]
    data['conversion_alimenticia_ref'] = [referencias(tipo = 'LIQ', sexo = sexo, linea = linea, peso_promedio=(peso_total/aves_sacrificadas), var = 'CONVERSION ALIMENTICIA REFERENCIA')]
    data['peso_promedio_ave_kg'] = [peso_total/aves_sacrificadas]
    data['ganancia_diaria_g_ave_dia'] = [100*(peso_total/aves_sacrificadas)/edad]
    data['mortalidad_total_%'] = [100*(1 - (aves_sacrificadas/aves_encasetadas))]
    data['mortalidad_total_ref_%'] = [referencias(tipo = 'MORT_LIQ', edad = edad)]
    data['costo_alimentacion_kg_pollo_producido'] = [(consumo*precio_promedio)/peso_total]
    data['eficiencia_americana'] = [100*(peso_total/aves_sacrificadas)/data['conversion_alimenticia'].values[0]]
    data['eficiencia_americana_ref'] = [referencias(tipo = 'LIQ', sexo = sexo, linea = linea, peso_promedio=(peso_total/aves_sacrificadas), var = 'EA')]
    data['eficiencia_europea'] = [((100-data['mortalidad_total_%'].values[0]/100)/100)*((data['peso_promedio_ave_kg'].values[0]*1000)*10/(edad*data['conversion_alimenticia'].values[0]))]
    data['eficiencia_europea_ref'] = [referencias(tipo = 'LIQ', sexo = sexo, linea = linea, peso_promedio=(peso_total/aves_sacrificadas), var = 'FEE')]
    data['ip'] = [data['eficiencia_americana'].values[0]/data['conversion_alimenticia'].values[0]]
    data['ip_ref'] = [referencias(tipo = 'LIQ', sexo = sexo, linea = linea, peso_promedio=(peso_total/aves_sacrificadas), var = 'IP')]
    data['observaciones'] = [observaciones]
    data = data.round(decimals = 2, )
    data.fillna(value=nan, inplace = True)
    return data

def referencias(referencia, especie = None, edad=None, peso_siembra = None,  temp = None):
    especies = {'MR': 'TILAPIA ROJA',
                'TN': 'TILAPIA NILOTICA',
                'TR': 'TRUCHA', 
                'CH': 'CACHAMA',
                'BB': 'BAGRE BASSA',
                'CV': 'CAMARÓN VANNA'}

    if referencia is None:
        return None

    if referencia == 'EDAD':
        df = pd.read_csv('Datos/referencias.csv', sep = ';')

        try:
            ref = df[(df['ESPECIE'] == especies.get(especie, None))][[referencia, 'PESO (g)']]
            if ref.empty:
                return None
            ref.reset_index(drop = True, inplace = True)
            ref['diff'] = (ref['PESO (g)'] - peso_siembra).abs()
            value = ref.loc[ref['diff'] == ref['diff'].min()][['EDAD', 'PESO (g)']]

            return value['EDAD'].values[0]

        except Exception as e:
            print(e)
            return None

    if referencia == 'CONSUMO (g/d)':
        df = pd.read_csv('Datos/referencias.csv', sep = ';')

        try:
            ref = df[(df['ESPECIE'] == especies.get(especie, None))][[referencia, 'EDAD']]
            if ref.empty:
                return None
            ref.reset_index(drop = True, inplace = True)
            value = ref.loc[ref['EDAD'] == edad][['EDAD', 'CONSUMO (g/d)']]

            return value['CONSUMO (g/d)'].values[0]

        except Exception as e:
            print(e)
            return None

    if referencia == 'ajuste_temp':
        df = pd.read_csv('Datos/ajuste_alimento_por_temperatura.csv')

        try:
            ref = df[(temp >= df['temp_inferior']) & (temp <= df['temp_superior'])]
            if ref.empty:
                return 1
            ref.reset_index(drop = True, inplace = True)
            value = ref['ofrecimiento_%'].values[0]

            return value

        except Exception as e:
            print(e)
            return None

def dashtable(archivo, tipo = ''):
    if tipo == 'ss':
        types = ['datetime'] + ['numeric']*3 + ['text', 'numeric'] + ['text']*9 + ['numeric', 'text', 'text'] + ['numeric']*25 + ['text']
    if tipo == 'lq':
        types = ['datetime', 'numeric', 'numeric', 'text', 'text', 'numeric'] + ['text']*11 +  ['numeric']*24 + ['text']
    if tipo == 'cp':
        pass
    table = dash_table.DataTable(
        data = archivo.to_dict('records'),
        columns = [{'name': i, 'id': i, 'type': j} for i, j in zip(archivo.columns, types)],
        #fixed_columns = {'headers': True},
        #fixed_rows = {'headers': True},
        #fixed_columns = {'headers': True, 'data': 3},
        filter_action = 'native',
        editable = False,
        #dropdown = {'Gerente de Zona': },
        style_table =  {
            'overflowY': 'scroll',
            'overflowY': 'scroll',
            'height': 200,
            'minWidth': '100%'
            },
        style_cell = {
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'textAlign': 'center',
            #'width': '135px',
            'fontSize': 16,
            'font-family': 'sans-serif'
            },
        style_header={
            'backgroundColor': '#FFA651',
            'fontWeight': 'bold',
            'fontSize': 15,
            },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
            ],
        style_cell_conditional = [
            ],
        tooltip_data = [
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
                } for row in archivo.to_dict('rows')
            ],
        tooltip_duration = None
        )

    return table

def make_df_bars(data, edad, lote, comparacion):
    export = pd.DataFrame()
    for ed in range(len(edad)):
        for i in range(1, len(lote) + 1):
            dt_exp = pd.DataFrame({'Lote': [nan],
                                'Edad': [nan],
                                'VPI': [nan],
                                'Conversión alimenticia': [nan],
                                'Consumo acumulado g/ave': [nan],
                                'Peso cierre semana g/ave': [nan],
                                'VPI referencia': [nan],
                                'Conversión alimenticia referencia': [nan],
                                'Consumo acumulado g/ave referencia': [nan],
                                'Peso cierre semana g/ave referencia': [nan]})
            if comparacion != 'SIN COMPARAR':
                try:
                    df = data[ed][[i, 'Referencia']]
                except Exception as e:
                    continue
                    print(e)
            else:
                try:
                    df = data[ed][[i]]
                except Exception as e:
                    continue
                    print(e)

            dt_exp['Lote'] = df.loc['Lote'][i]
            dt_exp['Edad'] = [edad[ed]]
            if edad[ed] == 7:
                dt_exp['VPI'] = df.loc['VPI'][i]
            if edad[ed] == 7 and comparacion != 'SIN COMPARAR':
                dt_exp['VPI referencia'] = df.loc['VPI']['Referencia']

            dt_exp['Conversión alimenticia'] = df.loc['Conversión alimenticia'][i]
            dt_exp['Consumo acumulado g/ave'] = df.loc['Consumo acumulado g/ave'][i]
            dt_exp['Peso cierre semana g/ave'] = df.loc['Peso cierre semana g/ave'][i]

            if comparacion != 'SIN COMPARAR':
                dt_exp['Conversión alimenticia referencia'] = df.loc['Conversión alimenticia']['Referencia']
                dt_exp['Consumo acumulado g/ave referencia'] = df.loc['Consumo acumulado g/ave']['Referencia']
                dt_exp['Peso cierre semana g/ave referencia'] = df.loc['Peso cierre semana g/ave']['Referencia']
            export = export.append(dt_exp)
    export.reset_index(drop = True, inplace = True)
    return export