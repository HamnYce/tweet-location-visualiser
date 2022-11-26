import random

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
from flask_sqlalchemy import SQLAlchemy
from dash.dependencies import Input, Output, State

token = open('.mapbox_token').read()
day_archived_df = pd.read_csv('datasets/new_types.csv', parse_dates=['date'])
custom_color_scale = 'inferno'

# this can all be done in SQL
top_10_area_series = day_archived_df.loc[:, 'area'].value_counts()[:10]
hour_counts = day_archived_df.loc[:, 'hour'].value_counts()
hour_df = day_archived_df.groupby('hour')
hours_df_list = [hour_df.get_group(name=i) for i in range(24)]

scatter_order_lis = [0, 23, 1, 22, 2, 21, 3, 20, 4, 19, 5,
                     18, 6, 17, 7, 16, 8, 15, 9, 14, 10, 13, 11, 12]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# TODO: define functions to get specific data from the dataframe?
# TODO:  or maybe load specific data into a dataframe before hand


def base_component_col(name, info):
    return dbc.Col(
        children=[
            html.B(name),
            html.P(children=[
                '{}'.format(info)
            ],
                style={'width': 'auto', },
            )
        ]
    )


def overview_row():
    return dbc.Row(
        id='total-data-row',
        children=[
            html.H3(children='Overview', className='text-center'),
            base_component_col('Total Data', day_archived_df.shape[0]),
            base_component_col(
                'Total Users', day_archived_df['user_id'].unique().shape[0])
            # room for changing this to be user settable sample size (random or other)
        ]
    )


def top_districts_row():
    return dbc.Row(
        children=[
            html.H3(children='Top Districts', className='text-center'),
            base_component_col(
                top_10_area_series.index[0], top_10_area_series.values[0]),
            base_component_col(
                top_10_area_series.index[1], top_10_area_series.values[0]),
            base_component_col(
                top_10_area_series.index[2], top_10_area_series.values[3])
        ]
    )


def misc_row():
    return dbc.Row(
        children=[
            dbc.Col(
                children=[
                    html.H3(children='Misc. Options', className='text-center'),
                    # dbc.Checklist(
                    #     options=[
                    #         dict(label='Dark Mode', value=1,)
                    #     ], switch=True, value=[1]
                    # ),
                    dbc.Button("Reset Graph",
                               id='reset-maps-button', n_clicks=0),
                ]
            )

        ]
    )


def stats_col():
    return dbc.Col(
        style={'border': '1px solid white', },
        width=3,
        children=[
            overview_row(),
            html.Hr(style=dict(height=2, width='100%')),
            top_districts_row(),
            html.Hr(style=dict(height=2, width='100%')),
            # misc_row(),
            # html.Hr(style=dict(height=2, width='100%')),
        ]
    )


def update_mapbox_fig(fig):
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
            colorscale=custom_color_scale,
            colorbar=dict(title=dict(text='hour')),
        ),
    )


def create_density_mapbox_fig():
    fig = go.Figure()
    update_mapbox_fig(fig)
    fig.update_layout(
        coloraxis=dict(
            colorscale=plotly.colors.sequential.deep_r,
            colorbar=dict(title=dict(text='intensity'))
        )
    )
    for i in range(24):
        fig.add_trace(
            go.Densitymapbox(
                hovertext=hours_df_list[i]['text'],
                lat=hours_df_list[i]['lat'],
                lon=hours_df_list[i]['lng'],
                name='{}'.format(i),
                coloraxis='coloraxis',
                showlegend=False,
                radius=15,
            )
        )
    return fig


def create_scatter_mapbox_fig():
    fig = go.Figure()
    update_mapbox_fig(fig)
    for i in scatter_order_lis:
        fig.add_trace(
            go.Scattermapbox(
                hovertext=hours_df_list[i]['text'],
                lat=hours_df_list[i]['lat'],
                lon=hours_df_list[i]['lng'],
                name='{}'.format(i),
                marker=dict(
                    color=[i for _ in range(len(hours_df_list[i]['lat']))],
                    coloraxis='coloraxis'
                ),
                showlegend=False,
            )
        )
    return fig


def create_bar_chart_fig():
    return px.bar(
        x=hour_counts.index,
        y=hour_counts.values,
        color=hour_counts.index,
        color_continuous_scale=custom_color_scale,
        text=hour_counts.values,
    ).update_layout(
        dict(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, b=0, t=0),
            hovermode='x',
            legend=dict(bgcolor='rgba(0,0,0,0)'),
            font=dict(color='#fff'),
        )
    ).update_traces(
        patch=dict(hovertemplate=None, hoverinfo='text',
                   textposition='outside')
    ).update_xaxes(
        showticklabels=True, title_text='Hour of the Day', nticks=48
    ).update_yaxes(
        showticklabels=False, title_text='', nticks=0
    )


def density_mapbox_graph():
    return dcc.Graph(
        id='density-mapbox',
        style={
            'height': 'calc(100% - 6px)',
            'border': '1px solid var(--bs-body-color)',
        },
        figure=create_density_mapbox_fig()
    )


def scatter_mapbox_graph():
    return dcc.Graph(
        id='scatter-mapbox',
        style={
            'height': 'calc(100% - 6px)',
            'border': '1px solid var(--bs-body-color)',
        },
        figure=create_scatter_mapbox_fig()
    )


def bar_chart_graph():
    return dcc.Graph(
        id='bar-chart',
        style=dict(height='calc(100% - 4px)',
                   border='1px solid var(--bs-body-color)'),
        figure=create_bar_chart_fig()
    )


def graphs_col():
    return dbc.Col(
        width=9,
        style=dict(height='100%'),
        children=[
            dbc.Row(
                style=dict(height='50px'),
                children=[
                    dbc.Col(
                        style=dict(height='100%'),
                        children=[
                            dbc.Tabs(
                                style=dict(border='0'),
                                children=[
                                    dbc.Tab(
                                        label='Scatter Map',
                                        tab_id='scatter-tab'
                                    ),
                                    dbc.Tab(
                                        label='Density Map',
                                        tab_id='density-tab',
                                    )
                                ],
                                id='map-tabs'
                            ),
                        ],
                    )

                ]
            ),
            dbc.Row(
                style=dict(height='calc(60% - 50px)'),
                children=[
                    dbc.Col(
                        style=dict(height='100%'),
                        children=[
                            dbc.Row(
                                children=[
                                    dbc.Col(
                                        scatter_mapbox_graph(),
                                        style=dict(height='100%'),
                                        id='scatter-graph-col'
                                    ),
                                    dbc.Col(
                                        density_mapbox_graph(),
                                        style=dict(
                                            height='100%',
                                            display='none',
                                        ),
                                        id='density-graph-col'
                                    ),
                                ],
                                style=dict(height='100%'),
                                id='map-graphs-row'
                            ),
                        ]
                    )
                ],
            ),
            dbc.Row(
                style=dict(height='40%'),
                align='end',
                children=[
                    dbc.Col(
                        style=dict(height='100%'),
                        children=[
                            bar_chart_graph()
                        ]
                    )
                ],
            ),
            dcc.Interval(id='data-update-interval', interval=10000),
            dcc.Interval(id='plot-update-interval', interval=5000)
        ]
    )


@app.callback(
    Output('map-graphs-row', 'children'),

    Input('map-tabs', 'active_tab'),

    State('map-graphs-row', 'children'),
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
    # TODO: also update content in misc row
    Output('scatter-mapbox', 'figure'),  # scatter figure output
    Output('density-mapbox', 'figure'),  # density figure output
    Output('bar-chart', 'figure'),  # bar chart output for live data
    Output('data-update-interval', 'n_intervals'),  # live updates interval

    Input('plot-update-interval', 'n_intervals'),

    State('scatter-mapbox', 'figure'),  # scatter figure
    State('density-mapbox', 'figure'),  # density figure
    State('bar-chart', 'figure'),
)
def realtime_update(plot_update_interval,
                    scatter_fig, density_fig, bar_fig):
    inputs = dash.callback_context.inputs
    print(inputs)
    # will read from a csv that is exported from a script outside
    return scatter_fig, density_fig, bar_fig, 0


# DONE: at the end add a callback that refreshes the data with new data
# DONE: have same colours for both bar chart and scatter graph
# DONE: callback function input from bar click and update scatter graph with only that area toggled
app.layout = dbc.Container(
    # TODO: set background to the KSIR png
    style=dict(padding=5),
    fluid=True,
    children=[
        dbc.Row(
            style=dict(
                height='calc(100vh - 10px)',
                width='calc(100vw - 10px)'
            ),
            children=[
                stats_col(),
                graphs_col()
            ]
        )
    ]


)


app.run_server(port=3001, debug=True)
