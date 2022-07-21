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

# import sys

# sys.path.append(".")
from assets.googleService import getDataframe_listOfLists, getDataframe
from assets.IG_audienceMetrics import audienceCountryDetail

# Import Dataset --------------------------------------------------
# df = pd.read_csv("data/ZypInstagram_Audience-Country.csv", index_col=False);
# df_iso_alpha_Final = pd.read_csv("assets/CountryCode-iso_alpha_Final.csv", index_col=False);
url="https://raw.githubusercontent.com/kjeshang/ZypArtGallerySocialMediaDashboard/main/SocialMediaDashboard-Zyp/assets/CountryCode-iso_alpha_Final.csv";
df_iso_alpha_Final = pd.read_csv(url, index_col=False);

sheet = "ZypInstagram_Audience-Country";
worksheet = "ZypInstagram_Audience-Country";
df = getDataframe(sheet, worksheet);
# listOfLists = getDataframe_listOfLists(sheet, worksheet);
# df = pd.DataFrame(listOfLists[1:], columns=listOfLists[0])

# sheet_iso_alpha = "CountryCode-iso_alpha_Final";
# worksheet_iso_alpha = "CountryCode-iso_alpha_Final";
# df_iso_alpha_Final = getDataframe(sheet_iso_alpha, worksheet_iso_alpha);

# Prepare Data --------------------------------------------
df["end_time"] = pd.to_datetime(df["end_time"]);

# Create elements of the webpage ----------------------------------

# Title of webpage:
countrySectionHeading = [html.H1("Instagram Audience Insights - Country", style={"font-weight":"bold"})];

# Year dropdown filter:
yearDropdownFilter = [
    html.P("Year", style={"font-weight":"bold"}),
    dcc.Dropdown(
        id="IG_country_year",
        options=[{"label":x, "value":x} for x in df["year"].unique().tolist()],
        value=df["year"].unique().tolist()[0],
        clearable=False,
        searchable=False
    )
];

# Week dropdown filter:
weekDropdownFilter = [
    html.P("Week", style={"font-weight":"bold"}),
    dcc.Dropdown(id="IG_country_week", clearable=False, searchable=False)
];

# Region scope radio button selector:
regionScopeRadioButtonSelector = [
    html.P("Region Scope", style={"font-weight":"bold"}),
    dcc.RadioItems(
        id="IG_country_region_scope",
        options=[{"label":x, "value":x} for x in df_iso_alpha_Final["Region"].unique().tolist()],
        value="World",
        inputStyle={"margin-right":"5px", "margin-left":"15px"}
    )
];

# Country choropleth:
countryChoropleth = dcc.Graph(id="IG_country_choropleth", figure={}, config={'displayModeBar':False});

# Country bar chart (top 10):
countryBarChart = dcc.Graph(id="IG_country_chart", figure={}, config={'displayModeBar':False});

# Audience country metric reference dataframe:
def createCountryMetricReferenceDataframe():
    data = [];
    for i in range(len(audienceCountryDetail)):
        row = [];
        row.append(audienceCountryDetail[i].get("metric"));
        row.append(audienceCountryDetail[i].get("title"));
        row.append(audienceCountryDetail[i].get("description"));
        data.append(row);
    df = pd.DataFrame(data, columns=["Metric","Title","Description"]);
    return df;

# Create country reference section of webpage:
countryMetricReference = [
    dbc.Button(
        "Metric Reference",
        id="IG_collapse-button-country",
        className="mb-3",
        n_clicks=0,
    ),
    dbc.Collapse(
        dbc.Table.from_dataframe(createCountryMetricReferenceDataframe(), striped=True, bordered=True, hover=True),
        id="IG_collapse-country",
        is_open=False,
    )
];

# Page layout -----------------------------------------------------

# Structure:
countryStructure = [
    dbc.Row(children=countrySectionHeading),
    dbc.Card(children=[
        dbc.CardBody(children=[
            dbc.Row(children=[
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=yearDropdownFilter)
                    ])
                ], width=2),
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=weekDropdownFilter)
                    ])
                ], width=2),
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=regionScopeRadioButtonSelector)
                    ])
                ], width=8),
            ]),
            # html.Br(),
            dbc.Row(children=[
                dbc.Col(children=[countryBarChart], width=5),
                dbc.Col(children=[countryChoropleth], width=7)
            ]),
            html.Br(),
            dbc.Row(children=countryMetricReference)
        ])
    ])
];

# Finalizing the layout:
countryLayout = dbc.Container(children=countryStructure, fluid=True);

# Callbacks --------------------------------------------------------

@callback(
    Output("IG_country_week", "options"),
    Output("IG_country_week", "value"),
    [
        Input("IG_country_year", "value")
    ]
)
def get_WeekDropdownFilter(year_select):
    yearMask = df["year"] == year_select;
    options = [{"label":x, "value":x} for x in df[yearMask]["week"].unique().tolist()];
    value = df[yearMask]["week"].unique().tolist()[0];
    return options, value;

# Render country reference section of the webpage:
@callback(
    Output("IG_collapse-country", "is_open"),
    [Input("IG_collapse-button-country", "n_clicks")],
    [State("IG_collapse-country", "is_open")],
)
def toggle_collapse_country(n, is_open):
    if n:
        return not is_open
    return is_open

def set_dataframeForCountryCharts(dataframe, mask):
    df = dataframe[mask].copy();
    index = df[mask].index.values.astype(int)[0];

    df = df.rename(columns={
        "Antigua":"Antigua and Barbuda",
        "Aland Islands":"Åland Islands",
        "The Bahamas":"Bahamas, The",
        "Democratic Republic of the Congo":"Congo, Democratic Republic of the",
        "Republic of the Congo":"Congo, Republic of the",
        "Falkland Islands":"Falkland Islands (Islas Malvinas)",
        "Federated States of Micronesia":"Micronesia, Federated States of",
        "The Gambia":"Gambia, The",
        "Isle Of Man":"Isle of Man",
        "South Korea":"Korea, South",
        "St. Lucia":"Saint Lucia",
        "Palestine":"Palestine, State of",
        "Saint Helena":"Saint Helena, Ascension and Tristan da Cunha",
        "Vatican City":"Holy See",
        "US Virgin Islands":"Virgin Islands (U.S.)",
        "CÃ´te d'Ivoire":"Côte d'Ivoire",
        "CuraÃ§ao":"Curaçao",
        "RÃ©union":"Réunion",
        "Saint BarthÃ©lemy":"Saint Barthélemy",
        "Cape Verde":"Cabo Verde"
    });

    countries1 = df.columns.tolist()[3:];

    data = [];
    for i in range(len(countries1)):
        row = [];
        row.append(countries1[i]);
        for j in df_iso_alpha_Final.index:
            if df_iso_alpha_Final.loc[j, "Country"] == countries1[i]:
                row.append(df_iso_alpha_Final.loc[j, "Code"]);
                row.append(df_iso_alpha_Final.loc[j, "Region"]);
        row.append(df[mask].transpose()[3:][index][i]);
        data.append(row);

    dff = pd.DataFrame(data, columns=["Country","iso_alpha","Region","Count"]); 

    indexANT = dff[dff["Country"] == "Netherlands Antilles"].index.astype(int)[0];
    dff.loc[indexANT, "iso_alpha"] = "ANT";
    dff.loc[indexANT, "Region"] = "Europe";

    dff["Count"] = dff["Count"].fillna(0);

    return dff;

@callback(
    Output("IG_country_choropleth", "figure"),
    Output("IG_country_chart", "figure"),
    [
        Input("IG_country_year", "value"),
        Input("IG_country_week", "value"),
        Input("IG_country_region_scope", "value")
    ]
)
def get_IGCountryVisualizations(year_select, week_select, region_scope):
    mask = (df["year"] == year_select) & (df["week"] == week_select);
    index = df[mask].index.values.astype(int)[0];
    end_time = str(df[mask].loc[index, "end_time"]).split(" ")[0];
    dff = set_dataframeForCountryCharts(df, mask);

    # Country Choropeth:
    figMap = go.Figure(data=go.Choropleth(
        locations = dff['iso_alpha'],
        z = dff['Count'],
        text = dff['Country'],
        colorbar_title = "Count",
    ));
    title = "Profile Followers by Country <br><sup>(As of " + end_time + ")</sup>";
    figMap.update_layout(
        title_text = title,
        geo = dict(
            projection = {'type':'natural earth'},
            scope = region_scope.lower()
        )
    );

    # Country Top 10 Bar Chart:
    dff = dff.sort_values(["Count","Country"], ascending=False);
    if region_scope == "World":
        filter = (dff["Count"] != '') & (dff["Count"].notna()) & (dff["Count"].notnull());
    else:
        filter = (dff["Count"] != '') & (dff["Count"].notna()) & (dff["Count"].notnull()) & (dff["Region"] == region_scope);
    dffTop = dff[filter][0:10].copy();
    dffTop = dffTop.sort_values("Count", ascending=True);
    title = "Profile Followers in Top 10 Countries <br><sup>(As of " + end_time + ")</sup>";
    # figBar = px.bar(dffTop, x="Count", y="Country", color="Region", title=title, orientation='h');
    figBar = px.bar(dffTop, x="Count", y="Country", title=title, orientation='h');

    return figMap, figBar;