from random import randint

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import callback, Input, Output, State, dcc, html
import app_modules.sql_library as sql_library

dash.register_page(__name__, path='/')

token = open('.mapbox_token').read()
px.set_mapbox_access_token(token)


# TODO: refactor to dbc.Card (card_header, card_body)


def data_container(title, content):
    return dbc.Container(
        fluid=True,
        children=[
            dbc.Card(
                children=[
                    dbc.CardHeader(
                        title,
                    ),
                    dbc.CardBody(
                        content,
                    )
                ]
            )
        ],
    )


def total_data_row():
    return dbc.Row(
        children=[
            dbc.Col(
                id='total-data-col'
            )
        ]
    )


def total_user_row():
    return dbc.Row(
        children=[
            dbc.Col(
                id='total-user-col'
            )
        ]
    )


def top_districts_row():
    return dbc.Row(
        children=[
            dbc.Col(
                children=[
                ],
                id='top-districts-col'
            )
        ]
    )


def overview_panel():
    return dbc.Col(
        xl=3,
        sm=12,
        class_name='p-2',
        style=dict(
            height='100%',
        ),
        children=[
            dbc.Container(
                fluid=True,
                class_name='p-2',
                style=dict(
                    border='1px solid white',
                    height='100%',
                ),
                children=[
                    html.H3('Overview', style=dict(textAlign='center')),
                    total_data_row(),
                    total_user_row(),
                    top_districts_row()
                ]
            )
        ]
    )


def create_tabs():
    return dbc.Tabs(
        style=dict(
            border='1px solid white',
            borderBottom='0'
        ),
        children=[
            dbc.Tab(label='Scatter Map', tab_id='scatter-tab'),
            dbc.Tab(label='Density Map', tab_id='density-tab')
        ],
        id='map-tabs',
        active_tab='scatter-tab'
    )


def update_mapbox_layout(fig):
    return fig.update_layout(
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
            colorscale=px.colors.sequential.Viridis_r,
            colorbar=dict(title=dict(text='hour')),
        ),
        legend=dict(

        )
    )


def create_scatter_map_fig():
    return px.scatter_mapbox(
        lat=[1, 2, 3, 4, 5],
        lon=[1, 2, 3, 4, 5],
        mapbox_style='open-street-map'
    )


def scatter_map_graph():
    return dcc.Graph(
        figure=update_mapbox_layout(
            px.scatter_mapbox(lat=[1], lon=[1]),
        ),
        style=dict(
            height='100%',
            border='1px solid white',
            borderTop='0'
        ),
        id='scatter-map-graph-live'
    )


def create_density_map_fig():
    return px.density_mapbox(
        lat=[1, 2, 3, 4, 5],
        lon=[1, 2, 3, 4, 5],
        mapbox_style='open-street-map'
    )


def density_map_graph():
    return dcc.Graph(
        figure=update_mapbox_layout(
            px.density_mapbox(lat=[1], lon=[1]),
        ),
        style=dict(
            height='100%',
            border='1px solid white',
            borderTop='0'
        ),
        id='density-map-graph'
    )


def maps_panel():
    return dbc.Col(
        class_name='p-2',
        style=dict(
            height='100%',
        ),
        children=[
            dbc.Row(
                style=dict(height='40px'),
                children=[
                    dbc.Col(
                        style=dict(
                            height='100%',
                        ),
                        children=[
                            create_tabs(),
                        ]
                    )
                ]
            ),
            dbc.Row(
                style=dict(
                    height='calc(100% - 40px)',
                ),
                children=[
                    dbc.Col(
                        style=dict(
                            height='100%',
                        ),
                        children=[
                            scatter_map_graph(),
                        ],
                        id='scatter-map-col'
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
                id='maps-row'
            )
        ]
    )


def create_hour_bar_fig(x, y, color):
    return px.bar(
        x=x,
        y=y,
        title='# of Tweets per Hour',
        color=x,
        barmode='group'
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
            colorscale=px.colors.sequential.Viridis_r,
            colorbar=dict(title=dict(text='hour')),
        ),
        title=dict(x=0.5, y=0.9, font=dict(size=15)),
    ).update_xaxes(
        title=dict(
            text='Hour',
            font=dict(size=10)
        ),
        tickfont=dict(size=10),
        range=[-0.5, 23.5],
        fixedrange=True,
        nticks=24,
    ).update_yaxes(
        title=dict(text='# of Tweets', font=dict(size=10)),
        fixedrange=True,
    )


def hour_bar_graph():
    return dcc.Graph(
        style=dict(height='100%'),
        figure=create_hour_bar_fig(
            [x for x in range(20)],
            [x * x for x in range(20)],
            None
        ),
        id='bar-graph'
    )


def bar_panel():
    return dbc.Col(
        class_name='p-2',
        style=dict(
            height='100%',
            border='1px solid white'
        ),

        children=[
            hour_bar_graph()
        ]
    )


@callback(
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


@callback(
    Output('total-data-col', 'children'),
    Output('total-user-col', 'children'),
    Output('top-districts-col', 'children'),
    Output('scatter-map-graph-live', 'figure'),
    Output('density-map-graph', 'figure'),
    Output('bar-graph', 'figure'),

    Input('interval', 'n_intervals'),

    # State('scatter-map-graph-live', 'figure'),
    # State('density-map-graph', 'figure'),
    # State('bar-graph', 'figure')
)
def update_data(_interval):
    lat, lng, hour, districts, user_id = sql_library.get_random_sample()

    df = pd.DataFrame({
        'user_id': user_id,
        'lat': lat,
        'lng': lng,
        'hour': hour,
        'districts': districts
    }).dropna()

    data_amount = df.shape[0]
    user_amount = df.loc[:, 'user_id'].nunique()
    total_data_children = data_container(
        title='Total # of Records', content=data_amount)
    total_user_children = data_container(
        title='Total # of Users', content=user_amount)

    top_districts = df.value_counts(['districts'])
    names, amounts = top_districts.index[:3], top_districts.values[:3]
    top_districts_children = [html.H4('Top Districts:')] + [data_container(
        title=name, content=amount) for name, amount in zip(names, amounts)]

    scatter_map = go.Figure().update_layout(
        dict(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=False,
                # showline=False,
                showticklabels=False,
                visible=False,
            ),
            yaxis=dict(
                showgrid=False,
                # showline=False,
                showticklabels=False,
                visible=False,
            ),
        )
    )

    density_map = px.density_mapbox(
        data_frame=df,
        lat='lat',
        lon='lng',
    )

    update_mapbox_layout(density_map)
    density_map.update_layout(
        dict(
            coloraxis=dict(
                # this sets the color scale
                colorscale=px.colors.sequential.Blackbody_r,
            ),
        )
    )

    hours = df.value_counts(['hour'])

    hour_names = [hour[0] for hour in hours.index]

    bar_graph = create_hour_bar_fig(
        hour_names, hours.values, None
    ).update_traces(
        dict(
            width=0.8
        )
    )

    ret_val = (
        total_data_children, total_user_children, top_districts_children,
        scatter_map, density_map, bar_graph
    )
    return ret_val


@callback(
    Output('scatter-map-col', 'children'),

    Input('scatter-map-graph-live', 'figure'),
)
def update_map(_scatter_map):
    # TODO: this can be optimised but will
    # depend on how we will be getting samples
    lat, lng, hour, _, _ = sql_library.get_random_sample()
    df = pd.DataFrame({
        'lat': lat,
        'lng': lng,
        'hour': hour,
    }).dropna()

    scatter_map = px.scatter_mapbox(
        data_frame=df,
        lat='lat',
        lon='lng',
        color='hour',
        range_color=[0, 23],
    )
    update_mapbox_layout(scatter_map)

    graph = dcc.Graph(
        figure=scatter_map,
        style=dict(
            border='1px solid var(--bs-body-color)',
            borderTop='0',
            height='100%'
        ),
        id='scatter-map-graph-live',
    )
    return graph


layout = dbc.Container(
    fluid=True,
    style=dict(
    ),
    children=[
        dcc.Interval(id='interval', interval=5000),
        dbc.Row(
            style=dict(height='100%'),
            children=[
                overview_panel(),
                dbc.Col(
                    xl=9,
                    sm=12,
                    style=dict(
                        height='100%'
                    ),
                    children=[
                        dbc.Row(
                            style=dict(
                            ),
                            children=[
                                maps_panel()
                            ]
                        ),
                        dbc.Row(
                            class_name='p-2',
                            style=dict(
                            ),
                            children=[
                                bar_panel()
                            ]
                        )
                    ]
                ),
            ]
        )
    ]
)
