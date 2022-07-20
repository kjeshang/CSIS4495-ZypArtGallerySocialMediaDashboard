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

import sys

sys.path.append(".")
from assets.googleService import getDataframe_listOfLists, getDataframe
from assets.FB_audienceMetrics import audienceAgeGenderDetail

# Import Dataset --------------------------------------------------
# df1 = pd.read_csv("data/ZypFacebook_Audience-Age&Gender1.csv", index_col=False);
# df2 = pd.read_csv("data/ZypFacebook_Audience-Age&Gender2.csv", index_col=False);

sheet1 = "ZypFacebook_Audience-Age&Gender1";
worksheet1 = "ZypFacebook_Audience-Age&Gender1";
df1 = getDataframe(sheet1, worksheet1);
# listOfLists1 = getDataframe_listOfLists(sheet1, worksheet1);
# df1 = pd.DataFrame(listOfLists1[1:], columns=listOfLists1[0])

sheet2 = "ZypFacebook_Audience-Age&Gender2";
worksheet2 = "ZypFacebook_Audience-Age&Gender2";
df2 = getDataframe(sheet2, worksheet2);
# listOfLists2 = getDataframe_listOfLists(sheet2, worksheet2);
# df2 = pd.DataFrame(listOfLists2[1:], columns=listOfLists2[0])

# Prepare Data --------------------------------------------
df1["end_time"] = pd.to_datetime(df1["end_time"]);
df2["end_time"] = pd.to_datetime(df2["end_time"]);

ageRange = [];
genderID = [];
for ageGender in df1.columns.tolist()[1:]:
    ageRange.append(ageGender[2:]);
    genderID.append(ageGender[0]);
ageRange = list(dict.fromkeys(ageRange));
genderID = list(dict.fromkeys(genderID));
genderNames = ["Female","Male","Undeclared"];

# Create elements of the webpage ----------------------------------

# Title of webpage:
ageGenderSectionHeading = [html.H1("Facebook Audience Insights - Age & Gender", style={"font-weight":"bold"})];

# Date range filter:
ageGenderDateRangeFilter = [
    html.P("Date Range", style={"font-weight":"bold"}),
    dcc.DatePickerRange(
        id="FB_ageGender_date-range",
        min_date_allowed=df1["end_time"][len(df1)-1],
        max_date_allowed=df1["end_time"][0],
        start_date=df1["end_time"][0] - timedelta(30),
        end_date=df1["end_time"][0],
        updatemode="bothdates"
    )
];

# Gender type dropdown filter:
genderChecklistFilter = [
    html.P("Gender Identity", style={"font-weight":"bold"}),
    dcc.Checklist(
        id="FB_gender_id",
        options=[{"label":genderNames[x], "value":x} for x in range(len(genderNames))],
        value=[0,1,2],
        inputStyle={"margin-right": "5px", "margin-left":"15px"}
    )
];

# Age range dropdown filter:
ageDropdownFilter = [
    html.P("Age Range", style={"font-weight":"bold"}),
    dcc.Dropdown(
        id="FB_age_range",
        options=[{"label":ageRange[x], "value":x} for x in range(len(ageRange))],
        value=[0,1,2,3,4,5,6],
        multi=True
    )
];

# Gender identity pie chart for lifetime likes:
genderPieChart_1 = dcc.Graph(id="FB_gender_chart_1", figure={}, config={"displayModeBar":False});

# Age range side-by-side bar chart for lifetime likes:
ageBarChart_1 = dcc.Graph(id="FB_age_range_chart_1", figure={}, config={"displayModeBar":False});

# Gender identity pie chart for daily reach demographics:
genderPieChart_2 = dcc.Graph(id="FB_gender_chart_2", figure={}, config={"displayModeBar":False});

# Age range side-by-side bar chart for lifetime likes:
ageBarChart_2 = dcc.Graph(id="FB_age_range_chart_2", figure={}, config={"displayModeBar":False});

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
        id="FB_collapse-button-ageGender",
        className="mb-3",
        n_clicks=0,
    ),
    dbc.Collapse(
        dbc.Table.from_dataframe(createAgeGenderMetricReferenceDataframe(), striped=True, bordered=True, hover=True),
        id="FB_collapse-ageGender",
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
                        dbc.CardBody(children=ageGenderDateRangeFilter)
                    ])
                ], width=4),
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=genderChecklistFilter)
                    ])
                ], width=3),
                dbc.Col(children=[
                    dbc.Card(children=[
                        dbc.CardBody(children=ageDropdownFilter)
                    ])
                ], width=5)
            ]),
            html.Br(),
            dbc.Row(children=[
                dcc.Tabs(children=[
                    dcc.Tab(label=audienceAgeGenderDetail[0].get("title"), children=[
                        dbc.Row(children=[
                            dbc.Col(children=[genderPieChart_1], width=5),
                            dbc.Col(children=[ageBarChart_1], width=7)
                        ])
                    ]),
                    dcc.Tab(label=audienceAgeGenderDetail[1].get("title"), children=[
                        dbc.Row(children=[
                            dbc.Col(children=[genderPieChart_2], width=5),
                            dbc.Col(children=[ageBarChart_2], width=7)
                        ])
                    ])
                ])
            ]),
            html.Br(),
            dbc.Row(children=ageGenderMetricReference)
        ])
    ])
];

# Finalizing the layout:
ageGenderLayout = dbc.Container(children=ageGenderStructure, fluid=True);

# Callbacks --------------------------------------------------------

# Function to render pie chart
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

# Function to render age range bar chart
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

# Render age & gender reference section of the webpage:
@callback(
    Output("FB_collapse-ageGender", "is_open"),
    [Input("FB_collapse-button-ageGender", "n_clicks")],
    [State("FB_collapse-ageGender", "is_open")],
)
def toggle_collapse_ageGender(n, is_open):
    if n:
        return not is_open
    return is_open

# Lifetime Likes by Age & Gender Tab - Gender ****************************************

def set_dataframeForGenderChart1(mask, ageRangeSelected, aggFunc):
    # Get the row index to use based on the end date selected
    index = df1[mask].index.values.astype(int)[0];

    # Retrieve age & gender data and save it in another list
    data = [];
    femaleRow = ["Female"];
    for i in range(0,7):
        femaleRow.append(df1[mask].transpose()[1:][index][i]);
    maleRow = ["Male"];
    for i in range(7,14):
        maleRow.append(df1[mask].transpose()[1:][index][i]);
    undeclaredRow = ["Undeclared"];
    for i in range(14,len(df1[mask].transpose()[1:])):
        undeclaredRow.append(df1[mask].transpose()[1:][index][i]);
    data.append(femaleRow);
    data.append(maleRow);
    data.append(undeclaredRow);

    # Construct a base pivot table dataframe from the recently retrieved data
    labels = ["Gender"];
    for lbl in ageRange:
        labels.append(lbl);
    initialPivot = pd.DataFrame(data, columns=labels);
    
    selectedLabels = ["Gender"];
    for lbl in ageRangeSelected:
        selectedLabels.append(lbl);
    basePivot = initialPivot[selectedLabels];

    # Calculate totals by gender, selected age ranges, & overall, and then create a temporary dataframe
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

    # Combine the base dataframe with the temporary dataframe to create the final dataframe that creates the final version of the pivot table (which includes the aggregated totals by age, gender, & overall)
    finalPivot = pd.concat([basePivot, tempPivot], ignore_index=True);

    return finalPivot;

@callback(
    Output("FB_gender_chart_1", "figure"),
    [
        Input("FB_ageGender_date-range", "end_date"),
        Input("FB_gender_id", "value"),
        Input("FB_age_range", "value")
    ]
)
def get_genderChart1(end_date, gender_id, age_range):
    # Filter dataframe by end date selected from date range date picker
    mask = df1["end_time"] == end_date;

     # Create pivot dataframe based on selections made in gender checklist and age range dropdown
    if len(age_range) == 0:
        df_pivot = set_dataframeForGenderChart1(mask, ageRange, aggFunc=np.sum);
    else:
        ageRangeSelected = [];
        for i in age_range:
            ageRangeSelected.append(ageRange[i]);
        df_pivot = set_dataframeForGenderChart1(mask, ageRangeSelected, aggFunc=np.sum);

    # Adjust dataframe based on gender identities selected from the respective checklist, and create pie chart
    values = "Total";
    title = "Aggregated Lifetime Likes by Gender";
    fig = createGenderPieChart(df_pivot, gender_id, values, title);

    accurateTitle = title + "<br><sup>(As of " + str(end_date[0:10]) + ")</sup>";
    fig.update_layout(title={'text': accurateTitle});

    return fig;

# Lifetime Likes by Age & Gender Tab - Age **********************************************

def set_dataframeForAgeChart1(mask, ageRangeSelected, aggFunc):
    # Get the row index to use based on the end date selected
    index = df1[mask].index.values.astype(int)[0];
    
    # Retrieve age & gender data and save it in another list
    data = [];
    for i in range(len(df1[mask].transpose()[1:])):
        try:
            row = [];
            row.append(ageRange[i]);
            row.append(df1[mask].transpose()[1:][index][i]);
            row.append(df1[mask].transpose()[1:][index][i+7]);
            row.append(df1[mask].transpose()[1:][index][i+14]);
            data.append(row);
        except:
            # print("Done");
            break;
    
    # Construct a base pivot table dataframe from the recently retrieved data
    labels = ["Age Range"];
    for lbl in genderNames:
        labels.append(lbl);
    initialPivot = pd.DataFrame(data, columns=labels);
    basePivot = initialPivot.iloc[ageRangeSelected];

    # Calculate totals by gender, selected age ranges, & overall, and then create a temporary dataframe
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

    # Combine the base dataframe with the temporary dataframe to create the final dataframe that creates the final version of the pivot table (which includes the aggregated totals by age, gender, & overall)
    finalPivot = pd.concat([basePivot, tempPivot], ignore_index=True);

    return finalPivot;

@callback(
    Output("FB_age_range_chart_1", "figure"),
    [
        Input("FB_ageGender_date-range", "end_date"),
        Input("FB_gender_id", "value"),
        Input("FB_age_range", "value")
    ]
)
def get_ageChart1(end_date, gender_id, age_range):
    # Filter dataframe by end date selected from date range date picker
    mask = df1["end_time"] == end_date;
    
    # Create pivot dataframe based on selections made in age range dropdown
    if len(age_range) != 0:
        df_pivot = set_dataframeForAgeChart1(mask, age_range, aggFunc=np.sum);
    else:
        df_pivot = set_dataframeForAgeChart1(mask, [0,1,2,3,4,5,6], aggFunc=np.sum);
    
    # Adjust dataframe based on gender identities selected from the respective checklist, and then create side-by-side bar chart
    title = "Aggregated Lifetime Likes by Age";
    labels = {'value':'Count'};

    fig = createAgeBarChart(df_pivot, gender_id, age_range, title, labels);

    accurateTitle = title + "<br><sup>(As of " + str(end_date[0:10]) + ")</sup>";
    fig.update_layout(title={'text': accurateTitle});
    
    return fig;

# Daily Reach Demographics Tab - Gender ****************************************

def set_dataframeForGenderChart2(mask, ageRangeSelected, aggFunc):
    data = [];
    femaleRow = ["Female"];
    for col in df2[mask].columns.tolist()[1:][0:7]:
        femaleRow.append(round(aggFunc(df2[mask][col]), 2));
    maleRow = ["Male"];
    for col in df2[mask].columns.tolist()[1:][7:14]:
        maleRow.append(round(aggFunc(df2[mask][col]), 2));
    undeclaredRow = ["Undeclared"];
    for col in df2[mask].columns.tolist()[1:][14:]:
        undeclaredRow.append(round(aggFunc(df2[mask][col]), 2));
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

    for i in basePivot.index:
        basePivot.loc[i, "Average"] = round(aggFunc(basePivot.loc[i, ageRangeSelected]), 2);
    
    data = [];
    row = ["All Genders"];
    for age in basePivot.columns.tolist()[1:]:
        row.append(round(aggFunc(basePivot[age]), 2));
    data.append(row);
    tempPivot = pd.DataFrame(data, columns=basePivot.columns.tolist());

    finalPivot = pd.concat([basePivot, tempPivot], ignore_index=True);

    return finalPivot;

@callback(
    Output("FB_gender_chart_2","figure"),
    [
        Input("FB_ageGender_date-range", "start_date"),
        Input("FB_ageGender_date-range", "end_date"),
        Input("FB_gender_id", "value"),
        Input("FB_age_range", "value")
    ],
)
def get_genderChart2(start_date, end_date, gender_id, age_range):
    mask = (df2["end_time"] >= start_date) & (df2["end_time"] <= end_date);

    if len(age_range) == 0:
        df_pivot = set_dataframeForGenderChart2(mask, ageRange, aggFunc=np.average);
    else:
        ageRangeSelected = [];
        for i in age_range:
            ageRangeSelected.append(ageRange[i]);
        df_pivot = set_dataframeForGenderChart2(mask, ageRangeSelected, aggFunc=np.average);
    
    values = "Average";
    title = "Average Daily Total Page Reach by Gender";
    fig = createGenderPieChart(df_pivot, gender_id, values, title);

    accurateTitle = title + "<br><sup>(From " + str(start_date[0:10]) + " to " + str(end_date[0:10]) + ")</sup>";
    fig.update_layout(title={'text': accurateTitle});

    return fig;

# Daily Reach Demographics Tab - Age ****************************************

def set_dataframeForAgeChart2(mask, ageRangeSelected, aggFunc):
    index = df2[mask].index.values.astype(int)
    data = [];
    for i in range(len(df2[mask].transpose()[1:])):
        try:
            row = [];
            row.append(ageRange[i]);
            row.append(round(aggFunc(df2[mask].transpose()[1:].iloc[i, index]),2));
            row.append(round(aggFunc(df2[mask].transpose()[1:].iloc[i+7, index]),2));
            row.append(round(aggFunc(df2[mask].transpose()[1:].iloc[i+14, index]),2));
            data.append(row);
        except:
            # print("Done");
            break;
    
    labels = ["Age Range"];
    for lbl in genderNames:
        labels.append(lbl);    
    initialPivot = pd.DataFrame(data, columns=labels);
    basePivot = initialPivot.iloc[ageRangeSelected];

    for i in basePivot.index:
        basePivot.loc[i, "Average"] = round(aggFunc(basePivot.loc[i, genderNames]), 2);

    data = [];
    row = ["All Ages"];
    for gender in basePivot.columns.tolist()[1:]:
        row.append(round(aggFunc(basePivot[gender]),2));
    data.append(row);
    tempPivot = pd.DataFrame(data, columns=basePivot.columns.tolist());

    finalPivot = pd.concat([basePivot, tempPivot], ignore_index=True);

    return finalPivot;

@callback(
    Output("FB_age_range_chart_2","figure"),
    [
        Input("FB_ageGender_date-range", "start_date"),
        Input("FB_ageGender_date-range", "end_date"),
        Input("FB_gender_id", "value"),
        Input("FB_age_range", "value")
    ],
)
def get_ageChart2(start_date, end_date, gender_id, age_range):
    mask = (df2["end_time"] >= start_date) & (df2["end_time"] <= end_date);
    
    if len(age_range) != 0:
        df_pivot = set_dataframeForAgeChart2(mask, age_range, aggFunc=np.average);
    else:
        df_pivot = set_dataframeForAgeChart2(mask, [0,1,2,3,4,5,6], aggFunc=np.average);
    
    title = "Average Daily Total Page Reach by Age";
    labels = {'value':'Count'};
    fig = createAgeBarChart(df_pivot, gender_id, age_range, title, labels);

    accurateTitle = title + "<br><sup>(From " + str(start_date[0:10]) + " to " + str(end_date[0:10]) + ")</sup>";
    fig.update_layout(title={'text': accurateTitle});

    return fig;