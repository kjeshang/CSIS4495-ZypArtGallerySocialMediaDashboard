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
from assets.IG_audienceMetrics import audienceAgeGenderDetail

# Import Dataset --------------------------------------------------
# df = pd.read_csv("data/ZypInstagram_Audience-Age&Gender.csv", index_col=False);

sheet = "ZypInstagram_Audience-Age&Gender";
worksheet = "ZypInstagram_Audience-Age&Gender";
# df = getDataframe(sheet, worksheet);
listOfLists = getDataframe_listOfLists(sheet, worksheet);
df = pd.DataFrame(listOfLists[1:], columns=listOfLists[0])

# Prepare Data --------------------------------------------
df["end_time"] = pd.to_datetime(df["end_time"]);

ageRange = [];
genderID = [];
for ageGender in df.columns.tolist()[3:]:
    ageRange.append(ageGender[2:]);
    genderID.append(ageGender[0]);
ageRange = list(dict.fromkeys(ageRange));
genderID = list(dict.fromkeys(genderID));
genderNames = ["Female","Male","Undeclared"];

# Create elements of the webpage ----------------------------------

# Title of webpage:
ageGenderSectionHeading = [html.H1("Instagram Audience Insights - Age & Gender", style={"font-weight":"bold"})];

# Year dropdown filter:
yearDropdownFilter = [
    html.P("Year", style={"font-weight":"bold"}),
    dcc.Dropdown(
        id="IG_ageGender_year",
        options=[{"label":x, "value":x} for x in df["year"].unique().tolist()],
        value=df["year"].unique().tolist()[0],
        clearable=False,
        searchable=False
    )
];

# Week dropdown filter:
weekDropdownFilter = [
    html.P("Week", style={"font-weight":"bold"}),
    dcc.Dropdown(id="IG_ageGender_week", clearable=False, searchable=False)
];

# # End time tile:
# endTimeTile = [
#     html.P("The visualizations below reflect " + audienceAgeGenderDetail[3].get("title") + " data as of:"),
#     html.H5(id="IG_ageGender_endTime", style={"font-weight":"bold"})
# ];

# Gender identity checklist filter:
genderChecklistFilter = [
    html.P("Gender Identity", style={"font-weight":"bold"}),
    dcc.Checklist(
        id="IG_gender_id",
        options=[{"label":genderNames[x], "value":x} for x in range(len(genderNames))],
        value=[0,1,2],
        inputStyle={"margin-right": "5px", "margin-left":"15px"}
    )
];

# Age range dropdown filter:
ageDropdownFilter = [
    html.P("Age Range", style={"font-weight":"bold"}),
    dcc.Dropdown(
        id="IG_age_range",
        options=[{"label":ageRange[x], "value":x} for x in range(len(ageRange))],
        value=[0,1,2,3,4,5,6],
        multi=True
    )
];

# Gender identity pie chart:
genderPieChart = dcc.Graph(id="IG_gender_chart", figure={}, config={"displayModeBar":False});

# Age range bar chart:
ageBarChart = dcc.Graph(id="IG_age_range_chart", figure={}, config={"displayModeBar":False});

# Audience age & gender metric reference dataframe:
def createAgeGenderMetricReferenceDataframe():
    data = [];
    for i in range(len(audienceAgeGenderDetail)):
        row = [];
        row.append(audienceAgeGenderDetail[i].get("metric"));
        row.append(audienceAgeGenderDetail[i].get("title"));
        row.append(audienceAgeGenderDetail[i].get("description"));
        data.append(row);
    df = pd.DataFrame(data, columns=["Metric","Title","Description"]);
    return df;

# Create age & gender metric reference section of webpage:
ageGenderMetricReference = [
    dbc.Button(
        "Metric Reference",
        id="IG_collapse-button-ageGender",
        className="mb-3",
        n_clicks=0,
    ),
    dbc.Collapse(
        dbc.Table.from_dataframe(createAgeGenderMetricReferenceDataframe(), striped=True, bordered=True, hover=True),
        id="IG_collapse-ageGender",
        is_open=False,
    )
];

# Page layout -----------------------------------------------------

# Structure:
ageGenderStructure = [
    dbc.Row(children=ageGenderSectionHeading),
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
                        dbc.CardBody(children=genderChecklistFilter)
                    ])
                ], width=2),
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=ageDropdownFilter)
                    ])
                ], width=6)
            ]),
            # html.Br(),
            dbc.Row(children=[
                dbc.Col(children=[genderPieChart], width=5),
                dbc.Col(children=[ageBarChart], width=7)
            ]),
            html.Br(),
            dbc.Row(children=ageGenderMetricReference)
        ])
    ])
];

# Finalizing the layout:
ageGenderLayout = dbc.Container(children=ageGenderStructure, fluid=True);

# Callbacks --------------------------------------------------------

@callback(
    Output("IG_ageGender_week", "options"),
    Output("IG_ageGender_week", "value"),
    [
        Input("IG_ageGender_year", "value")
    ]
)
def get_WeekDropdownFilter(year_select):
    yearMask = df["year"] == year_select;
    options = [{"label":x, "value":x} for x in df[yearMask]["week"].unique().tolist()];
    value = df[yearMask]["week"].unique().tolist()[0];
    return options, value;

# Render age & gender reference section of the webpage:
@callback(
    Output("IG_collapse-ageGender", "is_open"),
    [Input("IG_collapse-button-ageGender", "n_clicks")],
    [State("IG_collapse-ageGender", "is_open")],
)
def toggle_collapse_ageGender(n, is_open):
    if n:
        return not is_open
    return is_open

# Gender Chart Functions ***************************************************
def set_DataframeForGenderChart(mask, ageRangeSelected, aggFunc):
    index = df[mask].index.values.astype(int)[0];

    data = [];
    femaleRow = ["Female"];
    for i in range(0,7):
        femaleRow.append(df[mask].transpose()[3:][index][i]);
    maleRow = ["Male"];
    for i in range(7,14):
        maleRow.append(df[mask].transpose()[3:][index][i]);
    undeclaredRow = ["Undeclared"];
    for i in range(14,len(df[mask].transpose()[3:])):
        undeclaredRow.append(df[mask].transpose()[3:][index][i]);
    data.append(femaleRow);
    data.append(maleRow);
    data.append(undeclaredRow);

    labels = ["Gender"];
    for lbl in ageRange:
        labels.append(lbl);
    initialPivot = pd.DataFrame(data, columns=labels);

    selectedLabels = ["Gender"];
    for lbl in ageRangeSelected:
        selectedLabels.append(lbl);
    basePivot = initialPivot[selectedLabels];

    data = [];
    for i in basePivot.index:
        totalPerGender = 0;
        row = ["All Genders"];
        totalPerAge = 0;
        for age in ageRangeSelected:
            totalPerGender += basePivot.loc[i, age];
            row.append(aggFunc(basePivot[age]));
            totalPerAge += aggFunc(basePivot[age]);
        basePivot.loc[i, "Total"] = totalPerGender;
        row.append(totalPerAge);
    data.append(row);
    tempPivot = pd.DataFrame(data, columns=basePivot.columns.tolist());

    finalPivot = pd.concat([basePivot, tempPivot], ignore_index=True);

    return finalPivot;

def createGenderPieChart(df_pivot, gender_id, values, title):
    # Adjust dataframe based on gender identities selected from the respective checklist
    if len(gender_id) == 3:
        dff = df_pivot[0:3];
    elif len(gender_id) == 2:
        dff = df_pivot[(df_pivot["Gender"] == genderNames[gender_id[0]]) | (df_pivot["Gender"] == genderNames[gender_id[1]])];
    elif len(gender_id) == 1:
        dff = df_pivot[df_pivot["Gender"] == genderNames[gender_id[0]]];
    else:
        dff = df_pivot[df_pivot["Gender"] == "All Genders"];
    
    # Create pie chart
    fig = px.pie(dff, names="Gender", values=values, title=title);

    return fig;

# Age Chart Functions ***************************************************
def set_dataframeForAgeChart(mask, ageRangeSelected, aggFunc):
    index = df[mask].index.values.astype(int)[0];
    
    data = [];
    for i in range(len(df[mask].transpose()[3:])):
        try:
            row = [];
            row.append(ageRange[i]);
            row.append(df[mask].transpose()[3:][index][i]);
            row.append(df[mask].transpose()[3:][index][i+7]);
            row.append(df[mask].transpose()[3:][index][i+14]);
            data.append(row);
        except:
            # print("Done");
            break;
    
    labels = ["Age Range"];
    for lbl in genderNames:
        labels.append(lbl);
    initialPivot = pd.DataFrame(data, columns=labels);
    basePivot = initialPivot.iloc[ageRangeSelected];

    basePivot["Total"] = 0;
    data = [];
    for i in basePivot.index:
        totalPerAge = 0;
        row = ["All Ages"];
        totalPerGender = 0;
        for gender in genderNames:
            totalPerAge += basePivot.loc[i, gender];
            row.append(aggFunc(basePivot[gender]));
            totalPerGender += aggFunc(basePivot[gender]);
        basePivot.loc[i, "Total"] = totalPerAge;
        row.append(totalPerGender);
    data.append(row);
    tempPivot = pd.DataFrame(data, columns=basePivot.columns.tolist());

    finalPivot = pd.concat([basePivot, tempPivot], ignore_index=True);

    return finalPivot;

def createAgeBarChart(df_pivot, gender_id, age_range, title, labels):
    lastCol = df_pivot.columns.tolist()[len(df_pivot.columns.tolist())-1];
    
    # Retrieve gender selections from gender checklist
    genderSelected = [];
    for i in gender_id:
        genderSelected.append(genderNames[i]);
    
    # Adjust dataframe based on gender identities and age ranges selected
    if len(gender_id) == 0 and len(age_range) > 0:
        dff = df_pivot[:-1];
        fig = px.bar(dff, x="Age Range", y=[lastCol], barmode="group", title=title, labels=labels);
    elif len(gender_id) > 0 and len(age_range) == 0:
        dff = df_pivot[df_pivot["Age Range"] == "All Ages"];
        fig = px.bar(dff, x="Age Range", y=genderSelected, barmode="group", title=title, labels=labels);
    elif len(gender_id) == 0 and len(age_range) == 0:
        dff = df_pivot[df_pivot["Age Range"] == "All Ages"];
        fig = px.bar(dff, x="Age Range", y=[lastCol], barmode="group", title=title, labels=labels);
    else:
        dff = df_pivot[:-1];
        fig = px.bar(dff, x="Age Range", y=genderSelected, barmode="group", title=title, labels=labels);
    
    fig = fig.update_layout(legend_title_text="Gender");
    
    return fig;

# Age & Gender Callback *****************************************************************************
@callback(
    Output("IG_gender_chart", "figure"),
    Output("IG_age_range_chart", "figure"),
    [
        Input("IG_ageGender_year", "value"),
        Input("IG_ageGender_week", "value"),
        Input("IG_gender_id", "value"),
        Input("IG_age_range", "value")
    ]
)
def get_IGAgeGenderVisualizations(year_select, week_select, gender_id, age_range):
    mask = (df["year"] == year_select) & (df["week"] == week_select);
    index = df[mask].index.values.astype(int)[0];
    end_time = str(df[mask].loc[index, "end_time"]).split(" ")[0];
    
    # Gender Chart:
    if len(age_range) == 0:
        df_pivotGender = set_DataframeForGenderChart(mask, ageRange, aggFunc=np.sum);
    else:
        ageRangeSelected = [];
        for i in age_range:
            ageRangeSelected.append(ageRange[i]);
        df_pivotGender = set_DataframeForGenderChart(mask, ageRangeSelected, aggFunc=np.sum);
    
    values = "Total";
    titleGender = "Distribution of Followers by Gender<br><sup>(As of " + end_time + ")</sup>";
    figGender = createGenderPieChart(df_pivotGender, gender_id, values, titleGender);

    # Age Chart:
    if len(age_range) != 0:
        df_pivotAge = set_dataframeForAgeChart(mask, age_range, aggFunc=np.sum);
    else:
        df_pivotAge = set_dataframeForAgeChart(mask, [0,1,2,3,4,5,6], aggFunc=np.sum);
    
    titleAge = "Distribution of Followers by Age<br><sup>(As of " + end_time + ")</sup>";
    labels = {'value':'Count'};
    figAge = createAgeBarChart(df_pivotAge, gender_id, age_range, titleAge, labels);
    return figGender, figAge;