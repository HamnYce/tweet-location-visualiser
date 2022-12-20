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


def data_container(title, content):
    return dbc.Container(
        fluid=True,
        children=[
            dbc.Card(
                children=[
                    dbc.CardHeader(children=title),
                    dbc.CardBody(children=content)
                ]
            )
        ],
    )


def total_data_row():
    return dbc.Row(children=dbc.Col(id='total-data-col'))


def total_user_row():
    return dbc.Row(children=dbc.Col(id='total-user-col'))


def top_districts_row():
    return dbc.Row(children=dbc.Col(id='top-districts-col'))


def overview_panel():
    return dbc.Col(
        xl=3,
        sm=12,
        class_name='p-2',
        style=dict(height='100%'),
        children=[
            dbc.Container(
                fluid=True,
                class_name='p-2',
                style=dict(
                    border='1px solid white',
                    height='100%'
                ),
                children=[
                    html.H3('Overview', style=dict(textAlign='center'), ),
                    total_data_row(),
                    total_user_row(),
                    top_districts_row()
                ]
            )
        ]
    )


def create_tabs():
    return dbc.Tabs(
        id='map-tabs',
        style=dict(border='1px solid white'),
        active_tab='scatter-tab',
        children=[
            dbc.Tab(label='Scatter Map', tab_id='scatter-tab'),
            dbc.Tab(label='Density Map', tab_id='density-tab')
        ],
    )


def update_mapbox_layout(fig):
    return fig.update_layout(
        mapbox=dict(
            style='dark',
            center=dict(lat=29.311172, lon=47.993202),
            zoom=7,
            accesstoken=token,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        coloraxis=dict(
            # this sets the color scale
            colorscale=px.colors.sequential.Viridis_r,
            colorbar=dict(title=dict(text='hour')),
        ),
    )


def scatter_map_graph():
    return dcc.Graph(
        id='scatter-map-graph-live',
        style=dict(height='100%', border='1px solid white', borderTop='0'),
        figure=update_mapbox_layout(px.scatter_mapbox(lat=[1], lon=[1])),
    )


def density_map_graph():
    return dcc.Graph(
        id='density-map-graph',
        style=dict(height='100%', border='1px solid white', borderTop='0'),
        figure=update_mapbox_layout(px.density_mapbox(lat=[1], lon=[1]), ),
    )


def maps_panel():
    return dbc.Col(
        class_name='p-2',
        style=dict(height='100%'),
        children=[
            dbc.Row(
                style=dict(height='40px'),
                children=[
                    dbc.Col(style=dict(height='100%'), children=create_tabs())
                ]
            ),
            dbc.Row(
                id='maps-row',
                style=dict(height='calc(100% - 40px)'),
                children=[
                    dbc.Col(
                        id='scatter-map-col',
                        style=dict(height='100%'),
                        children=dbc.Spinner(scatter_map_graph()),
                    ),
                    dbc.Col(
                        style=dict(height='100%'),
                        children=dbc.Spinner(density_map_graph())
                    )
                ]
            )
        ]
    )

def create_hour_bar_fig(x, y):
    return px.bar(
        x=x,
        y=y,
        title='# of Tweets per Hour',
        color=x,
    ).update_traces(
        hovertemplate='%{y}'
    ).update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, b=10),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            title=dict(text='Hour')
        ),
        font=dict(color='#fff'),
        coloraxis=dict(
            # this sets the color
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
        nticks=24,
    ).update_yaxes(
        title=dict(text='# of Tweets', font=dict(size=10)),
    )


def hour_bar_graph():
    return dcc.Graph(
        id='bar-graph',
        style=dict(height='100%'),
        figure=create_hour_bar_fig(
            [x for x in range(20)],
            [x * x for x in range(20)]
        )
    )


def bar_panel():
    return dbc.Col(
        class_name='p-2',
        style=dict(
            height='100%',
            border='1px solid white'
        ),
        children=hour_bar_graph()
    )


@callback(
    Output('maps-row', 'children'),

    Input('map-tabs', 'active_tab'),

    State('maps-row', 'children'),
)
def change_tab(tab_id, graphs_row):
    s_tab = tab_id == 'scatter-tab'
    display_1, display_2 = ('block', 'none') if s_tab else ('none', 'block')

    graphs_row[0]['props']['style']['display'] = display_1
    graphs_row[1]['props']['style']['display'] = display_2
    return graphs_row


@callback(
    Output('total-data-col', 'children'),
    Output('total-user-col', 'children'),
    Output('top-districts-col', 'children'),
    Output('scatter-map-graph-live', 'figure'),
    Output('density-map-graph', 'figure'),
    Output('bar-graph', 'figure'),

    Input('interval', 'n_intervals'),

)
def update_data(_interval):
    lat, lng, date, hour, districts, texts, user_id = sql_library.get_random_sample()

    df = pd.DataFrame(dict(
        user_id=user_id,
        lat=lat,
        lng=lng,
        hour=hour,
        date=date,
        text=texts,
        districts=districts
    )
    ).dropna()

    # Overview Info (Total Data, Total Users)
    total_data_children = data_container(title='Total # of Records',
                                         content=df.shape[0])
    total_user_children = data_container(title='Total # of Users',
                                         content=df.loc[:, 'user_id'].nunique())

    # Top District Info
    top_districts = df.loc[:, 'districts'].value_counts()[:3]
    names, amounts = top_districts.index, top_districts.values
    top_districts_children = [html.H4('Top Districts:')]
    top_districts_children += [data_container(title=name, content=amount)
                               for name, amount in zip(names, amounts)]

    # Emptying Scatter Figure (because dash is weird about scatter_mapbox)
    empty_scatter_mapbox = go.Figure().update_layout(
        dict(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, showticklabels=False, visible=False),
            yaxis=dict(showgrid=False, showticklabels=False, visible=False),
        )
    )

    # Updating Density Figure
    density_mapbox = px.density_mapbox(
        data_frame=df,
        lat='lat',
        lon='lng',
    ).update_traces(
        customdata=df['text'],
        hovertemplate='%{customdata}'
    )

    update_mapbox_layout(density_mapbox)

    density_mapbox.update_layout(
        dict(
            coloraxis=dict(
                # this sets the color scale
                colorscale=px.colors.sequential.Blackbody_r,
            ),
        )
    )

    # hourly bar chart
    hours = df.loc[:, 'hour'].value_counts()
    hour_index, hour_values = hours.index, hours.values

    # to fix barchart x-axis
    for i in range(24):
        if i not in hour_index:
            hour_index += 0
            hour_values += 0

    bar_graph = create_hour_bar_fig(hour_index, hour_values
                                    ).update_traces(dict(width=0.8))

    # Output variables
    return (total_data_children, total_user_children, top_districts_children,
            empty_scatter_mapbox, density_mapbox, bar_graph)


@callback(
    Output('scatter-map-col', 'children'),

    Input('scatter-map-graph-live', 'figure'),
)
def update_map(_scatter_map):
    # TODO: this can be optimised but will
    # depend on how we will be getting samples
    lat, lng, date, hour, districts, texts, user_id = sql_library.get_random_sample()

    df = pd.DataFrame(
        dict(
            lat=lat,
            lng=lng,
            date=date,
            text=texts,
            hour=hour,
        )
    ).dropna()

    scatter_map = px.scatter_mapbox(
        data_frame=df,
        lat='lat',
        lon='lng',
        color='hour',
        range_color=[0, 23],
    ).update_traces(
        marker=dict(
            opacity=0.7,
            size=14
        ),
        customdata=df['text'],
        hovertemplate='%{customdata}'
    )

    update_mapbox_layout(scatter_map)

    graph = dbc.Spinner(
        dcc.Graph(
            figure=scatter_map,
            style=dict(
                border='1px solid var(--bs-body-color)',
                borderTop='0px',
                height='100%'
            ),
            id='scatter-map-graph-live',
        )
    )
    return graph


# NOTE: Current update delay is 20 seconds
layout = dbc.Container(
    fluid=True,
    children=[
        dcc.Interval(id='interval', interval=20000),
        dbc.Row(
            style=dict(height='100%'),
            children=[
                overview_panel(),
                dbc.Col(
                    xl=9,
                    sm=12,
                    style=dict(height='100%'),
                    children=[
                        dbc.Row(
                            children=maps_panel()
                        ),
                        dbc.Row(
                            class_name='p-2',
                            children=bar_panel()
                        )
                    ]
                ),
            ]
        )
    ]
)
