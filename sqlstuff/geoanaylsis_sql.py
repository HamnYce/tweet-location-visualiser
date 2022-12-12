from time import sleep

import pandas as pd
import sqlalchemy
from sqlalchemy import Column, MetaData, Table, text
from sqlalchemy.orm import Query

engine = sqlalchemy.create_engine(
    'postgresql+pg8000://postgres:Megaman1234@localhost:5433/Twitter_Streaming_DB'
)

with engine.connect() as conn:
    res = conn.execute(sqlalchemy.text(
        'SELECT lat FROM public."Table_2018" LIMIT 1000;'
    ))
    print(rows)
