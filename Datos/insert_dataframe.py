import pymysql
pymysql.install_as_MySQLdb()
import pandas as pd
from sqlalchemy import create_engine


def insert_dataframe(data, tabla):
       db_data = 'mysql+mysqldb://' + 'nutricion' + ':' + 'Nutr1c10n$' + '@' + 'db-app.cyvxpxlgwwja.us-east-2.rds.amazonaws.com' + ':3306/' \
              + 'AppPeces' + '?charset=utf8mb4'
       engine = create_engine(db_data)

       # Connect to the database
       connection = pymysql.connect(host='db-app.cyvxpxlgwwja.us-east-2.rds.amazonaws.com',
                            user='nutricion',
                            password='Nutr1c10n$',
                            db='AppPeces')    

       # create cursor
       cursor=connection.cursor()
       # Execute the to_sql for writting DF into SQL
       data.to_sql(tabla, engine, if_exists='append', index=False)    

       # Execute query
       #sql = f"SELECT * FROM `tabla`"
       #cursor.execute(sql)

       # Fetch all the records
       #result = cursor.fetchall()
       # for i in result:
       # print(i)