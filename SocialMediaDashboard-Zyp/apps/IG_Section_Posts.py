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
from assets.IG_postMetrics import postDetail

# Import Dataset --------------------------------------------------
# df = pd.read_csv("data/ZypInstagram_Posts.csv", index_col=False);

sheet = "ZypInstagram_Posts";
worksheet = "ZypInstagram_Posts";
# df = getDataframe(sheet, worksheet);
listOfLists = getDataframe_listOfLists(sheet, worksheet);
df = pd.DataFrame(listOfLists[1:], columns=listOfLists[0])

# Prepare Data --------------------------------------------
df["date"] = pd.to_datetime(df["date"]);

# Create elements of the webpage ----------------------------------

# Title of webpage:
postSectionHeading = [html.H1("Instagram Post Insights", style={"font-weight":"bold"})];

# Date range filter:
postDateRangeFilter = [
    html.P("Date Range", style={"font-weight":"bold"}),
    dcc.DatePickerRange(
        id="IG_post_date-range",
        min_date_allowed=df["date"][len(df)-1],
        max_date_allowed=df["date"][0],
        start_date=df["date"][0] - timedelta(30),
        end_date=df["date"][0],
        updatemode="bothdates"
    )
];

postTable = [html.Div(id="IG_post_table")];

postMetricbarChart = dcc.Graph(id="IG_post_metric_chart", figure={}, config={"displayModeBar":False});

selectedPostInformation = [html.Div(id="IG_post_tblOUT")];

# Page Layout --------------------------------------------------------

postSectionStructure = [
    dbc.Row(children=postSectionHeading),
    dbc.Card(children=[
        dbc.CardBody(children=[
            dbc.Row(children=[
                dbc.Col(children=[
                    dbc.Row(
                        dbc.Card(children=[
                            dbc.CardBody(children=postDateRangeFilter)
                        ], style={"width":"80%", "left":"2%"})
                    ),
                    # html.Br(),
                    dbc.Row(children=[postMetricbarChart]),
                ], width=5, lg=6),
                dbc.Col(children=selectedPostInformation, width=7, lg=6)
            ]),
            html.Br(),
            dbc.Row(children=postTable)
        ])
    ])
];

# Finalizing the layout:
postSectionlayout = dbc.Container(children=postSectionStructure, fluid=True);

# Callbacks ----------------------------------------------------------

def set_IGPostDataframe(start_date, end_date):
    mask = (df["date"] >= start_date) & (df["date"] <= end_date);
    dff = df[mask].copy().rename(columns={"id":"post_id"});
    dff = dff.sort_values(by=["date","time"], ascending=False);
    dff = dff.copy().reset_index().rename(columns={"index":"id"});
    return dff;

@callback(
    Output("IG_post_table", "children"),
    [
        Input("IG_post_date-range", "start_date"),
        Input("IG_post_date-range", "end_date"),
    ]
)
def get_IGPostTable(start_date, end_date):
    dff = set_IGPostDataframe(start_date, end_date);
    dffTable = dff[["id","post_id","shortened_caption","datetime","media_product_type","media_type"]];
    dashTable = dash_table.DataTable(
            style_cell={
                'whiteSpace':'normal',
                'height':'auto'
            },
            data=dffTable.to_dict('records'),
            columns=[{"name": i, "id": i} for i in dffTable.columns if i != "id"],
            id="IG_post_tblIN",
            tooltip_header={
                "post_id":postDetail[1].get("description"),
                "shortened_caption":postDetail[11].get("description"),
                "datetime":postDetail[8].get("description"),
                "media_product_type":postDetail[6].get("description"),
                "media_type":postDetail[7].get("description"),
            },
            tooltip_delay=0,
            tooltip_duration=None
        );
    return dashTable;

@callback(
    Output("IG_post_metric_chart", "figure"),
    Output("IG_post_tblOUT", "children"),
    [
        Input("IG_post_date-range", "start_date"),
        Input("IG_post_date-range", "end_date"),
        Input("IG_post_tblIN", "active_cell")
    ]
)
def get_IGSelectedPostVisualizations(start_date, end_date, active_cell):
    dff = set_IGPostDataframe(start_date, end_date);
    row_id = 0;
    if active_cell != None:
        row_id = active_cell.get("row_id");
    data = [];
    for i in range(len(df.columns.tolist())):
        row = [];
        row.append(df.columns.tolist()[i]);
        if active_cell == None:
            row.append(dff.loc[0, df.columns.tolist()[i]]);
        else:
            row.append(dff.loc[row_id, df.columns.tolist()[i]]);
        row.append(postDetail[i].get("description"));
        data.append(row);
    dffTemp = pd.DataFrame(data, columns=["Metric","Count","Description"]);
    
    dffBar = dffTemp[dffTemp["Metric"].isin(["comments_count","like_count"])];
    fig = px.bar(dffBar, x="Metric", y="Count", color="Metric",
        hover_data=["Count","Description"],
        hover_name="Metric",
        title="Post: " + str(dff.loc[row_id, "shortened_caption"]) + " (" + str(dff.loc[row_id, "datetime"]) + ")",
    );

    card = dbc.Card([
        dbc.CardHeader(str(dff.loc[row_id, "media_product_type"])),
        dbc.CardBody([
            html.Div([
                html.H4(postDetail[2].get("field"), id="IG_post_caption_tooltip"),
                dbc.Tooltip(
                    postDetail[2].get("description"),
                    target="IG_post_caption_tooltip",
                    placement="left-end"
                )
            ]),
            html.P(str(dff.loc[row_id, "caption"])),
            html.Div([
                html.H4(postDetail[3].get("field"), id="IG_post_mediaURL_tooltip"),
                dbc.Tooltip(
                    postDetail[3].get("description"),
                    target="IG_post_mediaURL_tooltip",
                    placement="left-end"
                )
            ]),
            dbc.Button(
                "Click Here",
                className="ml-auto",
                href=str(dff.loc[row_id, "media_url"])
            )
        ]),
        dbc.CardFooter(str(dff.loc[row_id, "media_type"]))
    ]);

    return fig, card;