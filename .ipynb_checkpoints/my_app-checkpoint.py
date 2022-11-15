#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly import colors
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


# In[2]:


df = pd.read_csv('types.csv').drop(columns=['Unnamed: 0', 'level_0'])


# In[4]:


df.loc[:, 'date'] = df.loc[:,'date'].astype(np.datetime64)


# In[5]:


def min_date_str(time_series):
    return str(time_series.min()).split()[0]
    
def max_date_str(time_series):
    return str(time_series.max()).split()[0]


# In[6]:


gov_options = [{'label':gov,'value':gov} for gov in df.governorate.unique()]


# In[7]:


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


# In[25]:


app.layout = dbc.Container(
    children=[
        dbc.Row(
            children=[
                dbc.Col(
                       children=[
                           dbc.Container(
                               dcc.DatePickerRange(id='date_picker',
                                                   min_date_allowed=min_date_str(df.date),
                                                   max_date_allowed=max_date_str(df.date),
                                                   start_date=min_date_str(df.date),
                                                   end_date=max_date_str(df.date)
                                                   ),
                               style={'border':'1px solid black'},
                           ),
                           dbc.Container(
                               dcc.Dropdown(id='gov_dropdown',
                                           options=gov_options,
                                           value=gov_options[0]['label']),
                               style={'border':'1px solid black'},
                           )
                       ],
                       width=3,
                   ),
                dbc.Col(
                   html.Div(
                       style={'border':'1px solid black'},
                       id='graph_container',
                       children=[
                           dcc.Graph(id='scatter_map')
                       ],
                   ),
               )
            ]
        )
    ]
)


# In[9]:


@app.callback(
    Output('scatter_map','figure'),
    Input('gov_dropdown','value'),
    Input('date_picker', 'start_date'),
    Input('date_picker', 'end_date'))
def filter_scatter(gov, start_date, end_date):
    dff = df[df['governorate'] == gov]
    if start_date is not None and end_date is not None:
        dff = dff[dff['date'] >= start_date]
        dff = dff[dff['date'] <= end_date]
        
    fig =  px.scatter_mapbox(data_frame=dff, lat='lat', lon='lng',
                             mapbox_style='open-street-map')
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0, pad=0))
    return {'data': fig.data, 'layout':fig.layout}


# In[ ]:


if __name__ == '__main__':
    app.run_server(port=3001)

