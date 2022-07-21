# Import packages -----------------------------------
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import calendar
# from dateutil import parser
import gspread

import plotly.express as px
# from jupyter_dash import JupyterDash
from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
# from dash_extensions import Lottie
from dash import dash_table

# import sys

# sys.path.append(".")
from assets.googleService import getDataframe_listOfLists, getDataframe
from assets.FB_pageMetrics import pageEngagementDetail, pageImpressionsDetail, pagePostsDetail, pageUserDemographicsDetail, pageViewsDetail
from assets.FB_pageMetrics import pageEngagementDetail_more
from assets.FB_pageMetrics import pageUserDemographics_more

# Import Dataset --------------------------------------------------
# df1 = pd.read_csv("data/ZypFacebook_Insights1.csv", index_col=False);
# df2 = pd.read_csv("data/ZypFacebook_Insights2.csv", index_col=False);
# df3 = pd.read_csv("data/ZypFacebook_Insights3.csv", index_col=False);

sheet1 = "ZypFacebook_Insights1";
worksheet1 = "ZypFacebook_Insights1";
df1 = getDataframe(sheet1, worksheet1);
# listOfLists1 = getDataframe_listOfLists(sheet1, worksheet1);
# df1 = pd.DataFrame(listOfLists1[1:], columns=listOfLists1[0])

sheet2 = "ZypFacebook_Insights2";
worksheet2 = "ZypFacebook_Insights2";
df2 = getDataframe(sheet2, worksheet2);
# listOfLists2 = getDataframe_listOfLists(sheet2, worksheet2);
# df2 = pd.DataFrame(listOfLists2[1:], columns=listOfLists2[0])

sheet3 = "ZypFacebook_Insights3";
worksheet3 = "ZypFacebook_Insights3";
# df3 = getDataframe(sheet3, worksheet3);
listOfLists3 = getDataframe_listOfLists(sheet3, worksheet3);
df3 = pd.DataFrame(listOfLists3[1:], columns=listOfLists3[0])

# Prepare Data --------------------------------------------
df1["end_time"] = pd.to_datetime(df1["end_time"]);
page_numerical_columns = df1.columns.tolist()[1:];

pageEngagement = page_numerical_columns[0:4];
pageImpressions = page_numerical_columns[4:6];
pagePosts = page_numerical_columns[6:8];
pageUserDemographics = page_numerical_columns[8:12];
pageViews = page_numerical_columns[12:];

pageMetricCategoryName = ["Page Engagement", "Page Impressions", "Page Posts", "Page User Demographics", "Page Views"];
pageMetricCategory = [pageEngagement, pageImpressions, pagePosts, pageUserDemographics, pageViews];

df2["end_time"] = pd.to_datetime(df2["end_time"]);

df3["end_time"] = pd.to_datetime(df3["end_time"]);

# Create elements of the webpage ----------------------------------

# Title of webpage:
pageSectionHeading = [html.H1("Facebook Page Insights", style={"font-weight":"bold"})];

# Date range filter:
pageDateRangeFilter = [
    html.P("Date Range", style={"font-weight":"bold"}),
    dcc.DatePickerRange(
        id="FB_page_date-range",
        min_date_allowed=df1["end_time"][len(df1)-1],
        max_date_allowed=df1["end_time"][0],
        start_date=df1["end_time"][0] - timedelta(30),
        end_date=df1["end_time"][0],
        updatemode="bothdates"
    )
];

# Lifetime page fans tile:
pageLifetimeFansTile = [
    html.H5("Lifetime Page Fans"),
    html.H2(id="FB_page_fans_tile"),
    dbc.Tooltip(pageUserDemographics_more[0].get("title"), target="FB_page_fans_tile", placement="bottom"),
];

# Average page fans online per day:
pageAverageFansOnlineTile = [
    html.H5("Average Page Fans Online"),
    html.H2(id="FB_page_fans_online_per_day_tile"),
    dbc.Tooltip("Average " + pageEngagementDetail_more[0].get("title"), target="FB_page_fans_online_per_day_tile", placement="bottom"),
];

# Page metric category checklist filter:
pageMetricCategoryCheckboxFilter = [
    html.P("Page Metric Category", style={"font-weight":"bold"}),
    dcc.Checklist(
        id="FB_page_metric_category",
        options=[{"label":pageMetricCategoryName[x], "value":x} for x in range(len(pageMetricCategoryName))],
        value=[0],
        inputStyle={"margin-right":"5px", "margin-left":"15px"}
    )
];

# Page metric line chart:
pageMetricLineChart = dcc.Graph(id="FB_page_metric_chart", figure={}, config={"displayModeBar":False});

# Create page metric reference section of webpage:
pageMetricReference = [
    dbc.Button(
        "Metric Reference",
        id="FB_collapse-button_page",
        className="mb-3",
        n_clicks=0,
    ),
    dbc.Collapse(
        html.Div(id="FB_create_page_metric_reference_dataframe"),
        id="FB_collapse_page",
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
                        dbc.CardBody(children=pageLifetimeFansTile)
                    ])
                ]),
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=pageAverageFansOnlineTile)
                    ])
                ]),
            ], justify="around"),
            html.Br(),
            dbc.Row(children=[
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=pageMetricCategoryCheckboxFilter)
                    ])
                ])
            ], justify="around"),
            dbc.Row(children=[pageMetricLineChart]),
            dbc.Row(children=pageMetricReference)
        ])
    ])
];

# Finalizing the layout:
pageSectionLayout = dbc.Container(children=pageSectionStructure, fluid=True);

# Callbacks --------------------------------------------------------

# Retrieve the lifetime fans of the Facebook page:
@callback(
    Output("FB_page_fans_tile", "children"),
    [Input("FB_page_date-range", "end_date")]
)
def get_pageFans(end_date):
    # endDate = df3["end_time"] == end_date;
    endDate = df1["end_time"] == end_date;
    pageFans = str(int(df3[endDate]["page_fans"]));
    return pageFans;

# Retrieve the average daily fans online of  the Facebook page:
@callback(
    Output("FB_page_fans_online_per_day_tile", "children"),
    [
        Input("FB_page_date-range", "start_date"),
        Input("FB_page_date-range", "end_date")
    ]
)
def get_pageFansOnline(start_date, end_date):
    # dateRange = (df2["end_time"] >= start_date) & (df2["end_time"] <= end_date);
    dateRange = (df1["end_time"] >= start_date) & (df1["end_time"] <= end_date);
    pageFansOnline = round(np.average(df2[dateRange]["page_fans_online_per_day"]), 2);
    return pageFansOnline;

# Create/update Facebook page metric line chart based on the metric categories chosen from the page metric category checklist:
@callback(
    Output("FB_page_metric_chart", "figure"),
    [
        Input("FB_page_date-range", "start_date"),
        Input("FB_page_date-range", "end_date"),
        Input("FB_page_metric_category", "value")
    ]
)
def get_pageMetricChart(start_date, end_date, page_metric_category):
    # Retrieve page metrics selected based on page metric categories chosen from respective checklist
    pageMetricsSelected = [];
    for index in page_metric_category:
        for j in range(len(pageMetricCategory[index])):
            pageMetricsSelected.append(pageMetricCategory[index][j]);
    
    # Drill down page data to be within the start & end dates from the date range filter
    dateRange = (df1["end_time"] >= start_date) & (df1["end_time"] <= end_date);
    dfTemp = df1[dateRange];

    # Create dataframe of from selected page metrics by retrieving the respective dates, metric names, values, and titles
    data = [];
    for i in dfTemp.index:
        for metric in pageMetricsSelected:
            row = [];
            row.append(dfTemp.loc[i, "end_time"]);
            row.append(metric);
            row.append(dfTemp.loc[i, metric].transpose());
            pageMetricDetail = [pageEngagementDetail, pageImpressionsDetail, pagePostsDetail, pageUserDemographicsDetail, pageViewsDetail];
            for metricType in pageMetricDetail:
                for detail in metricType:
                    if metric == detail.get("metric"):
                        row.append(detail.get("title"));
            data.append(row);
    labels = ["Date","Metric","Count","Title"];
    dff = pd.DataFrame(data, columns=labels);

    # Create line chart based on above created dataframe
    title = "Daily Page Insights";

    fig = px.line(dff, x="Date", y="Count", color="Metric", title=title, hover_name="Title");

    accurateTitle = title + "<br><sup>(From " + str(start_date[0:10]) + " to " + str(end_date[0:10]) + ")</sup>";
    fig.update_layout(title={'text': accurateTitle});

    return fig;

# Render page metric reference section of the webpage:
@callback(
    Output("FB_collapse_page", "is_open"),
    [Input("FB_collapse-button_page", "n_clicks")],
    [State("FB_collapse_page", "is_open")],
)
def toggle_collapse_page(n, is_open):
    if n:
        return not is_open
    return is_open

# Create page metric reference dataframe:
@callback(
    Output("FB_create_page_metric_reference_dataframe", "children"),
    [
        Input("FB_page_metric_category", "value")
    ]
)
def get_pageMetricReferenceDataframe(page_metric_category):
    pageMetricsSelected = [];
    for index in page_metric_category:
        for j in range(len(pageMetricCategory[index])):
            pageMetricsSelected.append(pageMetricCategory[index][j]);
    
    data = [];

    constantPageMetricDetail = [pageUserDemographics_more, pageEngagementDetail_more];
    for metricType in constantPageMetricDetail:
        for i in range(len(metricType)):
            row = [];
            row.append(metricType[i].get("metric"));
            row.append(metricType[i].get("title"));
            row.append(metricType[i].get("description"));
        data.append(row);

    pageMetricDetail = [pageEngagementDetail, pageImpressionsDetail, pagePostsDetail, pageUserDemographicsDetail, pageViewsDetail];
    for metric in pageMetricsSelected:
        for metricType in pageMetricDetail:
            for detail in metricType:
                if metric == detail.get("metric"):
                    row = [];
                    row.append(detail.get("metric"));
                    row.append(detail.get("title"));
                    row.append(detail.get("description"));
        data.append(row);

    df = pd.DataFrame(data, columns=["Metric","Title","Description"]);

    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True);