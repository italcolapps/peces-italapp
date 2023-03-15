import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from time import sleep
from datetime import datetime

# Agregar informacion al archivo de google drive
def actualizar_valor(archivo, hoja,  datos, update = False):
    if update == False:
        return ''
    # define the scope
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name('Archivos/check-list-pollo-47c68e363c26.json', scope)
    # authorize the clientsheet
    client = gspread.authorize(creds)
    # get the instance of the Spreadsheet
    sheet_archivo = client.open(archivo)
    # get the first sheet of the Spreadsheet
    sheet_archivo_instance = sheet_archivo.get_worksheet(hoja)
    fila = sheet_archivo_instance.row_count
    sheet_archivo_instance.insert_row(values = list(datos.values()), index = fila)
    sleep(1)

def tablas_drive(Archivo, hoja, tipo = 'ingreso', parametro = '', update = False):
    if update == False:
        return ''
    # define the scope
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name('Archivos/check-list-pollo-47c68e363c26.json', scope)

    # authorize the clientsheet
    client = gspread.authorize(creds)


    # get the instance of the Spreadsheet
    sheet_archivo = client.open(Archivo)

    if tipo == 'ingreso':
        # get the first sheet of the Spreadsheet
        sheet_archivo_instance = sheet_archivo.get_worksheet(hoja)

        data = pd.DataFrame.from_dict(sheet_archivo_instance.get_all_records())
        #data['Fecha'] = [datetime.strptime(i, '%d/%m/%y').date() for i in data['Fecha']]
        sleep(1)
        return data

    if tipo == 'consulta':
        if parametro == 'pass':
            sheet_archivo_instance = sheet_archivo.get_worksheet(hoja)
            data = pd.DataFrame.from_dict(sheet_archivo_instance.get_all_records())
            #data[['Usuario', 'Rol']].to_csv('Datos/Users_rols.csv', index = False)
            #word = [(str(u), str(p)) for u,p in zip(data['Usuario'], data['Contraseña'])]
            word = {str(u): str(p) for u,p in zip(data['Usuario'], data['Contraseña'])}
            del data
            sleep(1)
            return word
