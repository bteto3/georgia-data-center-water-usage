import pandas as pd
import numpy as np
from pathlib import Path
from pandas.errors import EmptyDataError
import ast
import re
#from geopy.geocoders import Nominatim
#from geopy.extra.rate_limiter import RateLimiter

#data_center_df = pd.DataFrame(columns = ["Current Status", "Contains 'data center'?", "Water Usage", "Data Center?"], index = water_data_df.index)
def water_data_post_processing():
    script_dir = Path(__file__).resolve().parent
    dri_data_path = script_dir.parent / "Data" / "dri_data.csv"
    dri_post_processing_path = script_dir.parent / "Data" / "dri_post_processing.csv"
    water_data_df = pd.read_csv(dri_data_path, index_col = "DRI Number")
    #file_path = Path("../Data/dri_post_processing.csv")
    if dri_post_processing_path.exists() and dri_post_processing_path.is_file():
        try:
            dri_post_processing_df = pd.read_csv(dri_post_processing_path, index_col = "DRI Number")
            #dri_post_processing_df.index = water_data_df.index
        except EmptyDataError:
            print("CSV file exists but is empty. Initializing new DataFrame.")
            dri_post_processing_df = pd.DataFrame(columns = ["Water Usage", "Project Name", "County", "Initial Info Form Submision Date", "Cleaned Water Usage Data", "Water Discharge Data", "Cleaned Water Discharge Data", "Contains 'data center'?", "Current Status", "Data Center?"], index = water_data_df.index)
            dri_post_processing_df.index = water_data_df.index
            dri_post_processing_df["Data Center?"] = water_data_df["Data Center?"]
            #data_center_df.set_index("DRI Number", inplace = True)
    else:
        print("No existing CSV file found, creating new one.")
        dri_post_processing_path.touch()
        dri_post_processing_df = pd.DataFrame(columns = ["Water Usage", "Project Name", "County", "Cleaned Water Usage Data", "Initial Info Form Submision Date", "Water Discharge Data", "Cleaned Water Discharge Data", "Contains 'data center'?", "Current Status", "Data Center?"], index = water_data_df.index)
        dri_post_processing_df.index = water_data_df.index
        dri_post_processing_df["Data Center?"] = water_data_df["Data Center?"]
    dri_post_processing_df["Current Status"] = water_data_df["Current Status"]

    #'''
    dri_list = water_data_df.index.to_list()
    post_processing_dri_list = dri_post_processing_df.index.to_list()
    dri_post_processing_df = dri_post_processing_df[["Water Usage", "Project Name", "County", "Initial Info Form Submision Date", "Cleaned Water Usage Data", "Water Discharge Data", "Cleaned Water Discharge Data", "Contains 'data center'?", "Current Status", "Data Center?"]]
    #dri_post_processing_df.index = water_data_df.index

    water_data_df["Project info"] = water_data_df["Project info"].apply(ast.literal_eval)
    for dri in dri_list:
        if dri not in post_processing_dri_list:
            dri_post_processing_df.loc[dri] = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        #print(data_center_df.loc[dri, "Data Center?"])
        #print(data_center_df.loc[dri, "Data Center?"] == "TBD")
        if pd.isna(dri_post_processing_df.loc[dri, "Project Name"]):
            dri_post_processing_df.loc[dri, "Project Name"] = water_data_df.loc[dri, "Project info"][0][1]

        if dri_post_processing_df.loc[dri, "Data Center?"] == "TBD":
            project_info = water_data_df.loc[dri, "Project info"]
            project_description = project_info[2][1].lower()
            #print(project_description)
            if 'data center' in project_description:
                dri_post_processing_df.loc[dri, "Contains 'data center'?"] = 1
            elif 'datacenter' in project_description:
                dri_post_processing_df.loc[dri, "Contains 'data center'?"] = 1
            else:
                dri_post_processing_df.loc[dri, "Contains 'data center'?"] = 0
              
            try:
                dri_post_processing_df.loc[dri, "Water Usage"] = project_info[13][1].lower()
                if 'n/a' in project_info[13][1].lower():
                    s = project_info[13][1].lower()
                    dri_post_processing_df.loc[dri, "Water Usage"] = "No water data"
                    dri_post_processing_df.loc[dri, "Cleaned Water Usage Data"] = "No water data"
                elif 'mgd' in project_info[13][1].lower():
                    s = project_info[13][1].lower()

                    dri_post_processing_df.loc[dri, "Cleaned Water Usage Data"] = (re.split(r"\bmgd\b", s, flags = re.IGNORECASE)[0].strip())
                elif 'mgpd' in project_info[13][1].lower():
                    s = project_info[13][1].lower()
                    dri_post_processing_df.loc[dri, "Cleaned Water Usage Data"] = (re.split(r"\bmgpd\b", s, flags = re.IGNORECASE)[0].strip())
                else:
                    dri_post_processing_df.loc[dri, "Cleaned Water Usage Data"] = project_info[13][1].lower()
                    '''
                if 'gpd' in project_info[13][1].lower():
                    s = project_info[13][1].lower()
                    data_center_df.loc[dri, "Water Usage"] = (re.split(r"\bgpd\b", s, flags = re.IGNORECASE)[0].strip())/1000000
                elif 'gallons per day' in project_info[13][1].lower():
                    s = project_info[13][1].lower()
                    data_center_df.loc[dri, "Water Usage"] = (re.split(r"\bgallons per day\b", s, flags = re.IGNORECASE)[0].strip())
                    '''
            except IndexError:
                dri_post_processing_df.loc[dri, "Water Usage"] = "No water data"
                dri_post_processing_df.loc[dri, "Cleaned Water Usage Data"] = "No water data"
            dri_post_processing_df["Cleaned Water Discharge Data"] = dri_post_processing_df["Cleaned Water Discharge Data"].astype("object")
            try:
                dri_post_processing_df.loc[dri, "Water Discharge Data"] = project_info[17][1].lower()
                if 'n/a' in project_info[17][1].lower():
                    s = project_info[17][1].lower()
                    dri_post_processing_df.loc[dri, "Water Discharge Data"] = "No water data"
                    dri_post_processing_df.loc[dri, "Cleaned Water Discharge Data"] = "No water data"
                elif 'mgd' in project_info[17][1].lower():
                    s = project_info[17][1].lower()

                    dri_post_processing_df.loc[dri, "Cleaned Water Discharge Data"] = (re.split(r"\bmgd\b", s, flags = re.IGNORECASE)[0].strip())
                elif 'mgpd' in project_info[17][1].lower():
                    s = project_info[17][1].lower()
                    dri_post_processing_df.loc[dri, "Cleaned Water Discharge Data"] = (re.split(r"\bmgpd\b", s, flags = re.IGNORECASE)[0].strip())
                else:
                    dri_post_processing_df.loc[dri, "Cleaned Water Discharge Data"] = project_info[17][1].lower()
                    '''
                if 'gpd' in project_info[13][1].lower():
                    s = project_info[13][1].lower()
                    data_center_df.loc[dri, "Water Usage"] = (re.split(r"\bgpd\b", s, flags = re.IGNORECASE)[0].strip())/1000000
                elif 'gallons per day' in project_info[13][1].lower():
                    s = project_info[13][1].lower()
                    data_center_df.loc[dri, "Water Usage"] = (re.split(r"\bgallons per day\b", s, flags = re.IGNORECASE)[0].strip())
                    '''
            except IndexError:
                dri_post_processing_df.loc[dri, "Water Discharge Data"] = "No water data"
                dri_post_processing_df.loc[dri, "Cleaned Water Discharge Data"] = "No water data"
            
            dri_post_processing_df.loc[dri, "County"] = water_data_df.loc[dri, "County"]
            dri_post_processing_df.loc[dri, "Initial Info Form Submision Date"] = water_data_df.loc[dri, "Initial Info Form Submision Date"]
    #dri_post_processing_df['Cleaned Water Usage Data'] = dri_post_processing_df['Water Usage'].apply(parse_water_usage)
    dri_post_processing_output_path = dri_post_processing_path.parent / "dri_post_processing.csv"
    dri_post_processing_df = dri_post_processing_df[["Project Name", "Water Usage", "County", "Initial Info Form Submision Date", "Cleaned Water Usage Data", "Water Discharge Data", "Cleaned Water Discharge Data", "Contains 'data center'?", "Current Status", "Data Center?"]]
    dri_post_processing_df.to_csv(dri_post_processing_output_path, index = True)
    #print(dri_post_processing_df)
    print(dri_post_processing_df["Contains 'data center'?"].sum())
    return dri_post_processing_df

def parse_water_usage(value):
    '''
    if not isinstance(value, str):
        return np.nan
    value = value.lower().strip()

    if "no water data" in value:
        return np.nan
    '''
    # Convert gpd → mgd
    match_gpd = re.search(r"([\d,.]+)\s*(gpd)", value)
    if match_gpd:
        gpd = float(match_gpd.group(1).replace(",", ""))
        return gpd / 1000000

    # Convert gpm → mgd (1 gpm = 1440 gpd)
    match_gpm = re.search(r"([\d,.]+)\s*(gpm)", value)
    if match_gpm:
        gpm = float(match_gpm.group(1).replace(",", ""))
        return (gpm * 1440) / 1000000

    # Convert 'mgd' values
    match_mgd = re.search(r"([\d.]+)\s*mgd", value)
    if match_mgd:
        return float(match_mgd.group(1))

    # Check for gallons/day
    match_gal_day = re.search(r"([\d,]+)\s*gallons.*day", value)
    if match_gal_day:
        gallons = float(match_gal_day.group(1).replace(",", ""))
        return gallons / 1000000

    match_int = re.search(r"[\d.]+", value)
    if match_int:
        return float(match_int.group())
    
    # check if it's just a number
    try:
        return float(value)
    except ValueError:
        return "No water data"

def calculate_water_consumption(row):
    try:
        return float(row["Cleaned Water Usage Data"]) - float(row["Cleaned Water Discharge Data"])
    except ValueError or TypeError:
        return "No water data"
def clean_entries(df):
    terminated_names = df.loc[df['Current Status'].str.lower() == 'terminated', 'Project Name'].unique()
    df = df[~df['Project Name'].isin(terminated_names)]
    withdrawn_names = df.loc[df['Current Status'].str.lower() == 'withdrawn', 'Project Name'].unique()
    df = df[~df['Project Name'].isin(withdrawn_names)]
    return df
def main():
    dri_post_processing_df = water_data_post_processing()

    #dri_post_processing_df = pd.read_csv("../Data/dri_post_processing.csv", index_col = "DRI Number")
    script_dir = Path(__file__).resolve().parent
    dri_post_processing_path = script_dir.parent / "Data" / "dri_post_processing.csv"
    #dri_post_processing_df = pd.read_csv(dri_post_processing_path, index_col = "DRI Number")
    data_center_df = dri_post_processing_df[dri_post_processing_df["Contains 'data center'?"] == 1]

    data_center_df.loc[:, 'Cleaned Water Usage Data'] = data_center_df['Water Usage'].apply(parse_water_usage)
    data_center_df.loc[:, 'Cleaned Water Discharge Data'] = data_center_df['Water Discharge Data'].apply(parse_water_usage)
    data_center_df.loc[:, "Water Consumption/Loss"] = data_center_df.apply(calculate_water_consumption, axis = 1)
    #data_center_df["Water Consumption/Loss"] = data_center_df["Water Consumption/Loss"].round(5)
    #gps_coordinates(data_center_df)
    data_center_df = data_center_df[["Water Consumption/Loss", "Project Name", "County", "Initial Info Form Submision Date", "Cleaned Water Usage Data", "Cleaned Water Discharge Data", "Water Usage", "Water Discharge Data","Contains 'data center'?", "Current Status", "Data Center?"]]
    data_center_df = clean_entries(data_center_df)
    print(data_center_df)
    data_center_output_path = dri_post_processing_path.parent / "data_center.csv"
    data_center_df.to_csv(data_center_output_path, index = True)

main()
