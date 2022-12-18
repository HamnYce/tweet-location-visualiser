import sqlalchemy
from random import randint

# TODO: Normalise Schema
#   (This will provide a performance boost for get_districts & get_govs
#   (This method can also be used to group multiple tweets in the same location
#   and have a count attribute to represent them and a couple of sample tweets.
#   In theory this should make displaying the scatter graph not very hard and
#   we might be able to transform it into a bubble graph which can give more
#   information)

engine = sqlalchemy.create_engine(
    'postgresql+pg8000://postgres:Megaman1234@localhost:5433/Twitter_Streaming_DB'
)


def get_distinct_govs():
    query = 'SELECT DISTINCT governorate FROM public."Table_2018";'

    with engine.connect() as conn:
        res = conn.execute(sqlalchemy.text(query))
        rows = res.all()
        govs = [i[0] for i in rows]
        return govs


def create_sql_data_query(table_name, table_alias, cols,
                          date_begin, date_end, hour_begin, hour_end, govs,
                          districts):

    columns = [f'{table_alias}.{col}' for col in cols]
    columns = ','.join(columns)
    query = f"\
SELECT {columns} \
FROM public.\"{table_name}\" AS {table_alias} \
WHERE \
{table_alias}.date BETWEEN '{date_begin}'::date AND '{date_end}'::date \
AND {table_alias}.hour BETWEEN {hour_begin} AND {hour_end} \
AND {table_alias}.text IS NOT NULL "

    if districts:
        query += " AND "
        query += [f" {table_alias}.districts = '{dis}' " for dis in districts].join(' OR ')
    elif govs:
        query += " AND "
        query += [f" {table_alias}.districts = '{gov}' " for gov in govs].join(' OR ')

    return query


def create_sql_count_query(col, date_begin, date_end, hour_begin, hour_end,
                           govs, districts):
    tables = [['Table_2018', 't1'], ['Table_2019', 't2']]
    columns = [col]
    querys = [create_sql_data_query(table[0], table[1], columns,
                                    date_begin, date_end, hour_begin,
                                    hour_end, govs, districts)
              for table in tables]
    total_query = ' UNION ALL '.join(querys)

    query = f"\
SELECT sub.{col}, COUNT(*) as c \
FROM ( \
{total_query} \
) as sub \
GROUP BY sub.{col} \
ORDER BY c DESC \
"
    return query


# TODO: change everything to mesh with
def get_data(date_begin, date_end, hour_begin, hour_end, govs, districts):
    tables = (('Table_2018', 't1'), ('Table_2019', 't2'))

    cols = ('lat', 'lng', 'text', 'hour', 'date')

    querys = [create_sql_data_query(table[0], table[1], cols,
                                    date_begin, date_end, hour_begin, hour_end,
                                    govs, districts)
              for table in tables]

    total_query = ' UNION ALL '.join(querys)
    total_query += ' LIMIT 1000;'

    stmt = sqlalchemy.text(total_query)

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
    query = create_sql_count_query('governorate', date_begin, date_end,
                                   hour_begin, hour_end, gov, None)

    stmt = sqlalchemy.text(query)

    with engine.connect() as conn:
        res = conn.execute(stmt)
        rows = res.all()
        gov_names = [row[0] for row in rows]
        gov_count = [row[1] for row in rows]
    return gov_names, gov_count


def get_district_counts(date_begin, date_end, hour_begin, hour_end, gov, district):
    query = create_sql_count_query('districts', date_begin, date_end,
                                   hour_begin, hour_end, gov, district)
    query += ' LIMIT 10'
    stmt = sqlalchemy.text(query)

    with engine.connect() as conn:
        res = conn.execute(stmt)
        rows = res.all()
        district_names = [row[0] for row in rows]
        district_count = [row[1] for row in rows]
    return district_names, district_count


def get_hour_counts(date_begin, date_end, hour_begin, hour_end, gov, district):
    query = create_sql_count_query('hour', date_begin, date_end,
                                   hour_begin, hour_end, gov, district)

    stmt = sqlalchemy.text(query)

    with engine.connect() as conn:
        res = conn.execute(stmt)
        rows = res.all()
        hours = [row[0] for row in rows]
        hours_count = [row[1] for row in rows]
    return hours, hours_count


def get_districts(governorate):

    query = 'SELECT DISTINCT governorate FROM public."Table_2018";'
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
