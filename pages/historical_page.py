import datetime

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, callback, dcc, html
import app_modules.sql_library as sql_library

dash.register_page(__name__, path='/historical')

token = open('.mapbox_token').read()
px.set_mapbox_access_token(token)


# NOTE: Config Panel


def date_picker_row():
    min_date = sql_library.get_min_date()
    max_date = sql_library.get_max_date()

    return dbc.Row(
        dbc.Col(
            children=[
                html.H5("Date"),
                dcc.DatePickerRange(
                    id='date-picker',
                    min_date_allowed=min_date,
                    max_date_allowed=max_date,
                    initial_visible_month=datetime.date(2019, 8, 5),
                    start_date=min_date,
                    end_date=max_date,
                    className='dash-bootstrap',
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
                    id='hour-slider',
                    min=0, max=23, step=1, value=[0, 23],
                    allowCross=False,
                    marks={i: str(i) for i in range(0, 24, 2)},
                    tooltip=dict(placement='bottom', always_visible=True),
                ),
            ]
        )
    )


def gov_picker_row():
    return dbc.Row(
        dbc.Col(
            children=[
                html.H5("Governorate"),
                dcc.Dropdown(
                    id='gov-dropdown',
                    className='dash-bootstrap',
                    multi=True,
                    options=[
                        dict(label=gov, value=gov)
                        for gov in sql_library.get_distinct_govs()
                    ]
                ),
            ]
        )
    )


def district_picker_row():
    return dbc.Row(
        dbc.Col(
            children=[
                html.H5("District"),
                dcc.Dropdown(
                    id='district-dropdown',
                    className='dash-bootstrap',
                    multi=True,
                ),
            ]
        )
    )


def button_row():
    return dbc.Row(
        children=[
            dbc.Col(dbc.Button("Apply", id='apply-button')),
            dbc.Col(dbc.Button("Clear All", id='clear-button'))
        ]
    )


def config_panel():
    return dbc.Col(
        sm=12,
        lg=3,
        children=[
            dbc.Row(
                class_name='p-2',
                style=dict(height='100%'),
                children=[
                    dbc.Col(
                        style=dict(border='1px solid var(--bs-body-color)'),
                        children=[
                            date_picker_row(),
                            hour_slider_row(),
                            gov_picker_row(),
                            district_picker_row(),
                            button_row()
                        ],
                    )
                ],
            )
        ],
    )


# NOTE: Map Boxes


def create_tabs():
    return dbc.Tabs(
        id='map-tabs',
        style=dict(
            borderLeft='1px solid var(--bs-body-color)',
            borderTop='1px solid var(--bs-body-color)',
            borderRight='1px solid var(--bs-body-color)',
        ),
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
        id='scatter-mapbox-graph-historical',
        style=dict(
            border='1px solid var(--bs-body-color)',
            borderTop='0',
            height='100%'
        ),
        figure=update_mapbox_layout(px.scatter_mapbox(lat=[1], lon=[1])),
    )


def density_map_graph():
    return dcc.Graph(
        id='density-mapbox-graph',
        style=dict(
            border='1px solid var(--bs-body-color)',
            borderTop='0',
            height='100%'
        ),
        figure=update_mapbox_layout(px.density_mapbox(lat=[1], lon=[1])),
    )


def maps_panel():
    return dbc.Col(
        id='maps-panel',
        sm=12,
        lg=9,
        class_name='p-2',
        style=dict(height='100%', ),
        children=[
            dbc.Row(
                style=dict(height='45px'),
                children=dbc.Col(children=create_tabs())
            ),
            dbc.Row(
                id='maps-row-historical',
                style=dict(height='calc(100% - 45px)'),
                children=[
                    dbc.Col(
                        id='scatter-map-col-historical',
                        style=dict(height='100%'),
                        children=dbc.Spinner(scatter_map_graph()),
                    ),
                    dbc.Col(
                        style=dict(height='100%'),
                        children=dbc.Spinner(density_map_graph())
                    )
                ],
            )
        ],
    )


# NOTE: top districts of # of tweets bar chart


def create_district_fig(names, count):
    return px.bar(
        x=names,
        y=count,
        title='Top 10 Districts',
        color_discrete_sequence=['#ffd']
    ).update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, b=10),
        hovermode='x',
        legend=dict(bgcolor='rgba(0,0,0,0)'),
        font=dict(color='#fff'),
        title=dict(x=0.5, y=0.9, font=dict(size=30)),
        showlegend=False
    ).update_xaxes(
        title=dict(
            text='Districts',
            font=dict(size=20),
        ),
        tickfont=dict(size=20),
    ).update_yaxes(
        title=dict(text='# of Tweets', font=dict(size=20))
    )


def district_graph():
    return dcc.Graph(
        id='district-bar-graph',
        figure=create_district_fig(None, None),
        style=dict(border='1px solid var(--bs-body-color)', height='100%'),
    )


def district_bar_panel():
    return dbc.Col(
        sm=12,
        lg=6,
        style=dict(height='100%'),
        class_name='p-2',
        children=district_graph()
    )


# NOTE: # of tweets per hour bar chart


def create_hour_bar_fig(x, y, color=None):
    color = x if not color else color
    return px.bar(
        x=x,
        y=y,
        title='# of Tweets per Hour',
        color=color,
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
        title=dict(x=0.5, y=0.9, font=dict(size=30)),
    ).update_xaxes(
        title=dict(
            text='Hour',
            font=dict(size=20)
        ),
        tickfont=dict(size=20),
    ).update_yaxes(
        title=dict(text='# of Tweets', font=dict(size=20))
    )


def hour_bar_graph():
    return dcc.Graph(
        id='hour-bar-graph',
        style=dict(
            border='1px solid var(--bs-body-color)',
            height='100%'
        ),
        figure=create_hour_bar_fig(None, None),
    )


def hour_bar_panel():
    return dbc.Col(
        sm=12,
        lg=6,
        style=dict(height='100%'),
        class_name='p-2',
        children=hour_bar_graph()
    )


# NOTE: # of tweet in each gov pie chart


def create_gov_pie_fig(names, values):
    return px.pie(
        names=names,
        values=values,
        color_discrete_sequence=px.colors.qualitative.Set3,
        title='Percentage of Tweets Per Governorate'
    ).update_layout(
        dict(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, b=0, t=55),
            legend=dict(
                bgcolor='rgba(0,0,0,0)',
                font=dict(size=20)),
            font=dict(color='#fff', size=20),
        )
    )


def gov_pie_graph():
    return dcc.Graph(
        id='gov-pie-graph',
        style=dict(border='1px solid var(--bs-body-color)'),
        figure=create_gov_pie_fig(None, None),
    )


def gov_pie_chart_panel():
    return dbc.Col(
        sm=12,
        lg=6,
        class_name='p-2',
        children=gov_pie_graph(),
    )


# NOTE: Datatable of tweets


def create_tweets_datatable(data):
    return dash.dash_table.DataTable(
        id='tweets-datatable',
        columns=[dict(name='Tweets', id='tweets')],
        data=data,
        style_header=dict(
            backgroundColor='#111',
            color='var(--bs-body-color)',
            textAlign='left',
            fontSize=20
        ),
        style_data=dict(
            backgroundColor='#111',
            color='var(--bs-body-color)',
            textAlign='left',
            fontSize=16
        ),
        style_table=dict(height='100%', overflowY='auto'),
        page_size=10,
        fixed_rows=dict(headers=True),
    )


def tweet_sample_panel():
    return dbc.Col(
        id='tweet-sample-panel',
        sm=12,
        lg=6,
        class_name='p-2',
        style=dict(height='100%'),
        children=create_tweets_datatable(None)
    )


@callback(
    Output('district-dropdown', 'options'),

    Input('gov-dropdown', 'value'),
)
def update_districts(gov_values):
    if not gov_values:
        return []

    districts = []
    for gov_value in gov_values:
        districts += sql_library.get_districts(gov_value)

    options = [
        dict(label=district, value=district)
        for district in districts
    ]
    return options


@callback(
    Output('maps-row-historical', 'children'),

    Input('map-tabs', 'active_tab'),

    State('maps-row-historical', 'children'),
)
def change_tab(tab_id, graphs_row):
    s_tab = tab_id == 'scatter-tab'
    display_1, display_2 = ('block', 'none') if s_tab else ('none', 'block')

    graphs_row[0]['props']['style']['display'] = display_1
    graphs_row[1]['props']['style']['display'] = display_2
    return graphs_row


def empty_scatter_fig():
    return go.Figure().update_layout(
        dict(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                visible=False,
            ),
            yaxis=dict(
                showgrid=False,
                showticklabels=False,
                visible=False,
            ),
        )
    )

@callback(
    Output('scatter-mapbox-graph-historical', 'figure'),  # scatter fig
    Output('district-bar-graph', 'figure'),  # district graph
    Output('hour-bar-graph', 'figure'),  # hour graph
    Output('gov-pie-graph', 'figure'),  # gov pie chart
    Output('tweets-datatable', 'data'),  # tweets datatable

    Input('apply-button', 'n_clicks'),  # apply button

    State('date-picker', 'start_date'),  # date begin
    State('date-picker', 'end_date'),  # date end
    State('hour-slider', 'value'),  # hour values
    State('gov-dropdown', 'value'),  # governorate
    State('district-dropdown', 'value'),  # district
)
def apply_filter_to_graphs(_click, date_start, date_end, hours, govs,
                           districts):
    scatter_fig = empty_scatter_fig()

    hour_order, hour_count = sql_library.get_hour_counts(date_start, date_end,
                                                         hours[0], hours[1],
                                                         govs, districts)

    # to fix barchart x-axis
    for i in range(24):
        if i not in hour_order:
            hour_order.append(i)
            hour_count.append(0)

    hour_fig = create_hour_bar_fig(hour_order, hour_count
                               ).update_traces(dict(width=0.8))

    gov_names, gov_counts = sql_library.get_gov_counts(date_start, date_end,
                                                       hours[0], hours[1], govs)

    pie_fig = create_gov_pie_fig(gov_names, gov_counts)

    district_names, district_count = sql_library.get_district_counts(
        date_start, date_end, hours[0], hours[1], govs, districts)

    district_fig = create_district_fig(
        district_names, district_count)

    _, _, text, hour, _ = sql_library.get_data(date_start, date_end,
                                               hours[0], hours[1],
                                               govs, districts)

    tweets = [dict(tweets=tex) for tex in text]

    return scatter_fig, district_fig, hour_fig, pie_fig, tweets


@callback(
    Output('scatter-map-col-historical', 'children'),
    Output('density-mapbox-graph', 'figure'),  # density fig

    Input('scatter-mapbox-graph-historical', 'figure'),

    State('date-picker', 'start_date'),  # date begin
    State('date-picker', 'end_date'),  # date end
    State('hour-slider', 'value'),  # hour values
    State('gov-dropdown', 'value'),  # governorate
    State('district-dropdown', 'value'),  # district

)
def update_graph(_fig, date_start, date_end, hours, gov, district):
    scatter_fig = go.Figure()
    density_fig = go.Figure()

    update_mapbox_layout(scatter_fig)
    update_mapbox_layout(density_fig)

    for i in range(24):
        lat, lng = [-1], [-1]
        custom_text = None

        if hours[0] <= i <= hours[1]:
            lat, lng, text, _, date = sql_library.get_data(
                date_start, date_end, i, i, gov, district)

            custom_text = [
                f'Date: {da}<br>Tweet:{tex}'
                for da, tex in zip(date, text)
            ]

            density_fig.add_trace(
                go.Densitymapbox(
                    lat=lat,
                    lon=lng,
                    name=str(i),
                    showlegend=False,
                )
            )

        scatter_fig.add_trace(
            go.Scattermapbox(
                text=custom_text,
                hovertemplate='%{text}',
                lat=lat,
                lon=lng,
                marker=dict(
                    color=[i for _ in range(len(lat))],
                    coloraxis='coloraxis',
                    opacity=0.7,
                    size=14
                ),
                name=str(i),
                showlegend=False,
                uid=1
            )
        )

    graph = dbc.Spinner(
        dcc.Graph(
            id='scatter-mapbox-graph-historical',
            style=dict(
                border='1px solid var(--bs-body-color)',
                borderTop='0',
                height='100%'
            ),
            figure=scatter_fig,
        ),
    )

    return graph, density_fig


@callback(
    Output('date-picker', 'start_date'),  # date begin
    Output('date-picker', 'end_date'),  # date end
    Output('hour-slider', 'value'),  # hour values
    Output('gov-dropdown', 'value'),  # governorante
    Output('district-dropdown', 'value'),  # district
    Output('clear-button', 'n_clicks'),  # clear all button

    Input('clear-button', 'n_clicks'),  # clear all button
)
def clear_config(_n_clicks):
    return (sql_library.get_min_date(), sql_library.get_max_date(),
            [0, 23], None, None, 0)


layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(children=[config_panel(), maps_panel()]),
        dbc.Row(
            style=dict(height='100%'),
            children=[district_bar_panel(), hour_bar_panel()],
        ),
        dbc.Row(children=[gov_pie_chart_panel(), tweet_sample_panel()])
    ]

)
