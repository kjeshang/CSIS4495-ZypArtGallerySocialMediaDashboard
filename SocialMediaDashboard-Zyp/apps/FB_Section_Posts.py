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
# from dash.dependencies import Input, Output, State, callback
# from dash_extensions import Lottie
from dash import dash_table

import sys

sys.path.append(".")
from assets.googleService import getDataframe
from assets.FB_postMetrics import postEngagmentDetail, postImpressionDetail, postReactionDetail

# Import Dataset --------------------------------------------------
sheet = "ZypFacebook_Posts";
worksheet = "ZypFacebook_Posts";

df = getDataframe(sheet, worksheet);

# Prepare Data --------------------------------------------
post_ids = df["id"];
df["date"] = pd.to_datetime(df["date"]);
post_numerical_columns = df.columns.tolist()[6:];

postEngagment = post_numerical_columns[0:15];
postImpression = post_numerical_columns[15:31];
postReaction = post_numerical_columns[31:];

postMetricCategoryName = ["Post Engagement", "Post Impressions", "Post Reactions"];
postmetricCategory = [postEngagment, postImpression, postReaction];

# Create elements of the webpage ----------------------------------

# Title of webpage:
postSectionHeading = [html.H1("Facebook Post Insights", style={"font-weight":"bold"})];

# Date range filter:
postDateRangeFilter = [
    html.P("Date Range", style={"font-weight":"bold"}),
    dcc.DatePickerRange(
        id="FB_post_date-range",
        min_date_allowed=df["date"][len(df)-1],
        max_date_allowed=df["date"][0],
        start_date=df["date"][0] - timedelta(30),
        end_date=df["date"][0],
        updatemode="bothdates"
    )
];

# Post metric category checkbox filter:
postMetricCategoryCheckboxFilter = [
    html.P("Post Metric Category", style={"font-weight":"bold"}),
    dcc.Checklist(
        id="FB_post_metric_category",
        options=[{"label":postMetricCategoryName[x], "value":x} for x in range(len(postMetricCategoryName))],
        value=[0],
        inputStyle={"margin-right":"5px", "margin-left":"15px"}
    )
];

# Post ID dropdown selector:
postIDDropdownSelector = [
    html.P("Post ID", style={"font-weight":"bold"}),
    dcc.Dropdown(id="FB_post_id", clearable=False)
];

# Post metric bar chart:
postMetricbarChart = dcc.Graph(id="FB_post_metric_chart", figure={}, config={"displayModeBar":False});

# Actual Facebook Post in full form:
postMessageLabel = "Full Facebook Post Message";
postMessageParagraph = html.P(id="FB_post_message");

# Create post metric reference section of webpage:
postMetricReference = [
    dbc.Button(
        "Metric Reference",
        id="FB_collapse-button_post",
        className="mb-3",
        n_clicks=0,
    ),
    dbc.Collapse(
        html.Div(id="FB_create_post_metric_reference_dataframe"),
        id="FB_collapse_post",
        is_open=False,
    )
];

# Page Layout --------------------------------------------------------

# Structure:
postSectionStructure = [
    dbc.Row(children=postSectionHeading),
    dbc.Card(children=[
        dbc.CardBody(children=[
            dbc.Row(children=[
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=postDateRangeFilter)
                    ])
                ]),
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=postMetricCategoryCheckboxFilter)
                    ])
                ]),
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=postIDDropdownSelector)
                    ])
                ]),
            ], justify="around"),
            dbc.Row(children=[postMetricbarChart]),
            dbc.Card(children=[
                dbc.CardHeader(postMessageLabel),
                dbc.CardBody(children=[postMessageParagraph])
            ]),
            html.Br(),
            dbc.Row(children=postMetricReference)
        ])
    ])
];

# Finalizing the layout:
postSectionlayout = dbc.Container(children=postSectionStructure, fluid=True);

# Callbacks ----------------------------------------------------------

# Populate the Post ID dropdown selector with options that are Facebook Post ID values:
@callback(
    Output("FB_post_id","options"),
    [
        Input("FB_post_date-range", "start_date"), 
        Input("FB_post_date-range", "end_date"),
    ]
)
def set_postIDOptions(start_date, end_date):
    dateRange = (df["date"] >= start_date) & (df["date"] <= end_date);
    data = df[dateRange];
    data = data.reset_index();
    options = [{"label":x, "value":x} for x in data["id"]];
    return options;

# Set the most recent Facebook Post's ID to be the default value in the dropdown based on the date range selected:
@callback(
    Output("FB_post_id","value"),
    [
        Input("FB_post_date-range", "start_date"), 
        Input("FB_post_date-range", "end_date"),
    ]
)
def set_postIDValue(start_date, end_date):
    dateRange = (df["date"] >= start_date) & (df["date"] <= end_date);
    data = df[dateRange];
    data = data.reset_index();
    value = data["id"][0];
    return value;

# Create/update Facebook Posts metric bar chart based on the Post ID selected and metric categories chosen from the post metric category checklist:
@callback(
    Output("FB_post_metric_chart", "figure"),
    [
        Input("FB_post_metric_category", "value"),
        Input("FB_post_id", "value"),
    ]
)
def get_postMetricChart(post_metric_category, post_id):
    # Retrieve post metrics selected based on post metric categories chosen from respective checklist
    postMetricsSelected = [];
    for index in post_metric_category:
        for j in range(len(postmetricCategory[index])):
            postMetricsSelected.append(postmetricCategory[index][j]);

    # Drill down posts data to simply the selected Post ID from the respective dropdown
    mask = df["id"] == post_id;
    i = df[mask].index.values.astype(int)[0];
    
    # Create dataframe of from selected post metrics by retrieving the respective metric names, values, and titles
    data = [];
    for metric in postMetricsSelected:
        row = [];
        row.append(metric);
        row.append(df[mask][metric][i]);
        postMetricDetail = [postEngagmentDetail, postImpressionDetail, postReactionDetail];
        for metricType in postMetricDetail:
            for detail in metricType:
                if metric == detail.get("metric"):
                    row.append(detail.get("title"));
        data.append(row);

    labels = ["Metric","Count","Title"];
    dff = pd.DataFrame(data, columns=labels);

    # Create bar chart based on above created dataframe
    fig = px.bar(dff, x="Metric", y="Count", 
        color="Metric",
        title="Post: " + str(df[mask]["post"][i]) + " (" + str(df[mask]["date"][i])[:-9] + " " + str(df[mask]["time"][i]) + ")",
        hover_name="Title"
    );
    fig = fig.update_layout(legend_title_text="");

    return fig;

# Retrieve selected Facebook Post's ID's actual post message in full form:
@callback(
    Output("FB_post_message", "children"),
    Input("FB_post_id", "value")
)
def get_postMessageParagraph(post_id):
    mask = df["id"] == post_id;
    i = df[mask].index.values.astype(int)[0];
    value = df[mask]["message"][i];
    return value;

# Render post metric reference section of the webpage:
@callback(
    Output("FB_collapse_post", "is_open"),
    [Input("FB_collapse-button_post", "n_clicks")],
    [State("FB_collapse_post", "is_open")],
)
def toggle_collapse_post(n, is_open):
    if n:
        return not is_open
    return is_open

# Create page metric reference dataframe:
@callback(
    Output("FB_create_post_metric_reference_dataframe", "children"),
    [
        Input("FB_post_metric_category", "value")
    ]
)
def get_pageMetricReferenceDataframe(post_metric_category):
    postMetricsSelected = [];
    for index in post_metric_category:
        for j in range(len(postmetricCategory[index])):
            postMetricsSelected.append(postmetricCategory[index][j]);
    
    data = [];

    postMetricDetail = [postEngagmentDetail, postImpressionDetail, postReactionDetail];
    for metric in postMetricsSelected:
        for metricType in postMetricDetail:
            for detail in metricType:
                if metric == detail.get("metric"):
                    row = [];
                    row.append(detail.get("metric"));
                    row.append(detail.get("title"));
                    row.append(detail.get("description"));
        data.append(row);

    df = pd.DataFrame(data, columns=["Metric","Title","Description"]);

    return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True);