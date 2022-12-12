import sqlalchemy
from random import randint

engine = sqlalchemy.create_engine(
    'postgresql+pg8000://postgres:Megaman1234@localhost:5433/Twitter_Streaming_DB'
)


def get_distinct_govs():
    with engine.connect() as conn:
        res = conn.execute(sqlalchemy.text(
            'SELECT DISTINCT governorate FROM public."Table_2018";'
        ))
        rows = res.all()
        govs = [i[0] for i in rows]
        return govs


def create_sql_data_query(table_name, table_alias, cols,
                          date_begin, date_end, hour_begin, hour_end, gov, district):
    columns = ['{}.{}'.format(table_alias, col) for col in cols]
    columns = ','.join(columns)
    query = "\
SELECT {columns} \
FROM public.\"{table_name}\" as {alias} \
WHERE \
{alias}.date BETWEEN '{date_begin}'::date AND '{date_end}'::date \
AND {alias}.hour BETWEEN {hour_begin} AND {hour_end} \
AND {alias}.text IS NOT NULL \
{area_condition} \
"
    area_condition = ''

    if district:
        area_condition = "AND {}.districts = '{}'".format(
            table_alias, district)
    elif gov:
        area_condition = "AND {}.governorate = '{}'".format(table_alias, gov)

    query = query.format(
        table_name=table_name, alias=table_alias, columns=columns,
        date_begin=date_begin, date_end=date_end, hour_begin=hour_begin,
        hour_end=hour_end, area_condition=area_condition
    )
    return query


def create_sql_count_query(col, date_begin, date_end, hour_begin, hour_end, gov, district):
    tables = [['Table_2018', 't1'], ['Table_2019', 't2']]
    columns = [col]
    querys = [create_sql_data_query(table[0], table[1], columns,
                                    date_begin, date_end, hour_begin,
                                    hour_end, gov, district)
              for table in tables]
    total_query = ' UNION ALL '.join(querys)
    query = "\
SELECT sub.{col}, COUNT(*) as c \
FROM ( \
{nested_query} \
) as sub \
GROUP BY sub.{col} \
ORDER BY c DESC \
LIMIT 10 \
;"
    return query.format(col=col, nested_query=total_query)


def get_data(date_begin, date_end, hour_begin, hour_end, gov, district):
    tables = (('Table_2018', 't1'), ('Table_2019', 't2'))
    cols = ('lat', 'lng', 'text', 'hour', 'date')
    querys = [create_sql_data_query(table[0], table[1], cols,
                                    date_begin, date_end, hour_begin, hour_end,
                                    gov, district)
              for table in tables]
    total_query = ' UNION ALL '.join(querys)
    total_query += ' LIMIT 1000;'

    stmt = sqlalchemy.text(total_query)

    # TODO: efficient way of getting columns as list
    with engine.connect() as conn:
        res = conn.execute(stmt)
        rows = res.all()
        lat = [row[0] for row in rows]
        lng = [row[1] for row in rows]
        text = [row[2] for row in rows]
        hour = [row[3] for row in rows]
        date = [row[4] for row in rows]
    return lat, lng, text, hour, date


def get_gov_counts(date_begin, date_end, hour_begin, hour_end, gov):
    query = create_sql_count_query(
        'governorate', date_begin, date_end, hour_begin, hour_end, gov, None)
    stmt = sqlalchemy.text(query)
    with engine.connect() as conn:
        res = conn.execute(stmt)
        rows = res.all()
        gov_names = [row[0] for row in rows]
        gov_count = [row[1] for row in rows]
    return gov_names, gov_count


def get_district_counts(date_begin, date_end, hour_begin, hour_end, gov, district):
    query = create_sql_count_query(
        'districts', date_begin, date_end, hour_begin, hour_end, gov, district
    )
    stmt = sqlalchemy.text(query)
    with engine.connect() as conn:
        res = conn.execute(stmt)
        rows = res.all()
        district_names = [row[0] for row in rows]
        district_count = [row[1] for row in rows]
    return district_names, district_count


def get_hour_counts(date_begin, date_end, hour_begin, hour_end, gov, district):
    query = create_sql_count_query(
        'hour', date_begin, date_end, hour_begin, hour_end, gov, district
    )
    stmt = sqlalchemy.text(query)
    with engine.connect() as conn:
        res = conn.execute(stmt)
        rows = res.all()
        hours = [row[0] for row in rows]
        hours_count = [row[1] for row in rows]
    return hours, hours_count


def get_districts(governorate):
    query = '\
        SELECT DISTINCT districts \
FROM public."Table_2018" as t1 \
WHERE t1.governorate = \'{0}\' \
AND t1.districts IS NOT NULL \
UNION \
SELECT DISTINCT districts \
FROM public."Table_2019" as t2 \
WHERE t2.governorate = \'{0}\' \
AND t2.districts IS NOT NULL \
;'.format(governorate)
    stmt = sqlalchemy.text(query)
    with engine.connect() as conn:
        res = conn.execute(stmt)
        rows = res.all()
        districts = [row[0] for row in rows]
    # # either pull all districts at the beginning of the program into a dictionary
    # # or run an SQL query each time (i think dict is probably the better idea)
    # return districts
    return districts


def get_min_date():
    query = 'SELECT Min(date) FROM public."Table_2018"'
    stmt = sqlalchemy.text(query)
    with engine.connect() as conn:
        res = conn.execute(stmt)
        date = res.all()[0][0]
    # just find the oldest tweet manually and place it in here it won't
    # be changing.
    return date


def get_max_date():
    query = 'SELECT Max(date) FROM public."Table_2019"'
    stmt = sqlalchemy.text(query)
    with engine.connect() as conn:
        res = conn.execute(stmt)
        date = res.all()[0][0]
    # a day before the today (in kuwait time)
    return date


def get_random_sample():
    lat, lng, hour = None, None, None
    query = 'SELECT lat,lng,hour,districts,user_id \
FROM public."Table_2018" \
ORDER BY RANDOM() \
LIMIT {}'.format(randint(2, 20))

    with engine.connect() as conn:
        stmt = sqlalchemy.text(query)
        res = conn.execute(stmt)
        rows = res.all()
        lat = [row[0] for row in rows]
        lng = [row[1] for row in rows]
        hour = [row[2] for row in rows]
        districts = [row[3] for row in rows]
        user_id = [row[4] for row in rows]

    return lat, lng, hour, districts, user_id
