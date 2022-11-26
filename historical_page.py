import random

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import sqlalchemy
import datetime
token = open('.mapbox_token').read()
px.set_mapbox_access_token(token)
scatter_order_lis = [0, 23, 1, 22, 2, 21, 3, 20, 4, 19, 5,
                     18, 6, 17, 7, 16, 8, 15, 9, 14, 10, 13, 11, 12]

engine = sqlalchemy.create_engine(
    'postgresql+pg8000://postgres:Megaman1234@localhost:5433/Twitter_Streaming_DB'
)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY],
                assets_folder='assets/')


with engine.connect() as conn:
    # res = conn.execute(sqlalchemy.text(
    #     'SELECT lat, lng, date, weekend,year,month,day,hour FROM public."Table_2018" LIMIT 100;'
    # ))
    # rows = res.all()
    res = conn.execute(sqlalchemy.text(
        'SELECT DISTINCT governorate FROM public."Table_2018";'
    ))
    rows = res.all()
    govs = [i[0] for i in rows]
    res = conn.execute(sqlalchemy.text(
        'SELECT lat, lng FROM public."Table_2018" LIMIT 20;'
    ))
    rows = res.all()
    lat = [i[0] for i in rows]
    lng = [i[1] for i in rows]


def get_data(date_begin, date_end, hour_begin, hour_end, gov, district):
    query = '\
SELECT t1.lat,t1.lng,t1.text,t1.hour \
FROM public."Table_2018" as t1 \
WHERE \
t1.date BETWEEN \'{0}\'::date AND \'{1}\'::date \
AND t1.hour BETWEEN {2} AND {3} \
{4} \
{5} \
UNION ALL \
SELECT t2.lat,t2.lng,t2.text,t2.hour \
FROM public."Table_2019" as t2 \
WHERE \
t2.date BETWEEN \'{0}\'::date AND \'{1}\'::date \
AND t2.hour BETWEEN {2} AND {3} \
{6} \
{7} \
LIMIT 500 \
;'
    gov_query_1 = ''
    gov_query_2 = ''
    district_query_1 = ''
    district_query_2 = ''
    if gov:
        gov_query_1 = 'AND t1.governorate = \'{}\''.format(gov)
        gov_query_2 = 'AND t2.governorate = \'{}\''.format(gov)
    if district:
        district_query_1 = 'AND t1.districts = \'{}\''.format(district)
        district_query_2 = 'AND t2.districts = \'{}\''.format(district)
    query = query.format(date_begin, date_end, hour_begin, hour_end,
                         gov_query_1, district_query_1,
                         gov_query_2, district_query_2)
    stmt = sqlalchemy.text(query)

    with engine.connect() as conn:
        print('        execution Begin!')
        res = conn.execute(stmt)
        rows = res.all()
        print('        execution complete!')
        lat = [row[0] for row in rows]
        lng = [row[1] for row in rows]
        text = [row[2] for row in rows]
        hour = [row[3] for row in rows]
    return lat, lng, text, hour


def get_gov_counts(date_begin, date_end, hour_begin, hour_end, gov):
    query = '\
SELECT sub.governorate, COUNT(*) \
FROM (SELECT t1.governorate \
FROM public."Table_2018" as t1 \
WHERE t1.date BETWEEN \'{0}\'::date AND \'{1}\'::date \
AND t1.hour BETWEEN {2} AND {3} \
{4} \
UNION ALL \
SELECT t2.governorate \
FROM public."Table_2019" as t2 \
WHERE t2.date BETWEEN \'{0}\'::date AND \'{1}\'::date \
AND t2.hour BETWEEN {2} AND {3} \
{5} \
) as sub \
GROUP BY sub.governorate \
;'
    gov_query_1 = ''
    gov_query_2 = ''
    if gov:
        gov_query_1 = 'AND t1.governorate = \'{}\''.format(gov)
        gov_query_2 = 'AND t2.governorate = \'{}\''.format(gov)
    query = query.format(date_begin, date_end, hour_begin,
                         hour_end, gov_query_1, gov_query_2)
    stmt = sqlalchemy.text(query)
    with engine.connect() as conn:
        res = conn.execute(stmt)
        rows = res.all()
        gov_names = [row[0] for row in rows]
        gov_count = [row[1] for row in rows]
    return gov_names, gov_count


def get_district_counts(date_begin, date_end, hour_begin, hour_end, gov, district):
    query = '\
SELECT sub.districts, COUNT(*) \
FROM (SELECT t1.districts \
FROM public."Table_2018" as t1 \
WHERE t1.date BETWEEN \'{0}\'::date AND \'{1}\'::date \
AND t1.hour BETWEEN {2} AND {3} \
{4} \
{5} \
UNION ALL \
SELECT t2.districts \
FROM public."Table_2019" as t2 \
WHERE t2.date BETWEEN \'{0}\'::date AND \'{1}\'::date \
AND t2.hour BETWEEN {2} AND {3} \
{6} \
{7} \
) as sub \
GROUP BY sub.districts \
LIMIT 10 \
;'
    gov_query_1 = ''
    gov_query_2 = ''
    district_query_1 = ''
    district_query_2 = ''
    if gov:
        gov_query_1 = 'AND t1.governorate = \'{}\''.format(gov)
        gov_query_2 = 'AND t2.governorate = \'{}\''.format(gov)
    if district:
        district_query_1 = 'AND t1.districts = \'{}\''.format(district)
        district_query_2 = 'AND t2.districts = \'{}\''.format(district)
    query = query.format(
        date_begin, date_end, hour_begin, hour_end,
        gov_query_1, district_query_1,
        gov_query_2, district_query_2
    )
    stmt = sqlalchemy.text(query)
    with engine.connect() as conn:
        res = conn.execute(stmt)
        rows = res.all()
        district_names = [row[0] for row in rows]
        district_count = [row[1] for row in rows]
    return district_names, district_count


def get_hour_counts(date_begin, date_end, hour_begin, hour_end, gov, district):
    query = '\
SELECT sub.hour, COUNT(*) \
FROM (SELECT t1.hour \
FROM public."Table_2018" as t1 \
WHERE t1.date BETWEEN \'{0}\'::date AND \'{1}\'::date \
AND t1.hour BETWEEN {2} AND {3} \
{4} \
{5} \
UNION ALL \
SELECT t2.hour \
FROM public."Table_2019" as t2 \
WHERE t2.date BETWEEN \'{0}\'::date AND \'{1}\'::date \
AND t2.hour BETWEEN {2} AND {3}) as sub \
{6} \
{7} \
GROUP BY sub.hour \
;'
    gov_query_1 = ''
    gov_query_2 = ''
    district_query_1 = ''
    district_query_2 = ''
    if gov:
        gov_query_1 = 'AND t1.governorate = \'{}\''.format(gov)
        gov_query_2 = 'AND t2.governorate = \'{}\''.format(gov)
    if district:
        district_query_1 = 'AND t1.districts = \'{}\''.format(district)
        district_query_2 = 'AND t2.districts = \'{}\''.format(district)
    # TODO: change the parameter names to match the arguement in callback
    query = query.format(
        date_begin, date_end, hour_begin,
        hour_end, gov_query_1, district_query_1,
        gov_query_2, district_query_2
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


# NOTE: Config Panel


def date_picker_row():
    min_date = get_min_date()
    max_date = get_max_date()
    return dbc.Row(
        dbc.Col(
            children=[
                html.H5("Date"),
                dcc.DatePickerRange(
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    initial_visible_month=datetime.date(2019, 8, 5),
                    start_date=min_date,
                    end_date=max_date,
                    className='dash-bootstrap',
                    id='date-picker'
                )
            ],
        ),
    )


def hour_slider_row():
    return dbc.Row(
        dbc.Col(
            children=[
                html.H5("Hour"),
                dcc.RangeSlider(
                    min=0, max=23, step=1, value=[0, 23],
                    id='hour-slider',
                    allowCross=False,
                    marks={i: str(i) for i in range(0, 24, 2)},
                    tooltip=dict(
                        placement='bottom',
                        always_visible=True
                    ),
                ),
            ]
        )
    )


def gov_picker_row():
    return dbc.Row(
        dbc.Col(
            children=[
                html.H5("Governate"),
                dcc.Dropdown(
                    options=[
                        {'label': gov, 'value': gov} for gov in govs
                    ],
                    className='dash-bootstrap',
                    id='gov-dropdown'
                ),
            ]
        )
    )


def district_picker_row():
    # TODO: if governate is null / empty_string then return empty list
    districts = get_districts('Ahmadi')
    return dbc.Row(
        dbc.Col(
            children=[
                html.H5("District"),
                # TODO: This dropdown is updated when
                # TODO: The governorate is changed
                # TODO: To reflect the current governorate's districts
                dcc.Dropdown(
                    options=[{'label': district, 'value': district}
                             for district in districts],
                    className='dash-bootstrap',
                    id='district-dropdown'
                ),
            ]
        )
    )


def button_row():
    return dbc.Row(
        children=[
            dbc.Col(
                dbc.Button("Apply", id='apply-button')
            ),
            dbc.Col(
                dbc.Button("Clear All", id='clear-button')
            )
        ]
    )


def config_panel():
    return dbc.Col(
        sm=12,
        lg=3,
        children=[
            dbc.Row(
                children=[
                    dbc.Col(
                        children=[
                            date_picker_row(),
                            hour_slider_row(),
                            gov_picker_row(),
                            district_picker_row(),
                            button_row()
                        ],
                        style=dict(
                            border='1px solid var(--bs-body-color)',
                        ),
                    )
                ],
                class_name='p-2',
                style=dict(height='100%')
            )
        ],
    )

# NOTE: Map Boxes


def create_tabs():
    return dbc.Tabs(
        style=dict(
            borderLeft='1px solid var(--bs-body-color)',
            borderTop='1px solid var(--bs-body-color)',
            borderRight='1px solid var(--bs-body-color)',
        ),
        children=[
            dbc.Tab(label='Scatter Map', tab_id='scatter-tab'),
            dbc.Tab(label='Density Map', tab_id='density-tab')
        ],
        id='map-tabs',
    )


def update_mapbox_layout(fig):
    fig.update_layout(
        mapbox=dict(
            style='dark',
            center=dict(lat=29.311182, lon=47.993202),
            zoom=9,
            accesstoken=token,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        coloraxis=dict(
            # this sets the color scale
            colorscale='inferno',
            colorbar=dict(title=dict(text='hour')),
        ),
    )


def create_scatter_fig():
    fig = px.scatter_mapbox(lat=[1, 2, 3, 4], lon=[
                            1, 2, 3, 4], mapbox_style='open-street-map')
    update_mapbox_layout(fig)
    return fig


def create_density_fig():
    fig = px.density_mapbox(lat=[1, 2, 3, 4], lon=[
                            1, 2, 3, 4], mapbox_style='open-street-map')
    update_mapbox_layout(fig)
    return fig


def scatter_map_graph():
    return dcc.Graph(
        figure=create_scatter_fig(),
        style=dict(
            border='1px solid var(--bs-body-color)',
            borderTop='0',
            height='100%'
        ),
        id='scatter-mapbox-graph'
    )


def density_map_graph():
    return dcc.Graph(
        figure=create_density_fig(),
        style=dict(
            border='1px solid var(--bs-body-color)',
            borderTop='0',
            height='100%'
        ),
        id='density-mapbox-graph'
    )


def maps_panel():
    return dbc.Col(
        sm=12,
        lg=9,
        class_name='p-2',
        children=[
            dbc.Row(
                style=dict(height='45px'),
                children=[
                    dbc.Col(
                        children=[
                            create_tabs()
                        ],
                    )
                ],
            ),
            dbc.Row(
                style=dict(height='calc(100% - 45px)'),
                children=[
                    dbc.Col(
                        style=dict(height='100%'),
                        children=[
                            scatter_map_graph()
                        ]
                    ),
                    dbc.Col(
                        style=dict(
                            height='100%',
                        ),
                        children=[
                            density_map_graph()
                        ]
                    )
                ],
                id='maps-row',
            )
        ],
        id='maps-panel',
        style=dict(height='100%')
    )

# NOTE: top districts of # of tweets bar chart


def create_district_fig(names, count, color):
    return px.bar(
        x=names,
        y=count,
        color=color,
        title='Top 10 Districts'
    ).update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, b=10),
        hovermode='x',
        legend=dict(bgcolor='rgba(0,0,0,0)'),
        font=dict(color='#fff'),
        title=dict(x=0.5, y=0.9),
        showlegend=False
    ).update_xaxes(
        title=dict(text='Districts')
    ).update_yaxes(
        title=dict(text='# of Tweets')
    )


def district_graph():
    return dcc.Graph(
        figure=create_district_fig(None, None, None),
        style=dict(
            border='1px solid var(--bs-body-color)',
            height='100%'
        ),
        id='district-bar-graph'
    )


def district_bar_panel():
    return dbc.Col(
        sm=12,
        lg=6,
        style=dict(height='100%'),
        class_name='p-2',
        children=[
            district_graph()
        ]
    )

# NOTE: # of tweets per hour bar chart


def create_hour_bar_fig(x, y, color):
    return px.bar(
        x=x,
        y=y,
        title='# of Tweets per Hour',
        color=color
    ).update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, b=10),
        hovermode='x',
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            title=dict(text='Hour')
        ),
        font=dict(color='#fff'),
        coloraxis=dict(
            # this sets the color scale
            colorscale='inferno',
            colorbar=dict(title=dict(text='hour')),
        )
    ).update_xaxes(
        title=dict(text='Hour')
    ).update_yaxes(
        title=dict(text='# of Tweets')
    )


def hour_bar_graph():
    return dcc.Graph(
        figure=create_hour_bar_fig(None, None, None),
        style=dict(
            border='1px solid var(--bs-body-color)',
            height='100%'
        ),
        id='hour-bar-graph'
    )


def hour_bar_panel():
    return dbc.Col(
        sm=12,
        lg=6,
        style=dict(height='100%'),
        class_name='p-2',
        children=[
            hour_bar_graph()
        ]
    )

# NOTE: # of tweet in each gov pie chart


def create_gov_pie_fig(names, values):
    return px.pie(
        names=names,
        values=values,
    ).update_layout(
        dict(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, b=0, t=0),
            legend=dict(bgcolor='rgba(0,0,0,0)'),
            font=dict(color='#fff'),
        )
    )


def gov_pie_graph():
    return dcc.Graph(
        figure=create_gov_pie_fig(None, None),
        style=dict(border='1px solid var(--bs-body-color)'),
        id='gov-pie-graph'
    )


def gov_pie_chart_panel():
    return dbc.Col(
        sm=12,
        lg=6,
        class_name='p-2',
        children=[
            gov_pie_graph()
        ],
    )

# NOTE: Datatable of tweets


def create_tweets_datatable(data):
    return dash.dash_table.DataTable(
        columns=[{'name': 'tweet', 'id': 'tweet'}],
        data=data,
        style_header=dict(
            backgroundColor='var(--bs-body-bg)',
            color='var(--bs-body-color)',
            textAlign='left'
        ),
        style_data=dict(
            backgroundColor='var(--bs-body-bg)',
            color='var(--bs-body-color)',
            textAlign='left',
        ),
        style_table=dict(
            height='100%',
            overflowY='auto'
        ),
        page_size=10,
        fixed_rows=dict(headers=True),
        id='tweets-datatable'
    )


def tweet_sample_panel():
    return dbc.Col(
        sm=12,
        lg=6,
        class_name='p-2',
        style=dict(height='100%'),
        children=[
            create_tweets_datatable(None)
        ],
        id='tweet-sample-panel'
    )


@ app.callback(
    Output('district-dropdown', 'options'),

    Input('gov-dropdown', 'value'),
)
def update_districts(gov_value):
    if gov_value:
        districts = get_districts(gov_value)
        options = [{'label': district, 'value': district}
                   for district in districts]
        return options
    return []


@app.callback(
    Output('maps-row', 'children'),

    Input('map-tabs', 'active_tab'),

    State('maps-row', 'children'),
)
def change_tab(tab_id, graphs_row):
    if tab_id == 'scatter-tab':
        graphs_row[0]['props']['style']['display'] = 'block'
        graphs_row[1]['props']['style']['display'] = 'none'
    else:
        graphs_row[0]['props']['style']['display'] = 'none'
        graphs_row[1]['props']['style']['display'] = 'block'
    return graphs_row


@app.callback(
    Output('scatter-mapbox-graph', 'figure'),  # scatter fig
    Output('density-mapbox-graph', 'figure'),  # density fig
    Output('district-bar-graph', 'figure'),  # district graph
    Output('hour-bar-graph', 'figure'),  # hour graph
    Output('gov-pie-graph', 'figure'),  # gov pie chart
    Output('tweets-datatable', 'data'),  # tweets datatable

    Input('apply-button', 'n_clicks'),  # apply button

    # TODO: bug handling (if end date is before start date)
    State('date-picker', 'start_date'),  # date begin
    State('date-picker', 'end_date'),  # date end
    State('hour-slider', 'value'),  # hour values
    State('gov-dropdown', 'value'),  # governorante
    State('district-dropdown', 'value'),  # district

    State('scatter-mapbox-graph', 'figure'),
    State('district-bar-graph', 'figure'),  # district graph
    State('hour-bar-graph', 'figure'),  # hour graph
    State('gov-pie-graph', 'figure'),
)
def apply_filter_to_graphs(apply_click,
                           date_start, date_end, hours, gov, district,
                           scatter_mapbox, district_bar, hour_bar, gov_pie):

    scatter_fig = go.Figure()
    update_mapbox_layout(scatter_fig)
    density_fig = go.Figure()
    update_mapbox_layout(density_fig)
    for i in range(hours[0], hours[1] + 1):
        lat, lng, text, _ = get_data(
            date_start, date_end, i, i, gov, district)
        scatter_fig.add_trace(
            go.Scattermapbox(
                hovertext=text,
                lat=lat,
                lon=lng,
                marker=dict(
                    color=[i for _ in range(len(lat))],
                    coloraxis='coloraxis',
                    allowoverlap=True,
                    autocolorscale=True,
                ),
                name=str(i),
                showlegend=False,
            )
        )
        density_fig.add_trace(
            go.Densitymapbox(
                lat=lat,
                lon=lng,
                name='{}'.format(i),
                showlegend=False,
            )
        )

    hour_order, hours_count = get_hour_counts(
        date_start, date_end, hours[0], hours[1], gov, district)
    hour_fig = create_hour_bar_fig(hour_order, hours_count, hour_order)

    gov_names, gov_counts = get_gov_counts(
        date_start, date_end, hours[0], hours[1], gov)
    pie_fig = create_gov_pie_fig(gov_names, gov_counts)

    district_names, district_count = get_district_counts(
        date_start, date_end, hours[0], hours[1], gov, district)
    district_fig = create_district_fig(
        district_names, district_count, district_names)

    _, _, text, _ = get_data(
        date_start, date_end, hours[0], hours[1], gov, district)
    tweets = [{'tweet': tex} for tex in text]

    return scatter_fig, density_fig, district_fig, hour_fig, pie_fig, tweets


# @app.callback(
#     Output(),  # daterangepicker
#     Output(),  # hour
#     Output(),  # governornate
#     Output(),  # district

#     Input(),  # clear all button
# )
# def clear_config():
#     pass
app.layout = dbc.Container(
    # TODO: set background to the KSIR png
    fluid=True,
    style=dict(
        height='100vh - 20px',
        width='100vw - 20px',
    ),
    children=[
        dbc.Row(
            children=[
                config_panel(),
                maps_panel()
            ],
        ),
        dbc.Row(
            children=[
                district_bar_panel(),
                hour_bar_panel()
            ],
            style=dict(height='100%')
        ),
        dbc.Row(
            children=[
                gov_pie_chart_panel(),
                tweet_sample_panel(),
            ]
        )
    ]


)


app.run_server(port=3001, debug=True)
