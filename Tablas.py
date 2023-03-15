import dash_table
import dash_bootstrap_components as dbc
import pandas as pd


# def dashtable(archivo, tipo = 'p1'):
#     archivo.sort_values(by = 'Fecha', inplace = True, ascending = False)

#     if tipo == 'p1':
#         types = ['datetime', 'text', 'numeric', 'text'] + ['numeric']*2 + ['text', 'numeric', 'text'] + ['numeric']*27 + ['text']
#     if tipo == 'p2':
#         types = ['datetime', 'numeric', 'text', 'text', 'text', 'numeric', 'text'] +  ['numeric']*6 + ['text']

#     if tipo == 'p3':
#         types = ['datetime'] + ['numeric']*8 + ['text']*2 + ['numeric']*24 + ['text']

#     table = dash_table.DataTable(
#         data = archivo.to_dict('records'),
#         columns = [{'name': i, 'id': i, 'type': j} for i, j in zip(archivo.columns, types)],
#         filter_action = 'native',
#         editable = False,
#         #dropdown = {'Gerente de Zona': },
#         style_table =  {
#             'overflowY': 'scroll',
#             'overflowY': 'scroll',
#             'height': 600,
#             },
#         style_cell = {
#             'overflow': 'hidden',
#             'textOverflow': 'ellipsis',
#             'textAlign': 'center',
#             'width': '0',
#             'fontSize': 16,
#             'font-family': 'sans-serif'
#             },
#         style_header={
#             'backgroundColor': '#FFA651',
#             'fontWeight': 'bold'
#             },
#         style_data_conditional=[
#             {
#                 'if': {'row_index': 'odd'},
#                 'backgroundColor': 'rgb(248, 248, 248)'
#             }
#             ],
#         style_cell_conditional = [
#             ],
#         tooltip_data = [
#             {
#                 column: {'value': str(value), 'type': 'markdown'}
#                 for column, value in row.items()
#                 } for row in archivo.to_dict('rows')
#             ],
#         tooltip_duration = None
#         )

#     return table

def render_table(data):
    table = dbc.Table.from_dataframe(data, striped=True, bordered=True, hover=True)
    return table

