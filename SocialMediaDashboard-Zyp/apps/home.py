# Import packages -----------------------------------
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import calendar
# from dateutil import parser
import gspread
import urllib.request, json

import plotly.express as px
import plotly.graph_objects as go
# from jupyter_dash import JupyterDash
from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
# from dash_extensions import Lottie
from dash import dash_table

# Create elements of the webpage ----------------------------------
homePageJumbotron = html.Div(children=[
    html.H5("Welcome to the Zyp Art Gallery Social Media Dashboard!", className="display-3"),
    html.P("By Kunal Ajaykumar Jeshang", className="lead"),
    html.Hr(className="my-2"),
    html.P("This application was developed with the intent to help Zyp Art Gallery derive & visualize social media insights from Facebook & Instagram data."),
], className="p-3 bg-light rounded-3");

image_path = "http://static1.squarespace.com/static/5ef69a36a33bc717a29b5f2e/t/5f171341b1185c55715415c0/1595347784126/Zyp+logo_large.jpg?format=1500w";

logoImage = html.Img(src=image_path, style={'height':'85%', 'width':'70%'});

# Page Layout --------------------------------------------------------

# Structure:
homePageStructure = [
    html.Br(),
    dbc.Row(children=[
        dbc.Col(children=homePageJumbotron),
        dbc.Col(children=logoImage)
    ])
];

# Finalizing the layout:
homePageLayout = dbc.Container(children=homePageStructure, fluid=True);