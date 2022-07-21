# Import packages -----------------------------------
import pandas as pd
import numpy as np
from datetime import date, datetime
import calendar
# from dateutil import parser
import gspread

import plotly.express as px
import plotly.graph_objects as go
# from jupyter_dash import JupyterDash
# import dash
import dash_bootstrap_components as dbc
from dash import Dash
from dash import dcc
from dash import html
from dash import callback
from dash.dependencies import Input, Output, State
# from dash_extensions import Lottie
from dash import dash_table
import dash_auth

# import sys

# sys.path.append(".")
from app import app
from app import server
from apps import home
from apps import FB_Section_Posts
from apps import FB_Section_Page
from apps import FB_Section_Audience_AgeGender
from apps import FB_Section_Audience_Country
from apps import FB_Section_Audience_TimeOfDay
from apps import FB_Section_Audience_CanadianCity
from apps import IG_Section_Posts
from apps import IG_Section_Page
from apps import IG_Section_Audience_AgeGender
from apps import IG_Section_Audience_Country
from apps import IG_Section_Audience_CanadianCity
from apps import IG_Section_Audience_TimeOfDay
from assets.googleService import getDataframe_listOfLists, getDataframe

# Instantiate dashboard application --------------------------------------
# app = Dash(__name__, external_stylesheets=[dbc.themes.LUX]);
# app = Dash(__name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True);

# Setup dashboard application basic authentication -----------------------------
sheet = "DashAppLogins";
worksheet = "DashAppLogins";
# df = getDataframe(sheet, worksheet);
listOfLists = getDataframe_listOfLists(sheet, worksheet);
df = pd.DataFrame(listOfLists[1:], columns=listOfLists[0])

authDict = {};
for i in df.index:
    authDict[df.loc[i, "Username"]] = str(df.loc[i, "Password"]);

auth = dash_auth.BasicAuth(
    app,
    # {'bugsbunny': 'topsecret',
    #  'pajaroloco': 'unsecreto'}
    authDict
)

# Create constant elements of webpages -----------------------------------

# Facebook navigation bar section:
facebookNavigationSection = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Posts", href="/FB_Section_Posts"),
        dbc.DropdownMenuItem("Page", href="/FB_Section_Page"),
        dbc.DropdownMenuItem("Audience", header=True),
        dbc.DropdownMenuItem("Age & Gender", href="/FB_Section_Audience_AgeGender"),
        dbc.DropdownMenuItem("Country", href="/FB_Section_Audience_Country"),
        dbc.DropdownMenuItem("Canadian City", href="/FB_Section_Audience_CanadianCity"),
        dbc.DropdownMenuItem("Time of Day", href="/FB_Section_Audience_TimeOfDay"), 
    ],
    nav=True,
    in_navbar=True,
    label="Facebook",
);

# Instagram navigation bar section:
instagramNavigationSection = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("Posts", href="/IG_Section_Posts"),
        dbc.DropdownMenuItem("Page", href="/IG_Section_Page"),
        dbc.DropdownMenuItem("Audience", header=True),
        dbc.DropdownMenuItem("Age & Gender", href="/IG_Section_Audience_AgeGender"),
        dbc.DropdownMenuItem("Country", href="/IG_Section_Audience_Country"),
        dbc.DropdownMenuItem("Canadian City", href="/IG_Section_Audience_CanadianCity"),
        dbc.DropdownMenuItem("Time of Day", href="/IG_Section_Audience_TimeOfDay")
    ],
    nav=True,
    in_navbar=True,
    label="Instagram",
);

# Navigation bar:
navigationBar = dbc.NavbarSimple(children=[
        facebookNavigationSection,
        instagramNavigationSection
    ],
    brand="Zyp Art Gallery Social Media Dashboard",
    brand_href="/",
    color="primary",
    dark=True,
);

# Create constant page layout --------------------------------------------
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    navigationBar,
    html.Div(id="page-content", children=[])
]);

# Callbacks --------------------------------------------------------------
@callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    # Home
    if pathname == "/":
        return home.homePageLayout;
    # Facebook
    if pathname == '/FB_Section_Posts':
        return FB_Section_Posts.postSectionlayout;
    if pathname == "/FB_Section_Page":
        return FB_Section_Page.pageSectionLayout;
    if pathname == "/FB_Section_Audience_AgeGender":
        return FB_Section_Audience_AgeGender.ageGenderLayout;
    if pathname == "/FB_Section_Audience_Country":
        return FB_Section_Audience_Country.countryLayout;
    if pathname == "/FB_Section_Audience_CanadianCity":
        return FB_Section_Audience_CanadianCity.canadianCityLayout;
    if pathname == "/FB_Section_Audience_TimeOfDay":
        return FB_Section_Audience_TimeOfDay.timeOfDayLayout;
    # Instagram
    if pathname == "/IG_Section_Posts":
        return IG_Section_Posts.postSectionlayout;
    if pathname == "/IG_Section_Page":
        return IG_Section_Page.pageSectionLayout;
    if pathname == "/IG_Section_Audience_AgeGender":
        return IG_Section_Audience_AgeGender.ageGenderLayout;
    if pathname == "/IG_Section_Audience_Country":
        return IG_Section_Audience_Country.countryLayout;
    if pathname == "/IG_Section_Audience_CanadianCity":
        return IG_Section_Audience_CanadianCity.canadianCityLayout;
    if pathname == "/IG_Section_Audience_TimeOfDay":
        return IG_Section_Audience_TimeOfDay.timeOfDayLayout;
    # Page Error
    else:
        return "404 Page Error! Please choose a link";

# Run dashboard application ----------------------------------------------
# app.run_server(debug=True, use_reloader=False)
if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
# if __name__ == '__main__':
#     app.run_server(debug=False)