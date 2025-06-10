import pandas as pd
import numpy as np
from pathlib import Path
from pandas.errors import EmptyDataError
import ast
import re

water_data_df = pd.read_csv("dri_data.csv", index_col = "DRI Number")
dri_list = water_data_df.index.to_list()
#data_center_df = pd.DataFrame(columns = ["Current Status", "Contains 'data center'?", "Water Usage", "Data Center?"], index = water_data_df.index)
file_path = Path("data_center.csv")
if file_path.exists() and file_path.is_file():
    try:
        data_center_df = pd.read_csv("data_center.csv", index_col = "DRI Number")
        data_center_df.index = water_data_df.index
    except EmptyDataError:
        print("CSV file exists but is empty. Initializing new DataFrame.")
        data_center_df = pd.DataFrame(columns = ["Project Name", "Current Status", "Contains 'data center'?", "Water Usage", "Data Center?"], index = water_data_df.index)
        data_center_df.index = water_data_df.index
        data_center_df["Data Center?"] = water_data_df["Data Center?"]
        #data_center_df.set_index("DRI Number", inplace = True)
else:
    print("No existing CSV file found, creating new one.")
    file_path.touch()
    data_center_df = pd.DataFrame(columns = ["Project Name", "Current Status", "Contains 'data center'?", "Water Usage", "Data Center?"], index = water_data_df.index)
    data_center_df.index = water_data_df.index
    data_center_df["Data Center?"] = water_data_df["Data Center?"]
data_center_df.insert(4, 'Cleaned Water Usage Data', np.nan)
data_center_df["Current Status"] = water_data_df["Current Status"]

#'''
water_data_df["Project info"] = water_data_df["Project info"].apply(ast.literal_eval)
for dri in dri_list:
    #print(data_center_df.loc[dri, "Data Center?"])
    #print(data_center_df.loc[dri, "Data Center?"] == "TBD")
    if pd.isna(data_center_df.loc[dri, "Project Name"]):
         data_center_df.loc[dri, "Project Name"] = water_data_df.loc[dri, "Project info"][0][1]

    if data_center_df.loc[dri, "Data Center?"] == "TBD":
        project_info = water_data_df.loc[dri, "Project info"]
        project_description = project_info[2][1].lower()
        #print(project_description)
        if 'data center' in project_description:
            data_center_df.loc[dri, "Contains 'data center'?"] = 1
        elif 'datacenter' in project_description:
            data_center_df.loc[dri, "Contains 'data center'?"] = 1
        else:
            data_center_df.loc[dri, "Contains 'data center'?"] = 0
        try:
            if 'n/a' in project_info[13][1].lower():
                s = project_info[13][1].lower()
                data_center_df.loc[dri, "Water Usage"] = "No water data"
                data_center_df.loc[dri, "Cleaned Water Usage Data"] = "No water data"
            elif 'mgd' in project_info[13][1].lower():
                s = project_info[13][1].lower()

                data_center_df.loc[dri, "Cleaned Water Usage Data"] = (re.split(r"\bmgd\b", s, flags = re.IGNORECASE)[0].strip())
            elif 'mgpd' in project_info[13][1].lower():
                s = project_info[13][1].lower()
                data_center_df.loc[dri, "Cleaned Water Usage Data"] = (re.split(r"\bmgpd\b", s, flags = re.IGNORECASE)[0].strip())
            else:
                data_center_df.loc[dri, "Cleaned Water Usage Data"] = project_info[13][1].lower()
                '''
            if 'gpd' in project_info[13][1].lower():
                s = project_info[13][1].lower()
                data_center_df.loc[dri, "Water Usage"] = (re.split(r"\bgpd\b", s, flags = re.IGNORECASE)[0].strip())/1000000
            elif 'gallons per day' in project_info[13][1].lower():
                s = project_info[13][1].lower()
                data_center_df.loc[dri, "Water Usage"] = (re.split(r"\bgallons per day\b", s, flags = re.IGNORECASE)[0].strip())
                '''
        except IndexError:
            data_center_df.loc[dri, "Cleaned Water Usage Data"] = "No water data"
                
data_center_df.to_csv("data_center.csv", index = True)
print(data_center_df)
print(data_center_df["Contains 'data center'?"].sum())
