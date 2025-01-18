# import sqlalchemy
# from random import randint

# # NOTE: friend recommended pypika for SQL statements
# engine = sqlalchemy.create_engine(
#     'postgresql+pg8000://postgres:<password_here>@localhost:5433/Twitter_Streaming_DB'
# )


# # returns a dict of district => gov
# def get_gov_names(districts):
#     districts = [dis.replace("'", "''") for dis in districts]

#     query = 'SELECT DISTINCT districts, governorate ' \
#             'FROM public."Table_2018" ' \
#             'WHERE districts IN ({}) '.format(
#                 ','.join([f"'{district}'" for district in districts])
#             )

#     stmt = sqlalchemy.text(query)

#     with engine.connect() as conn:
#         res = conn.execute(stmt)
#         rows = res.all()
#         district_gov_dict = dict(zip(
#             [row[0] for row in rows],
#             [row[1] for row in rows]
#         ))

#     return district_gov_dict


# # returns  a list of distinct govs
# def get_distinct_govs():
#     query = 'SELECT DISTINCT governorate FROM public."Table_2018";'

#     stmt = sqlalchemy.text(query)
#     with engine.connect() as conn:
#         res = conn.execute(stmt)
#         rows = res.all()
#         govs = [i[0] for i in rows]
#         return govs


# # get all districts with a list of govs
# def get_districts(govs):
#     query = f"""
#         SELECT DISTINCT districts
#         FROM public."Table_2018" as t1
#         WHERE t1.governorate IN ({','.join([f"'{gov}'" for gov in govs])})
#         AND t1.districts IS NOT NULL
#         UNION
#         SELECT DISTINCT districts
#         FROM public."Table_2019" as t2
#         WHERE t2.governorate IN ({','.join([f"'{gov}'" for gov in govs])})
#         AND t2.districts IS NOT NULL;
#     """

#     stmt = sqlalchemy.text(query)

#     with engine.connect() as conn:
#         res = conn.execute(stmt)
#         rows = res.all()
#         districts = [row[0] for row in rows]

#     # # either pull all districts at the beginning of the program into a dictionary
#     # # or run an SQL query each time (i think dict is probably the better idea)
#     # return districts
#     return districts


# def add_districts_govs(query, govs, districts, table_alias):
#     if districts:
#         districts = [dis.replace("'", "''") for dis in districts]
#         query += " AND "
#         query += ' OR '.join([f" {table_alias}.districts = '{dis}' "
#                               for dis in districts])
#     elif govs:
#         query += " AND "
#         query += ' OR '.join([f" {table_alias}.governorate = '{gov}' "
#                               for gov in govs])
#     return query


# def create_sql_data_query(table_name, table_alias, cols,
#                           date_begin, date_end, hour_begin, hour_end, govs,
#                           districts):
#     columns = [f'{table_alias}.{col}' for col in cols]
#     columns = ','.join(columns)
#     query = f"" \
#         f"SELECT {columns} " \
#         f"FROM public.\"{table_name}\" AS {table_alias} " \
#         f"WHERE \
#             {table_alias}.date BETWEEN '{date_begin}'::date AND '{date_end}'::date \
#             AND {table_alias}.hour BETWEEN {hour_begin} AND {hour_end} \
#             AND {table_alias}.text IS NOT NULL "

#     query = add_districts_govs(query, govs, districts, table_alias)

#     return query


# def get_data(date_begin, date_end, hour_begin, hour_end, govs, districts):
#     tables = (('Table_2018', 't1'), ('Table_2019', 't2'))

#     cols = ('lat', 'lng', 'text', 'hour', 'date', 'districts')

#     querys = [create_sql_data_query(table[0], table[1], cols,
#                                     date_begin, date_end, hour_begin, hour_end,
#                                     govs, districts)
#               for table in tables]

#     total_query = ' UNION ALL '.join(querys)
#     total_query += ' LIMIT 1000;'

#     stmt = sqlalchemy.text(total_query)

#     with engine.connect() as conn:
#         res = conn.execute(stmt)
#         rows = res.all()
#         lat = [row[0] for row in rows]
#         lng = [row[1] for row in rows]
#         text = [row[2] for row in rows]
#         hour = [row[3] for row in rows]
#         date = [row[4] for row in rows]
#         districts = [row[5] for row in rows]
#     return lat, lng, text, hour, date, districts


# def get_min_date():
#     query = 'SELECT Min(date) FROM public."Table_2018"'
#     stmt = sqlalchemy.text(query)
#     with engine.connect() as conn:
#         res = conn.execute(stmt)
#         date = res.all()[0][0]
#     # just find the oldest tweet manually and place it in here it won't
#     # be changing.
#     return date


# # get the latest date
# def get_max_date():
#     query = 'SELECT Max(date) FROM public."Table_2019"'
#     stmt = sqlalchemy.text(query)
#     with engine.connect() as conn:
#         res = conn.execute(stmt)
#         date = res.all()[0][0]
#     # a day before the today (in kuwait time)
#     return date


# def get_random_sample():
#     lat, lng, hour = None, None, None
#     query = 'SELECT lat,lng,date, hour,districts,text, user_id ' \
#             'FROM public."Table_2018" ' \
#             'ORDER BY RANDOM() ' \
#             'LIMIT {}'.format(randint(2, 20))

#     with engine.connect() as conn:
#         stmt = sqlalchemy.text(query)
#         res = conn.execute(stmt)
#         rows = res.all()
#         lat = [row[0] for row in rows]
#         lng = [row[1] for row in rows]
#         date = [row[2] for row in rows]
#         hour = [row[3] for row in rows]
#         districts = [row[4] for row in rows]
#         texts = [row[5] for row in rows]
#         user_id = [row[6] for row in rows]

#     return lat, lng, date, hour, districts, texts, user_id


# def create_sql_count_query(col, date_begin, date_end, hour_begin, hour_end,
#                            govs, districts):
#     tables = [['Table_2018', 't1'], ['Table_2019', 't2']]

#     columns = [col]

#     querys = [create_sql_data_query(table[0], table[1], columns,
#                                     date_begin, date_end, hour_begin,
#                                     hour_end, govs, districts)
#               for table in tables]

#     total_query = ' UNION ALL '.join(querys)

#     query = f"SELECT sub.{col}, COUNT(*) as c " \
#         f"FROM ( " \
#         f"{total_query} " \
#         f") as sub " \
#         f"GROUP BY sub.{col} " \
#         f"ORDER BY c DESC "
#     return query


# def get_gov_counts(date_begin, date_end, hour_begin, hour_end, gov):
#     query = create_sql_count_query('governorate', date_begin, date_end,
#                                    hour_begin, hour_end, gov, None)

#     stmt = sqlalchemy.text(query)

#     with engine.connect() as conn:
#         res = conn.execute(stmt)
#         rows = res.all()
#         gov_names = [row[0] for row in rows]
#         gov_count = [row[1] for row in rows]
#     return gov_names, gov_count


# def get_district_counts(date_begin, date_end, hour_begin, hour_end,
#                         gov, district):
#     query = create_sql_count_query('districts', date_begin, date_end,
#                                    hour_begin, hour_end, gov, district)

#     query += ' LIMIT 10'

#     stmt = sqlalchemy.text(query)

#     with engine.connect() as conn:
#         res = conn.execute(stmt)
#         rows = res.all()
#         district_names = [row[0] for row in rows]
#         district_count = [row[1] for row in rows]

#     return district_names, district_count


# def get_hour_counts(date_begin, date_end, hour_begin, hour_end,
#                     govs, districts):
#     query = create_sql_count_query('hour', date_begin, date_end,
#                                    hour_begin, hour_end, govs, districts)

#     stmt = sqlalchemy.text(query)

#     with engine.connect() as conn:
#         res = conn.execute(stmt)
#         rows = res.all()
#         hours = [row[0] for row in rows]
#         hours_count = [row[1] for row in rows]
#     return hours, hours_count
