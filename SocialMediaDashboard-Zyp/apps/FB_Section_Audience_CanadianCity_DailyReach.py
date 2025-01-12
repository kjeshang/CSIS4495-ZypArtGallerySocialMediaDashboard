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
from assets.FB_audienceMetrics import audienceCanadianCityDetail, provinceDetail, conciseDetail

# Import Dataset -------------------------------------------------

# Local Data ******************************************************
df2 = pd.read_csv("data/ZypFacebook_Audience-CanadianCity2.csv", index_col=False, encoding='utf8');
geo_df = pd.read_csv("assets/GeoNamesData.csv", index_col=False);

# Online Data ******************************************************
# sheet1 = "ZypFacebook_Audience-CanadianCity1";
# worksheet1 = "ZypFacebook_Audience-CanadianCity1";
# listOfLists1 = getDataframe_listOfLists(sheet1, worksheet1);
# df1 = pd.DataFrame(listOfLists1[1:], columns=listOfLists1[0])

# sheet2 = "ZypFacebook_Audience-CanadianCity2";
# worksheet2 = "ZypFacebook_Audience-CanadianCity2";
# listOfLists2 = getDataframe_listOfLists(sheet2, worksheet2);
# df2 = pd.DataFrame(listOfLists2[1:], columns=listOfLists2[0])

# geoSheet = "GeoNamesData";
# geoWorksheet = "GeoNamesData";
# geo_df = getDataframe(geoSheet, geoWorksheet);
# url = "https://raw.githubusercontent.com/kjeshang/ZypArtGallerySocialMediaDashboard/main/SocialMediaDashboard-Zyp/assets/GeoNamesData.csv";
# geo_df = pd.read_csv(url, index_col=False);

# Prepare Data --------------------------------------------
df2["end_time"] = pd.to_datetime(df2["end_time"]);

subRegion = [];
subRegionAbbreviation = [];
for i in range(len(provinceDetail)):
    subRegion.append(provinceDetail[i].get("definition"));
    subRegionAbbreviation.append(provinceDetail[i].get("term"));
subRegion.append("Canada");
subRegionAbbreviation.append("CAN");

# Create elements of the webpage ----------------------------------

# Title of webpage:
canadianCitySectionHeading = [
    html.H1("Facebook Audience Insights - Canadian City", style={"font-weight":"bold"}),
    html.H5("Daily Reach")
];

# Date range filter:
canadianCityDateRangeFilter = [
    html.P("Date Range", style={"font-weight":"bold"}),
    dcc.DatePickerRange(
        id="FB_canadianCity_date-range2",
        min_date_allowed=df2["end_time"][len(df2)-1],
        max_date_allowed=df2["end_time"][0],
        start_date=df2["end_time"][0] - timedelta(30),
        end_date=df2["end_time"][0],
        updatemode="bothdates"
    )
];

# Province filter:
canadianCityProvinceDropdownFilter = [
    html.P("Subregion Scope", style={"font-weight":"bold"}),
    dcc.Dropdown(
        id="FB_canadianCity_subRegion2",
        options=[{"label":subRegion[x], "value":subRegionAbbreviation[x]} for x in range(len(subRegion))],
        value="CAN",
        searchable=False,
        clearable=False
    )
];

# Daily reach by Canadian city bubble map chart:
canadianCityBubbleMap_2 = dcc.Graph(id="FB_canadianCity_bubbleMap_2", figure={}, config={'displayModeBar':False});

# Daily reach Canadian city (top 10) bar chart:
canadianCityBarChart_2 = dcc.Graph(id="FB_canadianCity_barChart_2", figure={}, config={'displayModeBar':False});

# Canadian city metric reference dataframe:
def createCanadianCityMetricReferenceDataframe():
    data = [];
    # for i in range(len(audienceCanadianCityDetail)):
    #     row = [];
    #     row.append(audienceCanadianCityDetail[i].get("metric"));
    #     row.append(audienceCanadianCityDetail[i].get("title"));
    #     row.append(audienceCanadianCityDetail[i].get("description"));
    #     data.append(row);
    row = [];
    row.append(audienceCanadianCityDetail[1].get("metric"));
    row.append(audienceCanadianCityDetail[1].get("title"));
    row.append(audienceCanadianCityDetail[1].get("description"));
    data.append(row);
    df = pd.DataFrame(data, columns=["Metric","Title","Description"]);
    return df;

# Create Canadian city reference section of webpage:
canadianCityMetricReference = [
    dbc.Button(
        "Metric Reference",
        id="FB_collapse-button-canadianCity2",
        className="mb-3",
        n_clicks=0,
    ),
    dbc.Collapse(
        dbc.Table.from_dataframe(createCanadianCityMetricReferenceDataframe(), striped=True, bordered=True, hover=True),
        id="FB_collapse-canadianCity2",
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
                        dbc.CardBody(children=canadianCityDateRangeFilter)
                    ])
                ]),
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=canadianCityProvinceDropdownFilter)
                    ])
                ])
            ]),
            html.Br(),
            dbc.Row(children=[
                dbc.Row(children=[canadianCityBubbleMap_2]),
                dbc.Row(children=[canadianCityBarChart_2])
            ]),
            html.Br(),
            dbc.Row(children=canadianCityMetricReference)
        ])
    ])
];

# Finalizing the layout:
canadianCityLayout = dbc.Container(children=canadianCityStructure, fluid=True);

# Callbacks --------------------------------------------------------

# Render canadian city reference section of the webpage:
@callback(
    Output("FB_collapse-canadianCity2", "is_open"),
    [Input("FB_collapse-button-canadianCity2", "n_clicks")],
    [State("FB_collapse-canadianCity2", "is_open")],
)
def toggle_collapse_canadianCity(n, is_open):
    if n:
        return not is_open
    return is_open

# Daily Reach by Canadian City Tab  *************************************

def set_dataframeForCanadianCityCharts2(dataframe, mask):
    df = dataframe[mask].copy();

    cities = df.columns.tolist()[1:];

    data = [];
    for city in cities:
        row = [];
        df[city] = df[city].astype('float');
        avg = round(np.average(df[city]), 2);
        if avg > 0:
            row.append(city);
            row.append(avg);
            data.append(row);
    dfTemp = pd.DataFrame(data, columns=["City","Count"]);

    data = [];
    for i in range(len(provinceDetail)):
        for x in dfTemp.index:
            if provinceDetail[i].get("term") == dfTemp.loc[x, "City"].split(", ")[1]:
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
    Output("FB_canadianCity_bubbleMap_2", "figure"),
    Output("FB_canadianCity_barChart_2", "figure"),
    [
        Input("FB_canadianCity_date-range2", "start_date"),
        Input("FB_canadianCity_date-range2", "end_date"),
        Input("FB_canadianCity_subRegion2", "value")
    ]
)
def get_canadianCityLifetimeLikesCharts2(start_date, end_date, subRegion):
    mask = (df2["end_time"] >= start_date) & (df2["end_time"] <= end_date);
    dff = set_dataframeForCanadianCityCharts2(df2, mask);
    center = dict(lat=56.1304, lon=-106.3468);
    zoom = 3;
    bubbleTitle = "Average Daily Reach by City in Canada<br><sup>(From " + str(start_date[0:10]) + " to " + str(end_date[0:10]) + ")</sup>";
    barTitle = "Average Daily Reach of Top 10 Canadian Cities<br><sup>(From " + str(start_date[0:10]) + " to " + str(end_date[0:10]) + ")</sup>";
    for i in range(len(provinceDetail)):
        if subRegion == provinceDetail[i].get("term"):
            dff = dff[dff["Province"] == provinceDetail[i].get("definition")];
            latitude = float(provinceDetail[i].get("latitude"));
            longitude = float(provinceDetail[i].get("longitude"));
            center = dict(lat=latitude, lon=longitude);
            zoom = 4.5;
            bubbleTitle = "Average Daily Reach by Canadian City in " + provinceDetail[i].get("definition") + "<br><sup>(From " + str(start_date[0:10]) + " to " + str(end_date[0:10]) + ")</sup>";
            barTitle = "Average Daily Reach of Top 10 Canadian Cities in " + provinceDetail[i].get("definition") + "<br><sup>(From " + str(start_date[0:10]) + " to " + str(end_date[0:10]) + ")</sup>";
    
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

    figBar = px.bar(dff[0:10].sort_values(["Count","Location"], ascending=False), x="City", y="Count", color="Province", title=barTitle);

    return figBubble, figBar;