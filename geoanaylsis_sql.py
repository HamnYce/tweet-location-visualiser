from time import sleep

import pandas as pd
import sqlalchemy
from sqlalchemy.orm import Query
from sqlalchemy import Column, MetaData, Table, text

engine = sqlalchemy.create_engine(
    'postgresql+pg8000://postgres:Megaman1234@localhost:5433/Testing_Database')

df = pd.read_csv('types.csv', index_col=0)

metadata_obj = MetaData()

table = Table(
    'geoanalysis',
    metadata_obj,
    Column('user_id', sqlalchemy.String(20)),
    Column('lang', sqlalchemy.VARCHAR(4)),
    Column('date', sqlalchemy.TIMESTAMP),
    Column('is_weekend', sqlalchemy.Boolean),
    Column('year', sqlalchemy.INT),
    Column('text', sqlalchemy.String(1000)),
    Column('lat', sqlalchemy.FLOAT),
    Column('lng', sqlalchemy.FLOAT),
    Column('governorate', sqlalchemy.String(20)),
    Column('area', sqlalchemy.String(50)),
    Column('links', sqlalchemy.String(100)),
    Column('level', sqlalchemy.FLOAT),
    Column('place_id', sqlalchemy.String(30)),
    Column('types', sqlalchemy.String(500)),
)
column_names = df.columns

with engine.connect() as conn:
    result = conn.execute(
        sqlalchemy.select(table.c.lat, table.c.lng)
    )
    print(list(result))
