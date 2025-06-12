import pandas as pd
import numpy as np
import re

dri_post_processing_df = pd.read_csv("dri_post_processing.csv", index_col = "DRI Number")
data_center_df = dri_post_processing_df[dri_post_processing_df["Contains 'data center'?"] == 1]

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

# Apply the parser
data_center_df['Cleaned Water Usage Data'] = data_center_df['Water Usage'].apply(parse_water_usage)

print(data_center_df)
data_center_df.to_csv("data_center.csv", index = True)