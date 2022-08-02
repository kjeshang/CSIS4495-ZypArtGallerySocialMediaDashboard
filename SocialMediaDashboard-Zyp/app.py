# Import packages -----------------------------------
import pandas as pd
import dash
import dash_bootstrap_components as dbc
import dash_auth
from assets.googleService import getDataframe_listOfLists, getDataframe
import flask
import os
from random import randint

# Instantiate dashboard application --------------------------------------
# bootstrap theme
# https://bootswatch.com/lux/
external_stylesheets = [dbc.themes.LUX]

# app = dash.Dash(__name__, 
#     external_stylesheets=external_stylesheets,
#     meta_tags=[{'name': 'viewport',
#                 'content': 'width=device-width, initial-scale=1.0'}]
# )
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
# app = dash.Dash(__name__,server=server,external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash(__name__,server=server,external_stylesheets=external_stylesheets)
# app = dash.Dash(__name__,server=server)

# server = app.server
app.config.suppress_callback_exceptions = True

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