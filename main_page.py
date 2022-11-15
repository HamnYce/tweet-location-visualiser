import itertools
from pathlib import WindowsPath

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from plotly import colors

px.set_mapbox_access_token(open('.mapbox_token').read())

df = pd.read_csv('types3.csv')
df.loc[:, 'date'] = df.loc[:, 'date'].astype(np.datetime64)

palette = itertools.cycle(px.colors.qualitative.Safe)

area_names = df['area'].unique()
area_df_dict = {area: df[df['area'] == area] for area in area_names}
area_color = {area: next(palette) for area in df.loc[:, 'area'].unique()}


def calc_top_10_areas():
    area_count_series = df.loc[:, 'area'].value_counts(
    ).sort_values(ascending=False)
    return area_count_series[:10]


top_10_area_series = calc_top_10_areas()

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
            base_component_col('Total Data', df.shape[0]),
            base_component_col('Total Users', df['user_id'].unique().shape[0])
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
                    dbc.Checklist(
                        options=[
                            dict(label='Dark Mode', value=1,)
                        ], switch=True, value=[1]
                    ),
                    dbc.Button("Reset Scatter Graph",
                               id='reset-scatter', n_clicks=0)
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
            misc_row(),
            html.Hr(style=dict(height=2, width='100%')),
        ]
    )


def scatter_mapbox_graph():
    return dcc.Graph(
        id='scatter-mapbox',
        style=dict(height='100%', border='1px solid black'),
        figure=px.scatter_mapbox(
            data_frame=df,
            lat='lat',
            lon='lng',
            center=dict(lat=df['lat'].mean(), lon=df['lng'].mean()),
            zoom=7,
            mapbox_style='dark',
            hover_name='text',
            hover_data=dict(lat=False, lng=False, area=False),
            color='area',
            color_discrete_map=area_color,
        ).update_layout(dict(
            margin=dict(t=0, b=0, l=0, r=0),
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                bgcolor='rgba(0,0,0,0)',
            ),
            font=dict(color='#fff')
        ))
    )


def create_bar_chart_fig():
    return px.bar(
        x=top_10_area_series.index,
        y=top_10_area_series.values,
        text=top_10_area_series.index,
        hover_name=top_10_area_series.index,
        color=top_10_area_series.index,
        color_discrete_map=area_color,
    ).update_layout(
        dict(
            title=dict(text='Top 10 Areas'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, b=0, t=10),
            hovermode='x',
            legend=dict(bgcolor='rgba(0,0,0,0)'),
            font=dict(color='#fff'),
        )
    ).update_traces(
        patch=dict(hovertemplate=None, hoverinfo='text', textangle=90)
    ).update_xaxes(
        showticklabels=False, title_text='Area'
    )


def bar_chart_graph():
    return dcc.Graph(
        id='bar-chart',
        style=dict(height='100%'),
        figure=create_bar_chart_fig()
    )


def graphs_col():
    return dbc.Col(
        width=9,
        children=[
            dbc.Row(
                style={'height': '60%'},
                children=[
                    dbc.Col(
                        children=[
                            scatter_mapbox_graph()
                        ]
                    )
                ]
            ),
            dcc.Interval(id='bar-chart-interval', interval=5000),
            dbc.Row(
                style=dict(height='calc(40% - 10px)'),
                children=[
                    dbc.Col(
                        children=[
                            bar_chart_graph()
                        ]
                    )
                ]
            )
        ]
    )


@app.callback(
    Output('scatter-mapbox', 'figure'),
    Output('bar-chart', 'figure'),
    Output('bar-chart', 'clickData'),
    Output('reset-scatter', 'n_clicks'),
    Input('bar-chart-interval', 'n_intervals'),
    Input('bar-chart', 'clickData'),
    Input('reset-scatter', 'n_clicks'),
    State('bar-chart', 'figure'),
    State('scatter-mapbox', 'figure')
)
def realtime_updates(n, clickData, n_clicks, bar_fig, scatter_fig):
    global df, top_10_area_series
    inputs = dash.callback_context.inputs
    print(inputs)
    if inputs['reset-scatter.n_clicks']:
        print(scatter_fig['data'][0].keys())
        for i in range(len(scatter_fig['data'])):
            scatter_fig['data'][i]['visible'] = True
    elif inputs['bar-chart.clickData']:
        area_name = clickData['points'][0]['x']
        for i in range(len(scatter_fig['data'])):
            scatter_fig['data'][i]['visible'] = scatter_fig['data'][i]['name'] == area_name
    elif inputs['bar-chart-interval.n_intervals']:
        df = pd.concat([df, pd.read_csv('inter_types.csv')])
        top_10_area_series = calc_top_10_areas()
        bar_fig = create_bar_chart_fig()

    return scatter_fig, bar_fig, None, 0


# TODO: add a date picker callback, or a scrollbar for year (maybe for the advanced page?)

# DONE: at the end add a callback that refreshes the data with new data

# DONE: have same colours for both bar chart and scatter graph
# DONE: callback function input from bar click and update scatter graph with only that area toggled
app.layout = dbc.Container(
    # TODO: set nice background
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
