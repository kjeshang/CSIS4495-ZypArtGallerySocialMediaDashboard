import pandas as pd
import dash
import dash_bootstrap_components as dbc

# bootstrap theme
# https://bootswatch.com/lux/
external_stylesheets = [dbc.themes.LUX]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.config.suppress_callback_exceptions = True

# import dash_auth

# import sys

# sys.path.append(".")
# from assets.googleService import getDataframe, getDataframe_listOfLists
# sheet = "DashAppLogins";
# worksheet = "DashAppLogins";
# # df = getDataframe(sheet, worksheet);
# listOfLists = getDataframe_listOfLists(sheet, worksheet);
# df = pd.DataFrame(listOfLists[1:], columns=listOfLists[0])

# authDict = {};
# for i in df.index:
#     authDict[df.loc[i, "Username"]] = str(df.loc[i, "Password"]);

# auth = dash_auth.BasicAuth(
#     app,
#     authDict
# )