import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.express as px
import sys
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from dash import callback_context
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
KISR_LOGO = "assets/KISR-Logo.png"
BACKGROUND = "assets/background.png"

colors = {
    'background': '#555555',
    'text': 'Black'
}

# Plotly mapbox public token
token = open(".mapbox_token").read()
#px.set_mapbox_access_token(open(".mapbox_token").read())

#df=pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")
df=pd.read_csv("Sample Data_twitter_Districts.csv")
total_data=df['data_id'].count()
print(total_data)

cnt = 0
visited = []
for i in range(0, len(df['user_id'])):
    if df['user_id'][i] not in visited:
        visited.append(df['user_id'][i])
        cnt += 1
print("No.of.unique values :", cnt)

df1 = pd.DataFrame(df.groupby("hour")["data_id"].count())
df1=df1.reset_index()
df2 = pd.DataFrame(df.groupby("districts")["data_id"].count())
df2=df2.reset_index()

col=df2["data_id"]
max_index = col.idxmax()

#top 3 districts
max=df2.nlargest(3,'data_id')
top1=max.iloc[0,0]
top2=max.iloc[1,0]
top3=max.iloc[2,0]
top4=max.iloc[0,1]
top5=max.iloc[1,1]
top6=max.iloc[2,1]

#maxmum data in districs
maxi=df2['data_id'].max()

layout_map=dict(
    hovermode='closest',
    showlegend=False,
    mapbox=dict(
        accesstoken=token,
        bearing=0,
        center=dict(
            lat=29.4,
            lon=47.9,
                ),
        pitch=0,
        zoom=7.9,
        style='dark'
                ),

    plot_bgcolor="#111111",
    paper_bgcolor="#111111",
    font=dict(color="#FFFFFF"),
        #coloraxis_colorbar=dict(tickvals=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]),
)

def Total_Data_Users_Card():
    """
    :return: A Div containing dashboard title & descriptions.
    """
    return dbc.Card(color="light",outline=True,style={'color': colors['text'],"margin-top":"10px"},
        id="description-card",
        children=[
            dbc.CardHeader(html.H5("Total Data")),
            dbc.CardBody([
                html.H5(total_data, className="card-title"),
                ]),
            dbc.CardHeader(html.H5("Total Users")),
            dbc.CardBody([
                html.H5(cnt, className="card-title"),
                ]),
        ],
    ),

def mapgraph():
    trace1 = go.Scattermapbox(
        lat=df.Y,
        lon=df.X,
        mode="markers",
        visible=True,
        marker=dict(size=12,cmax=0,cmin=24,color=df.hour,colorbar=dict(title="hour",tick0=0,dtick=1 ),colorscale="Viridis",reversescale=True,),
        text=df.text,
        hoverinfo='text',
        )

    trace2=go.Densitymapbox(
        lat=df.Y,
        lon=df.X,
        radius=10,
        visible=False,
        colorscale="RdYlBu",
    )
    
    fig = go.Figure(data=[trace1,trace2],layout=layout_map)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},height=800)
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                font=dict(
                    family="courier",
                    size=20
                ),
                direction="left",
                pad={"t": 40,"l":30},
                x=0.001,
                xanchor="left",
                y=1,
                yanchor="top",
                bgcolor=None,
                buttons=list([
                    dict(args=[{"visible": [ True, False]}],label="DefaultMap",method="update"),
                    dict(args=[{"visible": [False, True]}],label="Heatmap",method="update")
                ]),
            ),
        ]
    )
    return fig

def display_heatMap():
    fig = px.density_mapbox(df, lat='Y', lon='X', radius=16,
            hover_name="place_name",
            hover_data={'X':False,'Y':False,'hour':False,'text':True},
            color_continuous_scale=px.colors.sequential.YlOrRd[::-1],
            height=800,
            range_color=[0,23],
            zoom=7.9)
    fig.update_layout(mapbox_style="dark",
                mapbox_accesstoken=token,
                plot_bgcolor="#111111",
                paper_bgcolor="#111111",
                font=dict(color="#FFFFFF"),
                coloraxis_colorbar=dict(tickvals=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]),
            )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig


def bar():
    fig = px.bar(df1,x="hour",y="data_id",
    color_continuous_scale=px.colors.sequential.Viridis[::-1],
    color="hour",
    barmode="relative",
    height=470,
    title="Title: Bar Chart",
    hover_data={'hour':False,'data_id':False},)
    #fig = px.histogram(df1,x="hour",y="data_id",color_discrete_sequence=px.colors.sequential.Viridis,color="hour")
    fig.update_layout(
            plot_bgcolor="#111111",paper_bgcolor="#111111",
            font=dict(color="#FFFFFF"),
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            xaxis_zeroline=False,
            yaxis_zeroline=False,
            xaxis_visible=True,
            yaxis_visible=False,
            xaxis_title=None,
            yaxis_title=None,
            coloraxis_showscale=False,
            coloraxis_colorbar=dict(tickvals=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]),
            uniformtext=dict(mode="hide", minsize=10),
            xaxis = dict(
                tickmode = 'linear',
                tick0 = 0.0,
                dtick = 1,
                )
            )
    fig.update_traces(texttemplate='%{y:.2s}', textposition='outside',)
    return fig

app.layout = dbc.Container(
    [
        html.Div(

            children=[
            # the first row has 3 cols
                dbc.Row([
                    dbc.Col(html.Img(src=KISR_LOGO,height="60"),md=2),
                    dbc.Col(html.H4("Kuwait Map with Tweets"),md=8,align="center",
                            style={"textAlign": "center","color":"white","font-family": "courier"}),
                    dbc.Col(children=[
                            dbc.Button("Advance",
                                #href='/advance.py',
                                id="advance-button",
                                color="link",
                                size="lg",
                                style={"color":"white","font-family":"courier"},
                                className="mr-2",
                                n_clicks=0),
                            html.Span(id="advance-output", style={"verticalAlign": "middle"}),
                            dbc.Button("Menu",color="link",size="lg",
                                       style={"color":"white","font-family":"courier"}, className="mr-2", n_clicks=0),

                    ],md=2,)]),

                #for the grey line
                html.Hr(),

                # the second row that has 2 col
                dbc.Row(
                        [
                        #the first col
                        dbc.Col(children=[
                            #html.Div(Total_Data_Users_Card()),
                            html.Hr(),
                            html.H3("TOTAL DATA", style={"textAlign": "left","color":"white","font-family": "courier",'font-size':'30px',}),
                            html.Hr(style={"color":"#126180","background-color": "#126180",'width':'200px','margin-left':'3px'}),
                            html.H3(total_data,
                                    style={"textAlign": "left",
                                            "color":"white",
                                            "font-family": "courier",
                                            "border": "2px solid #126180",
                                            "border-radius": "5px",
                                            "padding":"10px",
                                            "background-color": "#126180",
                                            "width":"fit-content"
                                            }),
                            html.Hr(style={"color":"white","background-color": "black"}),
                            html.H3("TOTAL USERS", style={"textAlign": "left","color":"white","font-family": "courier",'font-size':'30px'}),
                            html.Hr(style={"color":"#126180","background-color": "#126180",'width':'200px','margin-left':'3px'}),
                            #html.Hr(style={"color":"white","background-color": "#126180"}),
                            html.H3(cnt,
                                    style={"textAlign": "left",
                                            "color":"white",
                                            "font-family": "courier",
                                            "border": "2px solid #126180",
                                            "border-radius": "5px",
                                            "padding":"10px",
                                            "background-color": "#126180",
                                            "width":"fit-content"
                                            }),
                            html.Hr(style={"color":"white","background-color": "black"}),
                            html.Hr(style={"color":"white","background-color": "black"}),
                            html.Hr(style={"color":"white","background-color": "black"}),
                            html.Hr(style={"color":"white","background-color": "#126180"}),
                            html.Hr(style={"color":"white","background-color": "black"}),
                            html.Hr(style={"color":"white","background-color": "black"}),

                            html.H3("TOP Districts", style={"textAlign": "left","color":"white","font-family": "courier",'font-size':'30px',}),
                            html.Hr(style={"color":"white","background-color": "black"}),

                            html.H3(top1,
                                    style={"textAlign": "left",
                                            "color":"white",
                                            "font-family": "courier",
                                            "border": "2px solid #126180",
                                            "border-radius": "5px",
                                            "padding":"10px",
                                            "background-color": "#126180",
                                            "width":"fit-content",

                                            }),
                            html.Hr(style={"color":"#126180","background-color": "#126180",'width':'200px','margin-left':'3px'}),
                            html.H3(top4, style={"textAlign": "left","color":"white","font-family": "courier",'font-size':'50px'}),
                            html.Hr(style={"color":"white","background-color": "black"}),
                            html.H3(top2,
                                    style={"textAlign": "left",
                                            "color":"white",
                                            "font-family": "courier",
                                            "border": "2px solid #126180",
                                            "border-radius": "5px",
                                            "padding":"10px",
                                            "background-color": "#126180",
                                            "width":"fit-content"
                                            }),
                            html.Hr(style={"color":"#126180","background-color": "#126180",'width':'200px','margin-left':'3px'}),
                            html.H3(top5, style={"textAlign": "left","color":"white","font-family": "courier",'font-size':'44px'}),
                            html.Hr(style={"color":"white","background-color": "black"}),
                            html.H3(top3,
                                    style={"textAlign": "left",
                                            "color":"white",
                                            "font-family": "courier",
                                            "border": "2px solid #126180",
                                            "border-radius": "5px",
                                            "padding":"10px",
                                            "background-color": "#126180",
                                            "width":"fit-content"
                                            }),
                            html.Hr(style={"color":"#126180","background-color": "#126180",'width':'200px','margin-left':'3px'}),
                            html.H3(top6, style={"textAlign": "left","color":"white","font-family": "courier",'font-size':'39px'}),
                            html.Hr(style={"color":"white","background-color": "black"}),
                            html.Hr(style={"color":"white","background-color": "black"}),
                            html.Hr(style={"color":"white","background-color": "#126180"}),

                            ],
                            md=3,
                            style={"border":"1px",
                                    "border-style":"solid",
                                    "border-radius": "5px",
                                    "border-width": "1px",
                                    "border-color": "#DEDEDE",
                                    "border-width":"5px",
                                    "box-shadow":"0px 0px 20px #888888",
                                    }),
                        #th second col
                        dbc.Col([
                            #the first row

                            dbc.Row([
                                        dcc.Graph(id="mapgraph",figure=mapgraph(),style={'width': '100%', 'height': '100%'}),
                                        ],style={"border":"1px",
                                                    "border-style":"solid",
                                                    "border-radius": "5px",
                                                    "border-color": "#DEDEDE",
                                                    "border-width":"5px",
                                                    "margin-left":"1px",
                                                    #"margin-right":"1px",
                                                    "box-shadow":"0px 0px 20px #888888",
                                                    }),

                                #the second row
                            dbc.Row([
                                dbc.Col(dcc.Graph(id="bar-chart",figure=bar()),
                                    )],style={"border":"1px",
                                                "border-style":"solid",
                                                "border-radius": "5px",
                                                "border-color": "#DEDEDE",
                                                "border-width":"5px",
                                                "margin-top":"15px",
                                                "margin-left":"1px",
                                                #"margin-right":"1px",
                                                "box-shadow":"0px 0px 20px #888888"})
                                ], md=9,
                            ),
                        ],
                    ),
                #for the grey line
                html.Hr(),

                dbc.Row([
                    dbc.Col(
                        html.Div(children=[
                        dbc.Button("About Us",color="link", className="mr-2",size="lg", n_clicks=0,style={"color":"white","font-family":"courier"}),
                        ]), md=4,
                    ),
                    dbc.Col(
                        html.Div("Col2"),md=4,
                            ),
                    dbc.Col(
                        html.Div(style={"verticalAlign": "middle"},
                            children=[
                                dbc.Button("Contact Us",color="link",size="lg", className="mr-2", n_clicks=0,style={"color":"white","font-family":"courier"}),
                                    ]),
                            md=4,
                            align="right",
                            style={"padding":"10px",'left':'22%'}
                            ),
                        ]),
                #for the grey line
                html.Hr(),

                dbc.Row([
                    dbc.Col(
                        html.P("Copyright: Kuwait Institute for Scientific Research © 2021. All rights reserved", style={'text-align':'center','font-size':'35','color':'white',"font-family":"courier"}),
                            ),
                ]),

            ],
        ),
    ],
    fluid=True, style={'color': colors['text'],'background-image': 'url("/assets/Background.png")','background-size': 'cover',  "width": "100%", "padding":" 35px"}
)

if __name__ == "__main__":
    app.run_server(debug=True,port=8300)

#this is inside the update_layout
#plot_bgcolor="#323130", for the dark area of right scale
#paper_bgcolor="#323130", for the text


# @app.callback(
#      Output("advance-output", "children"),
#      [Input("advance-button", "n_clicks")]
# #      Input('regularmapsketchButton', 'n_clicks')
#      )
# def on_button_click(n_clicks):
#     if n_clicks is None:
#         raise PreventUpdate
#     else:
#         script_fn = 'advance.py'
#         exec(open(script_fn).read())


#this is inside the choropleth_mapbox: color="Bergeron",for the colored color_continuous_scale
                                        # html.Button('HeatMap', id='heatmapsketchButton',n_clicks=0,style={"color":"white",
                                        # "font-family": "courier",
                                        # "border": "2px solid #126180",
                                        # "border-radius": "5px",
                                        # "method":"restyle",
                                        # "padding":"10px",
                                        # "background-color": "#126180","margin":"10px"}),
                                        # html.Button('Default', id='regularmapsketchButton',n_clicks=0,style={"color":"white","color":"white",
                                        # "font-family": "courier",
                                        # "border": "2px solid #126180",
                                        # "border-radius": "5px",
                                        # "padding":"10px",
                                        # "background-color": "#126180",}),
    # fig.update_coloraxes(
    #     #colorbar_nticks=0,
    #     cmin=0,
    #     cmax=23,
    #     colorbar_tick0=0,
    #     colorbar_dtick=1,
    #      #colorbar=dict(
    #         # title="hour",
    #          #tick0=0,
    #          #nticks=0
    #             #),
    #  )


    # fig.update_layout(mapbox_style="dark",
    #         mapbox_accesstoken=token,
    #         plot_bgcolor="#111111",
    #         paper_bgcolor="#111111",
    #         font=dict(color="#FFFFFF"),
    #         coloraxis_colorbar=dict(tickvals=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]),
    #     )

    #
    # def update_graph(heatmapsketchButton,regularmapsketchButton):
    #     changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    #     if 'heatmapsketchButton' in changed_id:
    #         #print("HeatMap= " + value)
    #         #sys.stdout.flush()
    #         return display_heatMap()
    #     elif 'regularmapsketchButton' in changed_id:
    #         #print("RegMap= " + value)
    #         #sys.stdout.flush()
    #         return mapgraph()
    #     else:
    #         return mapgraph()


    #df2=df.groupby("hour").count()
    #df2.get_group("0")

    #hours = df.loc[(df["hour"] == "0"),["text"]]
    #print(hours.head())

    # updatemenus=list([
    #     dict(
    #  # for each button I specify which dictionaries of my data list I want to visualize. Remember I have 7 different
    #  # types of storms but I have 8 options: the first will show all of them, while from the second to the last option, only
    #  # one type at the time will be shown on the map
    #      buttons=list([
    #         dict(label = 'HeatMap',
    #              method = 'update',
    #              args = [{'visible': [True]}]),
    #         dict(label = 'DefaultMap',
    #              method = 'update',
    #              args = [{'visible': [True]}]),
    #     ]),
    # # direction where the drop-down expands when opened
    #     direction = 'down',
    #     # positional arguments
    #     x = 0.01,
    #     xanchor = 'left',
    #     y = 0.99,
    #     yanchor = 'bottom',
    #     # fonts and border
    #     bgcolor = '#000000',
    #     bordercolor = '#FFFFFF',
    #     font = dict(size=11)
    #     )
    #     ]),

    # fig = go.Figure(go.Scattermapbox(df, lat="Y", lon="X",size="data_id",size_max=10,hover_name="place_name",
    # hover_data={'X':False,'Y':False,'hour':False,'data_id':False,'text':True},
    # color_continuous_scale=px.colors.sequential.Viridis[::-1],
    # color="hour",
    # height=800,
    # range_color=[0,23],
    # zoom=7.9))
    # fig.update_layout(mapbox_style="dark",
    #         mapbox_accesstoken=token,
    #         plot_bgcolor="#111111",
    #         paper_bgcolor="#111111",
    #         font=dict(color="#FFFFFF"),
    #         coloraxis_colorbar=dict(tickvals=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]),
    # )
    # fig.update_layout(
    #     updatemenus=[
    #         dict(
    #             buttons=list([
    #                 dict(
    #                     args=["type", "Scattermapbox"],
    #                     label="Scatter",
    #                     method="restyle"
    #                 ),
    #                 dict(
    #                     args=["type", "heatmap"],
    #                     label="Heatmap",
    #                     method="restyle"
    #                 )
    #             ]),
    #             direction="down",
    #             pad={"r": 10, "t": 10},
    #             showactive=True,
    #             x=0.1,
    #             xanchor="left",
    #             y=1.1,
    #             yanchor="top"
    #         ),
    #     ]
    # )

        # fig = px.scatter_mapbox(df, lat="Y", lon="X",size="data_id",size_max=10,
        #      hover_name="place_name",
        #      hover_data={'X':False,'Y':False,'hour':False,'data_id':False,'text':True},
        #      color_continuous_scale=px.colors.sequential.Viridis[::-1],
        #      color="hour",
        #      height=800,
        #      range_color=[0,23],
        #      zoom=7.9)
