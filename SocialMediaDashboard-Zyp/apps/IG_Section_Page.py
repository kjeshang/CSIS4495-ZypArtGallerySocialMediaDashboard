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
from assets.IG_pageMetrics import pageDetail, pageDetailMore

# Import Dataset --------------------------------------------------
# df1 = pd.read_csv("data/ZypInstagram_Insights1.csv", index_col=False);
# df2 = pd.read_csv("data/ZypInstagram_Insights2.csv", index_col=False);

sheet1 = "ZypInstagram_Insights1";
worksheet1 = "ZypInstagram_Insights1";
# df1 = getDataframe(sheet1, worksheet1);
listOfLists1 = getDataframe_listOfLists(sheet1, worksheet1);
df1 = pd.DataFrame(listOfLists1[1:], columns=listOfLists1[0])

sheet2 = "ZypInstagram_Insights2";
worksheet2 = "ZypInstagram_Insights2";
# df2 = getDataframe(sheet2, worksheet2);
listOfLists2 = getDataframe_listOfLists(sheet2, worksheet2);
df2 = pd.DataFrame(listOfLists2[1:], columns=listOfLists2[0])

# Prepare Data --------------------------------------------
df1["end_time"] = pd.to_datetime(df1["end_time"]);
df2["end_time"] = pd.to_datetime(df2["end_time"]);

# Create elements of the webpage ----------------------------------

# Title of webpage:
pageSectionHeading = [html.H1("Instagram Page Insights", style={"font-weight":"bold"})];

# Date range filter:
pageDateRangeFilter = [
    html.P("Date Range", style={"font-weight":"bold"}),
    dcc.DatePickerRange(
        id="IG_page_date-range",
        min_date_allowed=df1["end_time"][len(df1)-1],
        max_date_allowed=df1["end_time"][0],
        start_date=df1["end_time"][0] - timedelta(30),
        end_date=df1["end_time"][0],
        updatemode="bothdates"
    )
];

# Follower Count tile:
pagefollowerCountTile = [
    html.H5("New Follower Count"),
    html.H2(id="IG_follower_count_tile"),
    dbc.Tooltip(pageDetailMore[0].get("description"), target="IG_follower_count_tile", placement="bottom"),
];

# Page metric line chart:
pageMetricLineChart = dcc.Graph(id="IG_page_metric_chart", figure={}, config={"displayModeBar":False});

# Audience age & gender metric reference dataframe:
def createPageReferenceDataframe():
    data = [];
    data.append([pageDetailMore[0].get("metric"), pageDetailMore[0].get("title"), pageDetailMore[0].get("description")]);
    for i in range(len(pageDetail)):
        row = [];
        row.append(pageDetail[i].get("metric"));
        row.append(pageDetail[i].get("title"));
        row.append(pageDetail[i].get("description"));
        data.append(row);
    df = pd.DataFrame(data, columns=["Metric","Title","Description"]);
    return df;

# Create page metric reference section of webpage:
pageMetricReference = [
    dbc.Button(
        "Metric Reference",
        id="IG_collapse-button-page",
        className="mb-3",
        n_clicks=0,
    ),
    dbc.Collapse(
        dbc.Table.from_dataframe(createPageReferenceDataframe(), striped=True, bordered=True, hover=True),
        id="IG_collapse-page",
        is_open=False,
    )
];

# Page layout -----------------------------------------------------

# Structure:
pageSectionStructure = [
    dbc.Row(children=pageSectionHeading),
    dbc.Card(children=[
        dbc.CardBody(children=[
            dbc.Row(children=[
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=pageDateRangeFilter)
                    ])
                ]),
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=pagefollowerCountTile)
                    ])
                ])
            ]),
            dbc.Row(children=[pageMetricLineChart]),
            dbc.Row(children=pageMetricReference)
        ])
    ])
];

# Finalizing the layout:
pageSectionLayout = dbc.Container(children=pageSectionStructure, fluid=True);

# Callbacks --------------------------------------------------------

# Render page reference section of the webpage:
@callback(
    Output("IG_collapse-page", "is_open"),
    [Input("IG_collapse-button-page", "n_clicks")],
    [State("IG_collapse-page", "is_open")],
)
def toggle_collapse_ageGender(n, is_open):
    if n:
        return not is_open
    return is_open

def set_IGPageDataframe1(mask):
    data = [];
    for i in df1[mask].index:
        for col in df1[mask].columns.tolist()[1:]:
            row = [];
            row.append(df1[mask].loc[i, "end_time"]);
            row.append(col);
            row.append(df1[mask].loc[i, col].transpose());
            for detail in pageDetail:
                if col == detail.get("metric"):
                    row.append(detail.get("title"));
                    row.append(detail.get("description"));
            data.append(row);
    dff = pd.DataFrame(data, columns=["Date","Metric","Count","Title","Description"]);
    return dff;

@callback(
    Output("IG_page_metric_chart", "figure"),
    Output("IG_follower_count_tile", "children"),
    [
        Input("IG_page_date-range", "start_date"),
        Input("IG_page_date-range", "end_date")
    ]
)
def get_IGPageVisualizations(start_date, end_date):
    mask = (df1["end_time"] >= start_date) & (df1["end_time"] <= end_date);
    dff = set_IGPageDataframe1(mask);
    title = "Daily Page Insights<br><sup>(From " + str(start_date[0:10]) + " to " + str(end_date[0:10]) + ")</sup>";
    fig = px.line(dff, x="Date", y="Count", color="Metric", title=title, hover_name="Title", hover_data=["Metric","Count"]);
    currentFollowerCount = np.sum(df2[mask]["follower_count"]);
    return fig, currentFollowerCount;