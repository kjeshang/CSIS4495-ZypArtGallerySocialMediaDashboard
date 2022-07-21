# Import packages -----------------------------------
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import calendar
# from dateutil import parser
import gspread

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
from assets.FB_audienceMetrics import audienceTimeOfDayDetail

# Import Dataset --------------------------------------------------
# df = pd.read_csv("data/ZypFacebook_Audience-TimeOfDay.csv", index_col=False);

sheet = "ZypFacebook_Audience-TimeOfDay";
worksheet = "ZypFacebook_Audience-TimeOfDay";
df = getDataframe(sheet, worksheet);
# listOfLists = getDataframe_listOfLists(sheet, worksheet);
# df = pd.DataFrame(listOfLists[1:], columns=listOfLists[0])

# Prepare Data --------------------------------------------
df["end_time"] = pd.to_datetime(df["end_time"]);

timeZone = ["Mountain Time","Pacific Standard Time"];

years = [];
for i in df.index:
    years.append(df.loc[i, "end_time"].year);
years = list(dict.fromkeys(years));

# Create elements of the webpage ----------------------------------
timeOfDaySectionHeading = [html.H1("Facebook Audience Insights - Time of Day", style={"font-weight":"bold"})];

# Date range filter:
timeOfDayDateRangeFilter = [
    html.P("Date Range", style={"font-weight":"bold"}),
    dcc.DatePickerRange(
        id="FB_timeOfDay_date-range",
        min_date_allowed=df["end_time"][len(df)-1],
        max_date_allowed=df["end_time"][0],
        start_date=df["end_time"][0] - timedelta(30),
        end_date=df["end_time"][0],
        updatemode="bothdates"
    )
];

# Time zone selector:
timeZoneRadioButtonSelector = [
    html.P("Time Zone", style={"font-weight":"bold"}),
    dcc.RadioItems(
        id="FB_timeOfDay_time_zone",
        options=[{"label":timeZone[x], "value":x} for x in range(len(timeZone))],
        value=0,
        inputStyle={"margin-right":"5px", "margin-left":"15px"}
    )
];

# Year checklist selector:
yearDropdownSelector = [
    html.P("Year", style={"font-weight":"bold"}),
    dcc.Dropdown(
        id="FB_timeOfDay_year_select",
        options=[{"label":years[x], "value":x} for x in range(len(years))],
        value=[0,1],
        multi=True
    )
];

# Average page fans active online bar chart:
timeOfDayBarChart = dcc.Graph(id="FB_timeOfDay_chart_1", figure={}, config={'displayModeBar':False});

# Average page fans active online years area chart:
timeOfDayYearsAreaChart = dcc.Graph(id="FB_timeOfDay_chart_2", figure={}, config={'displayModeBar':False});

# Average page fans active online date range to year comparison line chart:
timeOfDayComparisonLineChart = dcc.Graph(id="FB_timeOfDay_chart_3", figure={}, config={'displayModeBar':False});

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
        id="FB_collapse-button-timeOfDay",
        className="mb-3",
        n_clicks=0,
    ),
    dbc.Collapse(
        dbc.Table.from_dataframe(createTimeOfDayMetricReferenceDataframe(), striped=True, bordered=True, hover=True),
        id="FB_collapse-timeOfDay",
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
                        dbc.CardBody(children=timeOfDayDateRangeFilter)
                    ])
                ]),
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=timeZoneRadioButtonSelector)
                    ])
                ]),
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=yearDropdownSelector)
                    ])
                ])
            ]),
            dbc.Row(children=[timeOfDayBarChart]),
            html.Br(),
            dbc.Row(children=[
                dbc.Col(children=[timeOfDayYearsAreaChart], width=6),
                dbc.Col(children=[timeOfDayComparisonLineChart], width=6)
            ]),
            html.Br(),
            dbc.Row(children=timeOfDayMetricReference)
        ])
    ])
];

# Finalizing the layout:
timeOfDayLayout = dbc.Container(children=timeOfDayStructure, fluid=True);

# Callbacks --------------------------------------------------------

# Render time of day reference section of the webpage:
@callback(
    Output("FB_collapse-timeOfDay", "is_open"),
    [Input("FB_collapse-button-timeOfDay", "n_clicks")],
    [State("FB_collapse-timeOfDay", "is_open")],
)
def toggle_collapse_timeOfDay(n, is_open):
    if n:
        return not is_open
    return is_open

# Setup of time of day dataframe based on filters and selectors:
def set_dataframeTimeOfDay(dataframe, mask, timezone):
    df = dataframe[mask].copy();
    
    data = [];
    row = [];
    for tRange in df.columns.tolist()[1:]:
        avg = round(np.average(df[tRange]), 2);
        row.append(avg);
    data.append(row);
    dfTemp = pd.DataFrame(data, columns=df.columns.tolist()[1:]);

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

# Callback for average page fans active online bar chart:
@callback(
    Output("FB_timeOfDay_chart_1", "figure"),
    [
        Input("FB_timeOfDay_date-range", "start_date"),
        Input("FB_timeOfDay_date-range", "end_date"),
        Input("FB_timeOfDay_time_zone", "value")
    ],  
)
def get_timeOfDayBarChart(start_date, end_date, time_zone):
    mask = (df["end_time"] >= start_date) & (df["end_time"] <= end_date);
    timeZoneSelected = timeZone[time_zone];
    dff = set_dataframeTimeOfDay(df, mask, timeZoneSelected);
    title = "Average Daily Fans Online by Time Range <br><sup>(From " + str(start_date[0:10]) + " to " + str(end_date[0:10]) + ")</sup>";
    fig = px.bar(dff, x="Time Range", y="Count", title=title);
    return fig;

# Callback for average page fans active online years area chart:
@callback(
    Output("FB_timeOfDay_chart_2", "figure"),
    [
        Input("FB_timeOfDay_year_select", "value"),
        Input("FB_timeOfDay_time_zone", "value"),
    ]
)
def get_TimeOfDayYearsAreaChart(year_select, timezone): 
    yearsSelected = [];
    for i in year_select:
        yearsSelected.append(years[i]); 

    yearReverse = [];
    for year in reversed(yearsSelected):
        yearReverse.append(year);
    
    dfList = [];
    for year in yearReverse:
        startDate = pd.Timestamp(year=year, month=1, day=1);
        endDate = pd.Timestamp(year=year, month=12, day=31);
        dateRange = (df["end_time"] >= startDate) & (df["end_time"] <= endDate);

        dfYear = set_dataframeTimeOfDay(df, dateRange, timezone);
        dfYear["Time Frame"] = year;
        dfList.append(dfYear);
    dffYear = pd.concat(dfList);

    title = "Average Daily Fans Online over the Years<br><sup>(From " + str(np.min(yearsSelected)) + " to " + str(np.max(yearsSelected)) + ")</sup>";

    fig = px.area(dffYear, x="Time Range", y="Count", color="Time Frame", title=title);

    return fig;

# Callback for average page fans active online date range to year comparison line chart:
@callback(
    Output("FB_timeOfDay_chart_3", "figure"),
    [
        Input("FB_timeOfDay_year_select", "value"),
        Input("FB_timeOfDay_time_zone", "value"),
        Input("FB_timeOfDay_date-range", "start_date"),
        Input("FB_timeOfDay_date-range", "end_date"),
    ]
)
def get_timeOfDayComparisonLineChart(year_select, time_zone, start_date, end_date): 
    yearsSelected = [];
    for i in year_select:
        yearsSelected.append(years[i]); 

    timeZoneSelected = timeZone[time_zone];

    yearReverse = [];
    for year in reversed(yearsSelected):
        yearReverse.append(year);
    
    dfList = [];
    for year in yearReverse:
        startDate = pd.Timestamp(year=year, month=1, day=1);
        endDate = pd.Timestamp(year=year, month=12, day=31);
        dateRange = (df["end_time"] >= startDate) & (df["end_time"] <= endDate);

        dfYear = set_dataframeTimeOfDay(df, dateRange, time_zone);
        dfYear["Time Frame"] = year;
        dfList.append(dfYear);
    
    mask = (df["end_time"] >= start_date) & (df["end_time"] <= end_date);
    dff = set_dataframeTimeOfDay(df, mask, timeZoneSelected);
    dff["Time Frame"] = str(start_date)[0:10] + " - " + str(end_date)[0:10];
    dfList.append(dff);

    dffYear = pd.concat(dfList);

    title = "Average Daily Fans Online Time Frame Comparison";
    title += "<br><sup>(Date Range: " + str(start_date)[0:10] + " - " + str(end_date)[0:10] + " <b>vs.</b> Years: " + str(np.min(yearsSelected)) + " to " + str(np.max(yearsSelected)) + ")</sup>";  

    fig = px.line(dffYear, x="Time Range", y="Count", color="Time Frame", title=title);

    return fig;
