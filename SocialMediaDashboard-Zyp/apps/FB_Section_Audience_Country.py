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

import sys

sys.path.append(".")
from assets.googleService import getDataframe
from assets.FB_audienceMetrics import audienceCountryDetail

# Import Dataset --------------------------------------------------
df1 = pd.read_csv("data/ZypFacebook_Audience-Country1.csv", index_col=False);
df2 = pd.read_csv("data/ZypFacebook_Audience-Country2.csv", index_col=False);
df_iso_alpha_Final = pd.read_csv("assets/CountryCode-iso_alpha_Final.csv", index_col=False);

# sheet1 = "ZypFacebook_Audience-Country1";
# worksheet1 = "ZypFacebook_Audience-Country1";
# df1 = getDataframe(sheet1, worksheet1);

# sheet2 = "ZypFacebook_Audience-Country2";
# worksheet2 = "ZypFacebook_Audience-Country2";
# df2 = getDataframe(sheet2, worksheet2);

# sheet_iso_alpha = "CountryCode-iso_alpha_Final";
# worksheet_iso_alpha = "CountryCode-iso_alpha_Final";
# df_iso_alpha_Final = getDataframe(sheet_iso_alpha, worksheet_iso_alpha);

# Prepare Data --------------------------------------------
df1["end_time"] = pd.to_datetime(df1["end_time"]);
df2["end_time"] = pd.to_datetime(df2["end_time"]);

# Create elements of the webpage ----------------------------------

# Title of webpage:
countrySectionHeading = [html.H1("Facebook Audience Insights - Country", style={"font-weight":"bold"})];

# Date range filter:
countryDateRangeFilter = [
    html.P("Date Range", style={"font-weight":"bold"}),
    dcc.DatePickerRange(
        id="FB_country_date-range",
        min_date_allowed=df1["end_time"][len(df1)-1],
        max_date_allowed=df1["end_time"][0],
        start_date=df1["end_time"][0] - timedelta(30),
        end_date=df1["end_time"][0],
        updatemode="bothdates"
    )
];

# Region scope radio button selector:
regionScopeRadioButtonSelector = [
    html.P("Region Scope", style={"font-weight":"bold"}),
    dcc.RadioItems(
        id="FB_country_region_scope",
        options=[{"label":x, "value":x} for x in df_iso_alpha_Final["Region"].unique().tolist()],
        value="World",
        inputStyle={"margin-right":"5px", "margin-left":"15px"}
    )
];

# Lifetime likes by country choropleth:
countryChoropleth_1 = dcc.Graph(id="FB_country_choropleth_1", figure={}, config={'displayModeBar':False});

# Lifetime likes by country bar chart (top 10):
countryBarChart_1 = dcc.Graph(id="FB_country_chart_1", figure={}, config={'displayModeBar':False});

# Daily reach by country choropleth:
countryChoropleth_2 = dcc.Graph(id="FB_country_choropleth_2", figure={}, config={'displayModeBar':False});

# Daily reach by country bar chart (top 10):
countryBarChart_2 = dcc.Graph(id="FB_country_chart_2", figure={}, config={'displayModeBar':False});

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
        id="FB_collapse-button-country",
        className="mb-3",
        n_clicks=0,
    ),
    dbc.Collapse(
        dbc.Table.from_dataframe(createCountryMetricReferenceDataframe(), striped=True, bordered=True, hover=True),
        id="FB_collapse-country",
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
                        dbc.CardBody(children=countryDateRangeFilter)
                    ])
                ], width=5),
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=regionScopeRadioButtonSelector)
                    ])
                ], width=7)
            ]),
            html.Br(),
            dbc.Row(children=[
                dcc.Tabs(children=[
                    dcc.Tab(label=audienceCountryDetail[0].get("title"), children=[
                        dbc.Row(children=[
                            dbc.Col(children=[countryBarChart_1], width=5),
                            dbc.Col(children=[countryChoropleth_1], width=7)
                        ])
                    ]),
                    dcc.Tab(label=audienceCountryDetail[1].get("title"), children=[
                        dbc.Row(children=[
                            dbc.Col(children=[countryBarChart_2], width=5),
                            dbc.Col(children=[countryChoropleth_2], width=7)
                        ])
                    ])
                ])
            ]),
            html.Br(),
            dbc.Row(children=countryMetricReference)
        ])
    ])
];

# Finalizing the layout:
countryLayout = dbc.Container(children=countryStructure, fluid=True);

# Callbacks --------------------------------------------------------

# Render country reference section of the webpage:
@callback(
    Output("FB_collapse-country", "is_open"),
    [Input("FB_collapse-button-country", "n_clicks")],
    [State("FB_collapse-country", "is_open")],
)
def toggle_collapse_country(n, is_open):
    if n:
        return not is_open
    return is_open

# Lifetime Likes by Country Tab  ****************************************

def set_dataframeForCountryCharts1(dataframe, mask):
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

    countries1 = df.columns.tolist()[1:];

    data = [];
    for i in range(len(countries1)):
        row = [];
        row.append(countries1[i]);
        for j in df_iso_alpha_Final.index:
            if df_iso_alpha_Final.loc[j, "Country"] == countries1[i]:
                row.append(df_iso_alpha_Final.loc[j, "Code"]);
                row.append(df_iso_alpha_Final.loc[j, "Region"]);
        row.append(df[mask].transpose()[1:][index][i]);
        data.append(row);

    dff = pd.DataFrame(data, columns=["Country","iso_alpha","Region","Count"]); 
    return dff;

# Callback for lifetime likes top ten countries bar chart:
@callback(
    Output("FB_country_chart_1", "figure"),
    [
        Input("FB_country_date-range", "end_date"),
        Input("FB_country_region_scope", "value")
    ],  
)
def get_countryBarChart1(end_date, region_scope):
    mask = df1["end_time"] == end_date;
    df = set_dataframeForCountryCharts1(df1, mask);
    
    df = df.sort_values(["Count","Country"], ascending=False);
    if region_scope == "World":
        filter = (df["Count"] != '') & (df["Count"].notna()) & (df["Count"].notnull());
    else:
        filter = (df["Count"] != '') & (df["Count"].notna()) & (df["Count"].notnull()) & (df["Region"] == region_scope);
    dff = df[filter][0:10].copy();
    dff = dff.sort_values("Count", ascending=True);
    
    title = "Aggregated Lifetime Likes of Top 10 Countries <br><sup>(As of " + str(end_date[0:10]) + ")</sup>";
    fig = px.bar(dff, x="Count", y="Country", title=title, orientation='h');

    return fig;

# Callback for lifetime likes country choloropeth chart:
@callback(
    Output("FB_country_choropleth_1", "figure"),
    [
        Input("FB_country_date-range", "end_date"),
        Input("FB_country_region_scope", "value")
    ],  
)
def get_countryChoropleth1(end_date, region_scope):
    mask = df1["end_time"] == end_date;
    dff = set_dataframeForCountryCharts1(df1, mask);

    fig = go.Figure(data=go.Choropleth(
        locations = dff['iso_alpha'],
        z = dff['Count'],
        text = dff['Country'],
        colorbar_title = "Count",
    ));

    title = "Aggregated Lifetime Likes by Country <br><sup>(As of " + str(end_date[0:10]) + ")</sup>";

    fig.update_layout(
        title_text = title,
        geo = dict(
            projection = {'type':'natural earth'},
            scope = region_scope.lower()
        )
    );
    return fig;

# Daily Reach by Country Tab  ****************************************

def set_dataframeForCountryCharts2(dataframe, mask):
    df = dataframe[mask].copy();

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

    df = df.loc[:,~df.columns.duplicated()]
    df = df.replace(r'^\s*$', np.NaN, regex=True);
    df = df.fillna(0)
    df = df.loc[:,~df.columns.duplicated()]

    data = [];
    row = [];
    for country in df.columns.tolist()[1:]:
        avg = round(np.average(df[country]), 2);
        row.append(avg);
    data.append(row);
    dfTemp = pd.DataFrame(data, columns=df.columns.tolist()[1:]);

    index = dfTemp.index.values.astype(int)[0];

    countries = dfTemp.columns.tolist();

    data = [];
    for i in range(len(countries)):
        row = [];
        row.append(countries[i]);
        for j in df_iso_alpha_Final.index:
            if df_iso_alpha_Final.loc[j, "Country"] == countries[i]:
                row.append(df_iso_alpha_Final.loc[j, "Code"]);
                row.append(df_iso_alpha_Final.loc[j, "Region"]);
        row.append(dfTemp.transpose()[index][i]);
        data.append(row);
    dff = pd.DataFrame(data, columns=["Country","iso_alpha","Region", "Count"]);

    return dff;

# Callback for average daily reach of top ten countries bar chart:
@callback(
    Output("FB_country_chart_2", "figure"),
    [
        Input("FB_country_date-range", "start_date"),
        Input("FB_country_date-range", "end_date"),
        Input("FB_country_region_scope", "value")
    ],  
)
def get_countryBarChart2(start_date, end_date, region_scope):
    mask = (df2["end_time"] >= start_date) & (df2["end_time"] <= end_date);
    df = set_dataframeForCountryCharts2(df2, mask);
    
    df = df.sort_values(["Count","Country"], ascending=False);
    # filter = (df["Count"] != '') & (df["Count"].notna()) & (df["Count"].notnull());
    # dff = df[filter][0:10].copy();
    if region_scope == "World":
        dff = df[0:10].copy();
    else:
        filter = df["Region"] == region_scope;
        dff = df[filter][0:10].copy();
    dff = dff.sort_values("Count", ascending=True);
    
    title = "Average Daily Reach of Top 10 Countries <br><sup>(From " + str(start_date[0:10]) + " to " + str(end_date[0:10]) + ")</sup>";
    fig = px.bar(dff, x="Count", y="Country", title=title, orientation='h');

    return fig;

# Callback for average daily reach of countries choropleth:
@callback(
    Output("FB_country_choropleth_2", "figure"),
    [
        Input("FB_country_date-range", "start_date"),
        Input("FB_country_date-range", "end_date"),
        Input("FB_country_region_scope", "value")
    ],  
)
def get_countryChoropleth2(start_date, end_date, region_scope):
    mask = (df2["end_time"] >= start_date) & (df2["end_time"] <= end_date);
    dff = set_dataframeForCountryCharts2(df2, mask);
    
    fig = go.Figure(data=go.Choropleth(
        locations = dff['iso_alpha'],
        z = dff['Count'],
        text = dff['Country'],
        colorbar_title = "Count",
    ));

    title = "Average Daily Reach by Country <br><sup>(From " + str(start_date[0:10]) + " to " + str(end_date[0:10]) + ")</sup>";

    fig.update_layout(
        title_text = title,
        geo = dict(
            projection = {'type':'natural earth'},
            scope = region_scope.lower()
        )
    );

    return fig;