import pandas as pd
from faker import Faker
import random
from time import sleep

fake = Faker()
# pd.read_csv('types.csv', index_col=0).drop(columns=[
#    'lang', 'year', 'links', 'types', 'place_id', 'level']).to_csv('types3.csv')
df = pd.read_csv('../datasets/types3.csv', index_col=0)
smal_lat, big_lat = df.loc[:, 'lat'].min(), df.loc[:, 'lat'].max()
smal_lon, big_lon = df.loc[:, 'lng'].min(), df.loc[:, 'lng'].max()


def create_template_tweet(gov_area=None):
    user_id = random.randint(1, 10000000000000)
    date = fake.date_time()
    is_weekend = random.choice((False, True))
    lat = random.uniform(smal_lat, big_lat),
    lng = random.uniform(smal_lon, big_lon),
    text = fake.sentence(random.randint(5, 20))
    gov = gov_area[0]
    area = gov_area[1]

    row = dict(
        user_id=user_id, date=date, is_weekend=is_weekend, text=text,
        lat=lat, lng=lng, governorate=gov, area=area
    )
    return pd.Series(row)


unique_areas = df.loc[:, 'area'].unique()

inter_df = pd.DataFrame(columns=df.columns)


for _ in range(100):
    row = create_template_tweet(
        gov_area=('some_gov', random.choice(unique_areas)))
    inter_df.loc[len(inter_df.index)] = row

inter_df.to_csv('../datasets/inter_types.csv')
