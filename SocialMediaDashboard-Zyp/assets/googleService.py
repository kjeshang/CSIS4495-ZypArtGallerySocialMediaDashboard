import gspread
import pandas as pd

sa = gspread.service_account(filename="Assets/zyp-art-gallery-62e00b2be4ff.json");

# sheet = "Test";
# worksheet = "Test";

def getDataframe(sheet, worksheet):
    global sa
    sh = sa.open(sheet);
    wks = sh.worksheet(worksheet);
    dataframe = pd.DataFrame(wks.get_all_records());
    return dataframe;

def getDataframe_listOfLists(sheet, worksheet):
    global sa
    sh = sa.open(sheet);
    wks = sh.worksheet(worksheet);
    # dataframe = pd.DataFrame(wks.get_all_records());
    listOfLists = wks.get_all_values();
    return listOfLists;