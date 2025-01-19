import dash
from dash import dcc, callback, Input, Output, html
from dash.dash_table import DataTable
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

df = pd.read_csv('data/timeseries.csv', index_col=None, parse_dates=['date'])
df = df.drop(columns=['user_name'])
df['hour'] = df['date'].apply(lambda d: d.hour)

app = dash.Dash(__name__, external_stylesheets=[
                dbc.themes.BOOTSTRAP, dbc.themes.DARKLY])


def date_picker():
    start_date = df['date'].min()
    end_date = df['date'].max()
    return dcc.DatePickerRange(
        start_date,
        end_date,
        min_date_allowed=start_date,
        max_date_allowed=end_date,
        stay_open_on_select=True,
        id='date-range-picker',

    )


def hour_picker():
    min_hour = df['hour'].min()
    max_hour = df['hour'].max()
    return dcc.RangeSlider(
        min=min_hour,
        max=max_hour,
        id='hour-range-slider',
    )


def tweet_data_table(df):
    return DataTable(df.to_dict('records'), page_size=12, fill_width=True,
                     style_header={"backgroundColor": "#2c2c2c",
                                   "color": "white", "fontWeight": "bold"},
                     style_data={"backgroundColor": "#2c2c2c",
                                 "color": "white"},
                     style_cell={"textAlign": "left",
                                 "border": "1px solid #444444"},
                     style_table={"overflowX": "auto"})


def top_locations_bar(df):
    locations = df['user_location'].value_counts().iloc[:50]
    fig = px.bar(title='Top Locations', x=locations.index, y=locations.values, labels={
                 'x': 'location', 'y': 'Number of Tweets'}, template='plotly_dark')
    return fig


def tweet_map(df):
    fig = px.scatter_mapbox(df, lat='lat', lon='long', opacity=0.1,
                            mapbox_style='carto-darkmatter', template='plotly_dark')
    fig.update_layout(
        mapbox=dict(
            center={"lat": df["lat"].mean(), "lon": df["long"].mean()},
            zoom=1,
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )
    return fig


@callback(
    Output('tweet-map', 'figure'),
    Output('top-locations-bar', 'figure'),
    Output('tweet-data-table', 'children'),
    Input('date-range-picker', 'start_date'),
    Input('date-range-picker', 'end_date'),
    Input('hour-range-slider', 'value'),
)
def update_data(start_date, end_date, hour_range):
    global df
    f_df = df
    if start_date:
        a = df['date'] >= start_date
        b = df['date'] <= end_date
        f_df = df.loc[a & b, :]
    if hour_range:
        c = df['hour'] >= hour_range[0]
        d = df['hour'] <= hour_range[1]
        f_df = df.loc[c & d, :]
    return (tweet_map(f_df), top_locations_bar(f_df), tweet_data_table(f_df))


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Row(["Date:", date_picker()], ),
            dbc.Row(["Hour:", hour_picker()]),
        ]),
        dbc.Col([dcc.Graph(id='tweet-map')])
    ]),
    dbc.Row([
        dbc.Col([dcc.Graph(id='top-locations-bar')], className='col-md-6'),
        dbc.Col([html.Div(id='tweet-data-table')], className='col-md-6'),
    ], ),
])


# Run the App
if __name__ == '__main__':
    app.run()
