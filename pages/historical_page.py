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


#  Config Panel


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
                        style=dict(
                            border='1px solid var(--bs-body-color)',
                            borderRadius='5px'
                        ),
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


#  Maps Panel


def create_tabs():
    return dbc.Tabs(
        id='map-tabs',
        style=dict(border='1px solid white', borderRadius='5px 5px 0 0'),
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


def scatter_map_graph(fig=None):
    if not fig:
        fig = update_mapbox_layout(px.scatter_mapbox(lat=[1], lon=[1]))

    return dcc.Graph(
        id='scatter-mapbox-graph-historical',
        style=dict(
            height='100%', border='1px solid white', borderTop='0',
            borderRadius='0 0 5px 5px'
        ),
        figure=fig,
    )


def density_map_graph():
    return dcc.Graph(
        id='density-mapbox-graph',
        style=dict(
            height='100%', border='1px solid white', borderTop='0',
            borderRadius='0 0 5px 5px'
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
                style=dict(height='40px'),
                children=dbc.Col(children=create_tabs())
            ),
            dbc.Row(
                id='maps-row-historical',
                style=dict(height='calc(100% - 40px)'),
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


# Top districts of # of tweets bar chart

def create_gov_color_map():
    return dict(
        zip(
            ['Ahmadi', 'Capital', 'Farwaniya', 'Hawalli', 'Jahra',
             'Mubarak Al-Kabeer'],
            px.colors.qualitative.Set3
        )
    )


def create_district_fig(districts, counts, govs):
    gov_color_map = create_gov_color_map()
    color_map = dict()
    for i in range(len(govs)):
        color_map[districts[i]] = gov_color_map[govs[i]]

    return px.bar(
        x=districts,
        y=counts,
        title=f'Top {len(govs)} Districts',
        color=districts,
        color_discrete_map=color_map,
        text=counts
    ).update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, b=10),
        legend=dict(bgcolor='rgba(0,0,0,0)'),
        font=dict(color='#fff'),
        title=dict(x=0.5, y=0.9, font=dict(size=30)),
        showlegend=False,
        hovermode=False,
    ).update_xaxes(
        title=dict(
            text='Districts',
            font=dict(size=20),
        ),
        tickfont=dict(size=15),
        showgrid=False
    ).update_yaxes(
        title=dict(text='# of Tweets', font=dict(size=20)),
        showgrid=False,
    )


def district_graph():
    return dcc.Graph(
        id='district-bar-graph',
        figure=create_district_fig(None, None, {}, ),
        style=dict(
            border='1px solid var(--bs-body-color)', height='100%',
            borderRadius='5px'
        ),
    )


def district_bar_panel():
    return dbc.Col(
        sm=12,
        lg=6,
        style=dict(height='100%'),
        class_name='p-2 order-sm-2 order-lg-1',
        children=district_graph()
    )


# # of tweets per hour bar chart


def create_hour_bar_fig(x, y):
    return go.Figure(
        data=[
            go.Bar(
                name=gov, x=x[gov], y=y[gov],
                marker=dict(
                    color=x[gov], line=dict(color=x[gov],
                                            colorscale=['#fff', '#000'])
                ),
                hovertemplate=gov + '<br>%{y} Tweets',
            )
            for gov in x
        ]
    ).update_traces(
        dict(width=0.8),
    ).update_layout(
        barmode='stack',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, b=10),
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
        title=dict(text='# of Tweets per Hour',
                   x=0.5, y=0.9, font=dict(size=30)),
    ).update_xaxes(
        title=dict(
            text='Hour',
            font=dict(size=20)
        ),
        tickfont=dict(size=20),
    ).update_yaxes(
        title=dict(text='# of Tweets', font=dict(size=20)),
    )


def hour_bar_graph():
    return dcc.Graph(
        id='hour-bar-graph',
        style=dict(
            border='1px solid var(--bs-body-color)',
            borderRadius='5px',
            height='100%'
        ),
        figure=create_hour_bar_fig({':)': [i for i in range(24)]},
                                   {':)': [i * i for i in range(24)]}),
    )


def hour_bar_panel():
    return dbc.Col(
        sm=12,
        lg=6,
        style=dict(height='100%'),
        class_name='p-2 order-sm-1 order-lg-2',
        children=hour_bar_graph()
    )


# # of tweet in each gov pie chart


def create_gov_pie_fig(names, values):
    return px.pie(
        names=names,
        values=values,
        color=names,
        color_discrete_map=create_gov_color_map(),
        title='Percentage of Tweets Per Governorate',
    ).update_traces(
        hovertemplate='%{value} Tweets'
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
        style=dict(border='1px solid var(--bs-body-color)', borderRadius='5px'),
        figure=create_gov_pie_fig(None, None),
    )


def gov_pie_chart_panel():
    return dbc.Col(
        sm=12,
        lg=6,
        class_name='p-2',
        children=gov_pie_graph(),
    )


# Datatable of tweets


def create_tweets_datatable(data):
    return dash.dash_table.DataTable(
        id='tweets-datatable',
        columns=[dict(name='Tweets', id='tweets')],
        data=data,
        style_header=dict(
            backgroundColor='#111',
            color='var(--bs-body-color)',
            textAlign='left',
            fontSize=20,
        ),
        style_data=dict(
            backgroundColor='#111',
            color='var(--bs-body-color)',
            textAlign='left',
            fontSize=16,
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


# Callback Helper methods

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


def update_hour_fig(date_start, date_end, hours, govs, districts):
    total_hour_order = dict()
    total_hour_count = dict()
    iterable = districts if districts else govs if govs else ['All']

    for iterab in iterable:
        gov, district = None, None
        if districts:
            district, gov = [iterab], None
        elif govs:
            district, gov = None, [iterab]
        hour_order, hour_count = sql_library.get_hour_counts(date_start,
                                                             date_end,
                                                             hours[0], hours[1],
                                                             gov, district)
        total_hour_order[iterab] = hour_order
        total_hour_count[iterab] = hour_count

    return create_hour_bar_fig(total_hour_order, total_hour_count)


def create_scatter_fig(custom_text, i, lat, lng):
    return go.Scattermapbox(
        text=custom_text,
        hovertemplate='%{text}',
        lat=lat,
        lon=lng,
        name='',
        showlegend=False,
        marker=dict(
            color=[i for _ in range(len(lat))],
            coloraxis='coloraxis',
            opacity=0.7,
            size=14
        ),
        uid=1,
    )


def create_density_trace(custom_text, lat, lng):
    return go.Densitymapbox(
        text=custom_text,
        hovertemplate='%{text}',
        lat=lat,
        lon=lng,
        name='',
        showlegend=False,
        colorscale=px.colors.sequential.Blackbody_r,
    )


# Callbacks

@callback(
    Output('district-dropdown', 'options'),

    Input('gov-dropdown', 'value'),
)
def update_districts(gov_values):
    if not gov_values:
        return []

    districts = sql_library.get_districts(gov_values)

    options = [
        dict(label=district, value=district)
        for district in sorted(districts)
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

    hour_fig = update_hour_fig(date_start, date_end, hours, govs, districts)

    gov_names, gov_counts = sql_library.get_gov_counts(date_start, date_end,
                                                       hours[0], hours[1], govs)

    pie_fig = create_gov_pie_fig(gov_names, gov_counts)

    district_names, district_count = sql_library.get_district_counts(
        date_start, date_end, hours[0], hours[1], govs, districts)

    district_gov_names = sql_library.get_gov_names(district_names)

    district_fig = create_district_fig(
        district_names, district_count,
        [district_gov_names[dis] for dis in district_names])

    _, _, text, hour, _, _ = sql_library.get_data(date_start, date_end,
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
def update_mapbox_graphs(_fig, date_start, date_end, hours, govs, districts):
    scatter_fig, density_fig = go.Figure(), go.Figure()

    update_mapbox_layout(scatter_fig)
    update_mapbox_layout(density_fig)

    for i in range(24):
        lat, lng, point_districts = [-1], [-1], [-1]
        custom_text = None

        if hours[0] <= i <= hours[1]:
            lat, lng, text, _, date, point_districts = sql_library.get_data(
                date_start, date_end, i, i, govs, districts)

            custom_text = [f'{da}<br>{tex}' for da, tex in zip(date, text)]

            density_fig.add_trace(create_density_trace(custom_text, lat, lng))

        scatter_fig.add_trace(create_scatter_fig(custom_text, i, lat, lng))

    graph = dbc.Spinner(scatter_map_graph(scatter_fig))

    return graph, density_fig


@callback(
    Output('date-picker', 'start_date'),  # date begin
    Output('date-picker', 'end_date'),  # date end
    Output('hour-slider', 'value'),  # hour values
    Output('gov-dropdown', 'value'),  # governorante
    Output('district-dropdown', 'value'),  # district
    Output('clear-button', 'n_clicks'),

    Input('clear-button', 'n_clicks'),  # clear all button
)
def clear_config(_n_clicks):
    if _n_clicks:
        return (sql_library.get_min_date(), sql_library.get_max_date(),
                [0, 23], None, None, None)
    else:
        raise dash.exceptions.PreventUpdate


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
