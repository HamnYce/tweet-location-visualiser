from time import sleep

import pandas as pd
import sqlalchemy
from sqlalchemy import Column, MetaData, Table, text
from sqlalchemy.orm import Query

engine = sqlalchemy.create_engine(
    'postgresql+pg8000://postgres:Megaman1234@localhost:5433/Twitter_Streaming_DB'
)

metadata_obj = MetaData()

table = Table(
    'Table_2018',
    metadata_obj,
    Column('userid', sqlalchemy.String(40)),
    Column('language', sqlalchemy.String(10)),
    Column('date_local', sqlalchemy.DATE),
    Column('app', sqlalchemy.String(100)),
    Column('tweet_text', sqlalchemy.String(1000)),
    Column('lat', sqlalchemy.FLOAT),
    Column('lng', sqlalchemy.FLOAT),
    Column('place_name', sqlalchemy.String(500)),
    Column('screen_name', sqlalchemy.String(100)),
    Column('hashtags', sqlalchemy.String(200)),
    Column('country', sqlalchemy.String(50)),
    Column('governorate', sqlalchemy.String(100)),
    Column('districts', sqlalchemy.String(100)),
)

with engine.connect() as conn:
    res = conn.execute(sqlalchemy.text(
        'SELECT * FROM public."Table_2018" LIMIT 1000;'
    ))
    rows = res.all()
    print(rows[0])
