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
from assets.IG_audienceMetrics import audienceTimeOfDayDetail

# Import Dataset --------------------------------------------------
# df = pd.read_csv("data/ZypInstagram_Audience-TimeOfDay.csv", index_col=False);

sheet = "ZypInstagram_Audience-TimeOfDay";
worksheet = "ZypInstagram_Audience-TimeOfDay";
df = getDataframe(sheet, worksheet);

# Prepare Data --------------------------------------------
df["end_time"] = pd.to_datetime(df["end_time"]);

timeZone = ["Mountain Time","Pacific Standard Time"];

years = [];
for i in df.index:
    years.append(df.loc[i, "end_time"].year);
years = list(dict.fromkeys(years));

# Create elements of the webpage ----------------------------------
timeOfDaySectionHeading = [html.H1("Instagram Audience Insights - Time of Day", style={"font-weight":"bold"})];

# Year dropdown filter:
yearDropdownFilter = [
    html.P("Year", style={"font-weight":"bold"}),
    dcc.Dropdown(
        id="IG_timeOfDay_year",
        options=[{"label":x, "value":x} for x in df["year"].unique().tolist()],
        value=df["year"].unique().tolist()[0],
        clearable=False,
        searchable=False
    )
];

# Week dropdown filter:
weekDropdownFilter = [
    html.P("Week", style={"font-weight":"bold"}),
    dcc.Dropdown(id="IG_timeOfDay_week", clearable=False, searchable=False)
];

# Time zone selector:
timeZoneRadioButtonSelector = [
    html.P("Time Zone", style={"font-weight":"bold"}),
    dcc.RadioItems(
        id="IG_timeOfDay_time_zone",
        options=[{"label":timeZone[x], "value":x} for x in range(len(timeZone))],
        value=0,
        inputStyle={"margin-right":"5px", "margin-left":"15px"}
    )
];

# Time of day bar chart:
timeOfDayBarChart = dcc.Graph(id="IG_timeOfDay_chart", figure={}, config={'displayModeBar':False});

# Audience time of day metric reference dataframe:
def createTimeOfDayMetricReferenceDataframe():
    data = [];
    for i in range(len(audienceTimeOfDayDetail)):
        row = [];
        row.append(audienceTimeOfDayDetail[i].get("metric"));
        row.append(audienceTimeOfDayDetail[i].get("title"));
        row.append(audienceTimeOfDayDetail[i].get("description"));
        data.append(row);
    df = pd.DataFrame(data, columns=["Metric","Title","Description"]);
    return df;

# Create time of day reference section of webpage:
timeOfDayMetricReference = [
    dbc.Button(
        "Metric Reference",
        id="IG_collapse-button-timeOfDay",
        className="mb-3",
        n_clicks=0,
    ),
    dbc.Collapse(
        dbc.Table.from_dataframe(createTimeOfDayMetricReferenceDataframe(), striped=True, bordered=True, hover=True),
        id="IG_collapse-timeOfDay",
        is_open=False,
    )
];

# Page layout -----------------------------------------------------

# Structure:
timeOfDayStructure = [
    dbc.Row(children=timeOfDaySectionHeading),
    dbc.Card(children=[
        dbc.CardBody(children=[
            dbc.Row(children=[
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=yearDropdownFilter)
                    ])
                ]),
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=weekDropdownFilter)
                    ])
                ]),
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=timeZoneRadioButtonSelector)
                    ])
                ]),
            ]),
            # html.Br(),
            dbc.Row(children=[timeOfDayBarChart]),
            html.Br(),
            dbc.Row(children=timeOfDayMetricReference)
        ])
    ])
];

# Finalizing the layout:
timeOfDayLayout = dbc.Container(children=timeOfDayStructure, fluid=True);

# Callbacks --------------------------------------------------------

@callback(
    Output("IG_timeOfDay_week", "options"),
    Output("IG_timeOfDay_week", "value"),
    [
        Input("IG_timeOfDay_year", "value")
    ]
)
def get_WeekDropdownFilter(year_select):
    yearMask = df["year"] == year_select;
    options = [{"label":x, "value":x} for x in df[yearMask]["week"].unique().tolist()];
    value = df[yearMask]["week"].unique().tolist()[0];
    return options, value;

# Render time of day reference section of the webpage:
@callback(
    Output("IG_collapse-timeOfDay", "is_open"),
    [Input("IG_collapse-button-timeOfDay", "n_clicks")],
    [State("IG_collapse-timeOfDay", "is_open")],
)
def toggle_collapse_timeOfDay(n, is_open):
    if n:
        return not is_open
    return is_open

def set_dataframeTimeOfDay(dataframe, mask, timezone):
    df = dataframe[mask].copy();
    
    data = [];
    row = [];
    for tRange in df.columns.tolist()[3:]:
        avg = round(np.average(df[tRange]), 2);
        row.append(avg);
    data.append(row);
    dfTemp = pd.DataFrame(data, columns=df.columns.tolist()[3:]);

    index = dfTemp.index.values.astype(int)[0];

    timeRanges = dfTemp.columns.tolist();

    data = [];
    for i in range(len(timeRanges)):
        row = [];
        row.append(timeRanges[i]);
        row.append(dfTemp.transpose()[index][i]);
        data.append(row);
    dff = pd.DataFrame(data, columns=["Time Range","Count"]);

    if timezone == "Mountain Time":
        data = [];
        data.append([timeRanges[0], float(dff[dff["Time Range"] == "23:00 - 24:00"]["Count"])]);
        for i in range(len(timeRanges)-1):
            row = [];
            row.append(timeRanges[i+1]);
            row.append(dff.loc[i, "Count"]);
            data.append(row);
        dffMT = pd.DataFrame(data, columns=["Time Range", "Count"]);
        return dffMT;
    
    return dff;

@callback(
    Output("IG_timeOfDay_chart", "figure"),
    [
        Input("IG_timeOfDay_year", "value"),
        Input("IG_timeOfDay_week", "value"),
        Input("IG_timeOfDay_time_zone", "value")
    ],  
)
def get_timeOfDayBarChart(year_select, week_select, time_zone):
    mask = (df["year"] == year_select) & (df["week"] == week_select);
    index = df[mask].index.values.astype(int)[0];
    end_time = str(df[mask].loc[index, "end_time"]).split(" ")[0];
    timeZoneSelected = timeZone[time_zone];
    dff = set_dataframeTimeOfDay(df, mask, timeZoneSelected);
    title = "Online Followers by Time Range<br><sup>(As of " + end_time +")</sup>";
    fig = px.bar(dff, x="Time Range", y="Count", title=title);
    return fig;