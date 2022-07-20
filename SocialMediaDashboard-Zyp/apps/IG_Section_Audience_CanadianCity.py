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

import sys

sys.path.append(".")
from assets.googleService import getDataframe_listOfLists, getDataframe
from assets.IG_audienceMetrics import audienceCanadianCityDetail, provinceDetail, conciseDetail

# Import Dataset --------------------------------------------------
# df = pd.read_csv("data/ZypInstagram_Audience-CanadianCity.csv", index_col=False);
geo_df = pd.read_excel("assets/GeoNamesData.xlsx", index_col=False)

sheet = "ZypInstagram_Audience-CanadianCity";
worksheet = "ZypInstagram_Audience-CanadianCity";
listOfLists = getDataframe_listOfLists(sheet, worksheet);
df = pd.DataFrame(listOfLists[1:], columns=listOfLists[0])

# geoSheet = "GeoNamesData";
# geoWorksheet = "GeoNamesData";
# geo_df = getDataframe(geoSheet, geoWorksheet);

# Prepare Data --------------------------------------------
df["end_time"] = pd.to_datetime(df["end_time"]);

subRegion = [];
subRegionAbbreviation = [];
for i in range(len(provinceDetail)):
    subRegion.append(provinceDetail[i].get("definition"));
    subRegionAbbreviation.append(provinceDetail[i].get("term"));
subRegion.append("Canada");
subRegionAbbreviation.append("CAN");

# Create elements of the webpage ----------------------------------

# Title of webpage:
canadianCitySectionHeading = [html.H1("Instagram Audience Insights - Canadian City", style={"font-weight":"bold"})];

# Year dropdown filter:
yearDropdownFilter = [
    html.P("Year", style={"font-weight":"bold"}),
    dcc.Dropdown(
        id="IG_canadianCity_year",
        options=[{"label":x, "value":x} for x in df["year"].unique().tolist()],
        value=df["year"].unique().tolist()[0],
        clearable=False,
        searchable=False
    )
];

# Week dropdown filter:
weekDropdownFilter = [
    html.P("Week", style={"font-weight":"bold"}),
    dcc.Dropdown(id="IG_canadianCity_week", clearable=False, searchable=False)
];

# Province filter:
canadianCityProvinceDropdownFilter = [
    html.P("Subregion Scope", style={"font-weight":"bold"}),
    dcc.Dropdown(
        id="IG_canadianCity_subRegion",
        options=[{"label":subRegion[x], "value":subRegionAbbreviation[x]} for x in range(len(subRegion))],
        value="CAN",
        searchable=False,
        clearable=False
    )
];

# Canadian city bubble map chart:
canadianCityBubbleMap = dcc.Graph(id="IG_canadianCity_bubbleMap", figure={}, config={'displayModeBar':False});

# Canadian city (top 10) bar chart:
canadianCityBarChart = dcc.Graph(id="IG_canadianCity_barChart", figure={}, config={'displayModeBar':False});

# Canadian city metric reference dataframe:
def createCanadianCityMetricReferenceDataframe():
    data = [];
    for i in range(len(audienceCanadianCityDetail)):
        row = [];
        row.append(audienceCanadianCityDetail[i].get("metric"));
        row.append(audienceCanadianCityDetail[i].get("title"));
        row.append(audienceCanadianCityDetail[i].get("description"));
        data.append(row);
    df = pd.DataFrame(data, columns=["Metric","Title","Description"]);
    return df;

# Create Canadian city reference section of webpage:
canadianCityMetricReference = [
    dbc.Button(
        "Metric Reference",
        id="IG_collapse-button-canadianCity",
        className="mb-3",
        n_clicks=0,
    ),
    dbc.Collapse(
        dbc.Table.from_dataframe(createCanadianCityMetricReferenceDataframe(), striped=True, bordered=True, hover=True),
        id="IG_collapse-canadianCity",
        is_open=False,
    )
];

# Page layout -----------------------------------------------------

# Structure:
canadianCityStructure = [
    dbc.Row(children=canadianCitySectionHeading),
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
                        dbc.CardBody(children=canadianCityProvinceDropdownFilter)
                    ])
                ], width=8),
            ]),
            html.Br(),
            dbc.Row(children=[canadianCityBubbleMap]),
            dbc.Row(children=[canadianCityBarChart]),
            html.Br(),
            dbc.Row(children=canadianCityMetricReference)
        ])
    ])
];

# Finalizing the layout:
canadianCityLayout = dbc.Container(children=canadianCityStructure, fluid=True);

# Callbacks --------------------------------------------------------

@callback(
    Output("IG_canadianCity_week", "options"),
    Output("IG_canadianCity_week", "value"),
    [
        Input("IG_canadianCity_year", "value")
    ]
)
def get_WeekDropdownFilter(year_select):
    yearMask = df["year"] == year_select;
    options = [{"label":x, "value":x} for x in df[yearMask]["week"].unique().tolist()];
    value = df[yearMask]["week"].unique().tolist()[0];
    return options, value;

# Render canadian city reference section of the webpage:
@callback(
    Output("IG_collapse-canadianCity", "is_open"),
    [Input("IG_collapse-button-canadianCity", "n_clicks")],
    [State("IG_collapse-canadianCity", "is_open")],
)
def toggle_collapse_canadianCity(n, is_open):
    if n:
        return not is_open
    return is_open

# Set dataframe for canadian city charts:
def set_dataframeForCanadianCityCharts(dataframe, mask):
    df = dataframe[mask].copy();
    index = df[mask].index.values.astype(int)[0];

    cities = df.columns.tolist()[3:];

    data = [];
    for i in range(len(cities)):
        row = [];
        count = int(df[mask].transpose()[3:][index][i]);
        if count > 0:
            row.append(cities[i]);
            row.append(count);
            data.append(row);
    dfTemp = pd.DataFrame(data, columns=["City","Count"]);

    data = [];
    for i in range(len(provinceDetail)):
        for x in dfTemp.index:
            if provinceDetail[i].get("definition") == dfTemp.loc[x, "City"].split(", ")[1]:
                for y in geo_df.index:
                    if dfTemp.loc[x, "City"].split(", ")[0] == geo_df.loc[y, "Geographical Name"]:
                        row = [];
                        row.append(dfTemp.loc[x, "City"]);
                        row.append(dfTemp.loc[x, "Count"]);
                        row.append(geo_df.loc[y, "Latitude"]);
                        row.append(geo_df.loc[y, "Longitude"]);
                        row.append(dfTemp.loc[x, "City"].split(", ")[0]);
                        row.append(provinceDetail[i].get("definition"));
                        data.append(row);
                        
    dfFinal = pd.DataFrame(data, columns=["Location","Count","Latitude","Longitude","City","Province"]);
    dfFinal = dfFinal.sort_values(["Count","Location"], ascending=False);
    dfFinal = dfFinal.drop_duplicates(subset=["Location"], keep="first");

    return dfFinal;

@callback(
    Output("IG_canadianCity_bubbleMap", "figure"),
    Output("IG_canadianCity_barChart", "figure"),
    [
        Input("IG_canadianCity_year", "value"),
        Input("IG_canadianCity_week", "value"),
        Input("IG_canadianCity_subRegion", "value")
    ]
)
def get_IGCanadianCityVisualizations(year_select, week_select, subRegion):
    mask = (df["year"] == year_select) & (df["week"] == week_select);
    index = df[mask].index.values.astype(int)[0];
    end_time = str(df[mask].loc[index, "end_time"]).split(" ")[0];
    dff = set_dataframeForCanadianCityCharts(df, mask);

    center = dict(lat=56.1304, lon=-106.3468);
    zoom = 3;
    bubbleTitle = "Profile Followers by City in Canada <br><sup>(As of " + end_time + ")</sup>";
    barTitle = "Profile Followers of Top 10 Canadian Cities <br><sup>(As of " + end_time + ")</sup>";
    for i in range(len(provinceDetail)):
        if subRegion == provinceDetail[i].get("term"):
            dff = dff[dff["Province"] == provinceDetail[i].get("definition")];
            latitude = float(provinceDetail[i].get("latitude"));
            longitude = float(provinceDetail[i].get("longitude"));
            center = dict(lat=latitude, lon=longitude);
            zoom = 4.5;
            bubbleTitle = "Profile Followers by Canadian City in " + provinceDetail[i].get("definition") + "<br><sup>(As of " + end_time + ")</sup>";
            barTitle = "Profile Followers of Top 10 Canadian Cities in " + provinceDetail[i].get("definition") + "<br><sup>(As of " + end_time + ")</sup>";
    
    # Bubble Map Chart:    
    figBubble = px.scatter_mapbox(dff, lat="Latitude", lon="Longitude",
                        color="Province",
                        size="Count",
                        hover_name="Location",
                        center=center,
                        zoom=zoom,
                        title=bubbleTitle
                    );
    figBubble.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        title_x=0.01,
        title_y=0.95,
    );

    # Bar Chart:
    figBar = px.bar(dff[0:10].sort_values(["Count","Location"], ascending=False), x="City", y="Count", color="Province", title=barTitle);

    return figBubble, figBar;