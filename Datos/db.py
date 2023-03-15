import pymysql
import pymysql.cursors
import pandas as pd
from datetime import datetime
import time


def usuario():
    ## Datos de acceso
    DB_instance_identifier = 'DB-APP'
    username = 'nutricion'
    password = 'Nutr1c10n$'
    host = 'db-app.cyvxpxlgwwja.us-east-2.rds.amazonaws.com'
    Database_port = 3306

    # Connect to the database
    connection = pymysql.connect(host = host,
                                user = username,
                                password = password,
                                database='AppPeces',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            sql = 'SELECT nombre, usuario, rol_usuario, doc_id, contraseña, pais FROM usuarios'
            cursor.execute(sql)
            result = cursor.fetchall()

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()
    return pd.DataFrame(result)

def get_data(sql):
    ## Datos de acceso
    DB_instance_identifier = 'DB-APP'
    username = 'nutricion'
    password = 'Nutr1c10n$'
    host = 'db-app.cyvxpxlgwwja.us-east-2.rds.amazonaws.com'
    Database_port = 3306

    # Connect to the database
    connection = pymysql.connect(host = host,
                                user = username,
                                password = password,
                                database='AppPeces',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()
    return pd.DataFrame(result)

def change_pw(new_pw, user):
    ## Datos de acceso
    DB_instance_identifier = 'DB-APP'
    username = 'nutricion'
    password = 'Nutr1c10n$'
    host = 'db-app.cyvxpxlgwwja.us-east-2.rds.amazonaws.com'
    Database_port = 3306

    # Connect to the database
    connection = pymysql.connect(host = host,
                                user = username,
                                password = password,
                                database='AppPeces',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:

            sql = f'''
                UPDATE `usuarios` SET `contraseña` = '{new_pw}' WHERE (`usuario` = '{user}');
            '''
            #print(sql)
            cursor.execute(sql)
            result = cursor.fetchall()
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

def crear_usuario(usuario, rol, doc_id, pais, nombre, pw):
    ## Datos de acceso
    DB_instance_identifier = 'DB-APP'
    username = 'nutricion'
    password = 'Nutr1c10n$'
    host = 'db-app.cyvxpxlgwwja.us-east-2.rds.amazonaws.com'
    Database_port = 3306

    # Connect to the database
    connection = pymysql.connect(host = host,
                                user = username,
                                password = password,
                                database='AppPeces',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            sql = f'''
           INSERT INTO `usuarios` (usuario, doc_id, rol_usuario, nombre, contraseña, pais)
           VALUES ('{usuario}', {doc_id}, '{rol}', '{nombre.title()}', '{pw}', '{pais.upper()}');
            '''
            cursor.execute(sql)
            result = cursor.fetchall()
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

def crear_gerente(documento, nombre, planta, pais, especialista, creador, correo, telefono):
    ## Datos de acceso
    DB_instance_identifier = 'DB-APP'
    username = 'nutricion'
    password = 'Nutr1c10n$'
    host = 'db-app.cyvxpxlgwwja.us-east-2.rds.amazonaws.com'
    Database_port = 3306

    # Connect to the database
    connection = pymysql.connect(host = host,
                                user = username,
                                password = password,
                                database='AppPeces',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            sql = f'''
           INSERT INTO `gerentes` (documento_identidad, nombre_gerente, planta, telefono, correo, pais, especialista, creador, fecha)
           VALUES ('{documento}', '{nombre.upper()}', '{planta.upper()}', '{telefono}', '{correo}', '{pais.upper()}', '{especialista}', '{creador.upper()}', '{datetime.today().date().strftime('%Y-%m-%d')}');
            '''
            cursor.execute(sql)
            result = cursor.fetchall()
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

def crear_cliente(nit, nombre, gerente, pais, telefono, correo, creador):
    ## Datos de acceso
    DB_instance_identifier = 'DB-APP'
    username = 'nutricion'
    password = 'Nutr1c10n$' 
    host = 'db-app.cyvxpxlgwwja.us-east-2.rds.amazonaws.com'
    Database_port = 3306

    # Connect to the database
    connection = pymysql.connect(host = host,
                                user = username,
                                password = password,
                                database='AppPeces',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            sql = f'''
           INSERT INTO `clientes` (nit, nombre_cliente, gerente_zona, pais, telefono, correo, creador, fecha)
           VALUES ({nit}, '{nombre.upper()}', '{gerente}', '{pais}', '{telefono}', '{correo}', '{creador}', '{datetime.today().date().strftime('%Y-%m-%d')}');
            '''
            cursor.execute(sql)
            result = cursor.fetchall()
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

def agregar_galpon(nit, granja, galpon,temperatura, humedad, tipo_galpon, tipo_comedero, tipo_bebedero, creador):
    ## Datos de acceso
    DB_instance_identifier = 'DB-APP'
    username = 'nutricion'
    password = 'Nutr1c10n$' 
    host = 'db-app.cyvxpxlgwwja.us-east-2.rds.amazonaws.com'
    Database_port = 3306

    # Connect to the database
    connection = pymysql.connect(host = host,
                                user = username,
                                password = password,
                                database='AppPeces',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            sql = f'''
           INSERT INTO `galpones` (nit_cliente, nombre_granja, nombre_galpon, temperatura, humedad, tipo_galpon, tipo_comedero, tipo_bebedero, creador)
           VALUES ({nit}, '{granja}', '{galpon}', {temperatura}, {humedad}, '{tipo_galpon}', '{tipo_comedero}', '{tipo_bebedero}', '{creador}');
            '''
            cursor.execute(sql)
            result = cursor.fetchall()
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()

def ifExist(sql):
    ## Datos de acceso
    DB_instance_identifier = 'DB-APP'
    username = 'nutricion'
    password = 'Nutr1c10n$'
    host = 'db-app.cyvxpxlgwwja.us-east-2.rds.amazonaws.com'
    Database_port = 3306

    # Connect to the database
    connection = pymysql.connect(host = host,
                                user = username,
                                password = password,
                                database='AppPeces',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()
    return list(result[0].values())

def cerrar_lote_(lote=''):
    ## Datos de acceso
    DB_instance_identifier = 'DB-APP'
    username = 'nutricion'
    password = 'Nutr1c10n$'
    host = 'db-app.cyvxpxlgwwja.us-east-2.rds.amazonaws.com'
    Database_port = 3306

    # Connect to the database
    connection = pymysql.connect(host = host,
                                user = username,
                                password = password,
                                database='AppPeces',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            sql = f"UPDATE lotes SET cerrado = 'Si'  WHERE id_lote = '{lote}'"
            print(sql)
            cursor.execute(sql)
            result = cursor.fetchall()
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()


def trazabilidad(doc_id, tipo_usuario, fecha, accion):
    ## Datos de acceso
    DB_instance_identifier = 'DB-APP'
    username = 'nutricion'
    password = 'Nutr1c10n$'
    host = 'db-app.cyvxpxlgwwja.us-east-2.rds.amazonaws.com'
    Database_port = 3306

    # Connect to the database
    connection = pymysql.connect(host = host,
                                user = username,
                                password = password,
                                database='AppPeces',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            sql = f'''
            INSERT INTO `trazabilidad` (doc_id, tipo_usuario, fecha, accion)
            VALUES ('{doc_id}', '{tipo_usuario}', '{fecha}', '{accion}');'''
            # print(sql)
            cursor.execute(sql)
            result = cursor.fetchall()
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        connection.commit()