import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd
import plotly.express as px
from pathlib import Path
import os
import plotly.graph_objects as go
import plotly.io as pio
import requests
from shapely.geometry import shape

def map_visualzation_matplotlib():
    # Load Georgia counties geometry from GeoJSON
    url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    geojson = requests.get(url).json()
    features = geojson["features"]
    geometries = [shape(f["geometry"]) for f in features]
    fips_codes = [f["id"] for f in features]
    ga_geo = gpd.GeoDataFrame({"fips": fips_codes}, geometry=geometries)
    ga_geo = ga_geo[ga_geo["fips"].str.startswith("13")]

    script_dir = Path(__file__).resolve().parent
    data_center_path = script_dir.parent / "Data" / "data_center.csv"
    df = pd.read_csv(data_center_path)  # or use pd.read_excel() if Excel
    df["Water Consumption/Loss"] = pd.to_numeric(df["Water Consumption/Loss"], errors="coerce")  # convert numbers
    df["Initial Info Form Submision Date"] = pd.to_datetime(df["Initial Info Form Submision Date"], errors="coerce")

    usage_by_county = df.groupby("County").agg(
    Water_Consumption=("Water Consumption/Loss", "sum"),
    Num_Data_Centers=("DRI Number", "count")
    ).reset_index()

    ga_counties = pd.read_csv("https://raw.githubusercontent.com/kjhealy/fips-codes/master/state_and_county_fips_master.csv")
    ga_counties = ga_counties[ga_counties["state"] == "GA"]
    ga_counties["fips"] = ga_counties["fips"].apply(lambda x: f"{x:05d}")
    ga_counties = ga_counties.rename(columns={"name": "County"})[["County", "fips"]]
    ga_counties['County'] = ga_counties['County'].str.split().str[0]

    merged = ga_counties.merge(usage_by_county, on="County", how="left")
    merged["Water_Consumption"] = merged["Water_Consumption"].fillna(0)
    merged["Num_Data_Centers"] = merged["Num_Data_Centers"].fillna(0)

    column_names = ["Sort", "State", "fips", "County", "County Seat(s)", "Population", "Land Area (km)", "Land Area(mi)", "Water Area (km)", "Water Area(mi)", "Total Area (km)", "Total Area(mi)", "Lat", "Long"]
    county_data_path = script_dir.parent / "Data" / "GA_county_centroids.csv"
    county_data_df = pd.read_csv(county_data_path, header = None, names = column_names)
    county_data_df = county_data_df.drop(["Sort", "State", "County Seat(s)", "Population", "Land Area (km)", "Land Area(mi)", "Water Area (km)", "Water Area(mi)", "Total Area (km)", "Total Area(mi)"], axis = 1)

    # Add latitude and longitude from county_data_df
    county_data_df['fips'] = county_data_df['fips'].astype(str)
    merged['fips'] = merged['fips'].astype(str)
    merged = merged.merge(county_data_df[["fips", "Lat", "Long"]], on="fips", how="left")

    # Merge geometry with data
    gdf = ga_geo.merge(merged, on="fips", how="left")

    # Set up figure
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    # Plot choropleth
    gdf.plot(column="Water_Consumption", cmap="Blues", linewidth=0.8, edgecolor='0.8', legend=True, ax=ax)
    
    positions = [
    {"offset": (0.2, 0.2), "ha": "left", "va": "bottom"},    # right-up
    {"offset": (-0.3, 0), "ha": "right", "va": "center"},    # left
    {"offset": (0, -0.25), "ha": "center", "va": "top"},     # below
    ]

    
    # Annotate counties with # of data centers
    for i, row in gdf[gdf["Num_Data_Centers"] > 0].iterrows():
        ax.text(row["geometry"].centroid.x, row["geometry"].centroid.y, 
                str(int(row["Num_Data_Centers"])),
                fontsize=6, ha='center', va='center', color='black')
        '''
        centroid = row["geometry"].centroid
        #label = f"{row['County']}\n{int(row['Num_Data_Centers'])} data center(s)"
        label = f"{row['County']}"
        
        
        pos = positions[i % len(positions)]  # cycle positions
    
        ax.annotate(
            label,
            xy=(centroid.x, centroid.y),
            xytext=(centroid.x + pos["offset"][0], centroid.y + pos["offset"][1]),
            textcoords='data',
            fontsize=6,
            ha=pos["ha"],
            va=pos["va"],
            bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='none', alpha=0.8),
            arrowprops=dict(arrowstyle='->', color='black', lw=0.5),
        )

        
        # Offset the text slightly from the county centroid
        offset_x = -0.1  # degrees of longitude
        offset_y = 0.2  # degrees of latitude
        ax.annotate(
            label,
            xy=(centroid.x, centroid.y),  # arrow points here
            xytext=(centroid.x + offset_x, centroid.y + offset_y),  # text is placed here
            textcoords='data',
            fontsize=6,
            ha='left',
            va='bottom',
            #bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='none', alpha=0.8),
            arrowprops=dict(arrowstyle='->', color='black', lw=0.5),
        )
        '''
    '''
    for idx, row in gdf[gdf["Num_Data_Centers"] > 0].iterrows():
        centroid = row["geometry"].centroid
        label = f"{row['County']}\n{int(row['Num_Data_Centers'])} data center(s)"
        ax.text(
            centroid.x, centroid.y,
            label,
            fontsize=6,
            ha='center',
            va='center',
            color='black',
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, boxstyle='round,pad=0.2')
        )
    '''
        
    # Tidy layout
    ax.set_title("Water Consumption by County", fontsize=16)
    ax.axis("off")

    # Save the static image
    folder = "visualizations"
    os.makedirs(folder, exist_ok=True)
    plt.savefig(os.path.join(folder, "data_center_water_data_county_map_matplotlib.png"), dpi=300, bbox_inches='tight')
    plt.close()

def map_visualization():
    script_dir = Path(__file__).resolve().parent
    data_center_path = script_dir.parent / "Data" / "data_center.csv"
    county_data_path = script_dir.parent / "Data" / "GA_county_centroids.csv"
    df = pd.read_csv(data_center_path)  # or use pd.read_excel() if Excel
    column_names = ["Sort", "State", "fips", "County", "County Seat(s)", "Population", "Land Area (km)", "Land Area(mi)", "Water Area (km)", "Water Area(mi)", "Total Area (km)", "Total Area(mi)", "Lat", "Long"]
    county_data_df = pd.read_csv(county_data_path, header = None, names = column_names)
    df["Water Consumption/Loss"] = pd.to_numeric(df["Water Consumption/Loss"], errors="coerce")  # convert numbers
    df["Initial Info Form Submision Date"] = pd.to_datetime(df["Initial Info Form Submision Date"], errors="coerce")
    county_data_df = county_data_df.drop(["Sort", "State", "County Seat(s)", "Population", "Land Area (km)", "Land Area(mi)", "Water Area (km)", "Water Area(mi)", "Total Area (km)", "Total Area(mi)"], axis = 1)

    ga_counties = pd.read_csv("https://raw.githubusercontent.com/kjhealy/fips-codes/master/state_and_county_fips_master.csv")
    ga_counties = ga_counties[ga_counties["state"] == "GA"]
    ga_counties["fips"] = ga_counties["fips"].apply(lambda x: f"{x:05d}")  # Pad FIPS
    ga_counties = ga_counties.rename(columns={"name": "County"})[["County", "fips"]]
    ga_counties['County'] = ga_counties['County'].str.split().str[0]

    usage_by_county = df.groupby("County").agg(
        Water_Consumption=("Water Consumption/Loss", "sum"),
        Num_Data_Centers=("DRI Number", "count")
    ).reset_index()

    merged = ga_counties.merge(usage_by_county, on="County", how="left")
    merged["Water_Consumption"] = merged["Water_Consumption"].fillna(0)
    merged["Num_Data_Centers"] = merged["Num_Data_Centers"].fillna(0)
    print(merged)

    merged["text_label"] = merged["Num_Data_Centers"].apply(
        lambda x: f"{x} data centers" if x > 0 else ""
    )
    fig = px.choropleth(
        merged,
        geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
        locations="fips",
        color="Water_Consumption",
        hover_name="County",
        hover_data=["Num_Data_Centers"],
        scope="usa",
        labels={"Water_Consumption": "Water Use (mgd)"},
        color_continuous_scale="Blues"
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        title="Water Consumption by County",
        margin={"r":0,"t":30,"l":0,"b":0}
    )
    merged['fips'] = merged['fips'].astype(str)
    county_data_df['fips'] = county_data_df['fips'].astype(str)
    merged = merged.merge(county_data_df[["fips", "Lat", "Long"]], on = "fips", how = "left")
    df_nonzero = merged[merged["Num_Data_Centers"] > 0]
    fig.add_trace(go.Scattergeo(
        lon=df_nonzero["Long"],  # longitude of county center
        lat=df_nonzero["Lat"],  # latitude of county center
        text=df_nonzero["Num_Data_Centers"].astype(int),
        mode="text",
        textfont=dict(color="black", size=8),
        showlegend=False
    ))
    '''
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_scale=10  # Try values between 5–10 to "zoom" in more
    )
    '''
    fig.show()

    folder = "visualizations"
    filename = "data_center_water_data_county_map.png"
    full_path = os.path.join(folder, filename)
    #fig.write_image(full_path)
    fig.write_image(full_path, width=1200, height=900, scale=2)
    fig.write_html(os.path.join(folder, "data_center_water_data_county_map.html"))

    '''
    county_group = df.groupby("County", as_index=False).agg({
        "Water Consumption/Loss": "sum",
        "DRI Number": "count"
    })
    county_group.rename(columns={"DRI Number": "Number of Projects"}, inplace=True)

    # You’ll need a county FIPS code mapping
    county_fips = county_county_data_df.set_index("County")["FIPS"].to_dict()
        #"Fulton": "13121", "Douglas": "13097", "Coweta": "13077", "Bartow": "13015",
        # Add all counties in your data with correct FIPS codes
        


    county_group["fips"] = county_group["County"].map(county_fips)

    fig = px.choropleth(
        county_group,
        geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
        locations="fips",
        color="Water Consumption/Loss",
        hover_name="County",
        hover_data=["Number of Projects"],
        scope="usa",
        labels={"Water Consumption/Loss": "Total Water (mgd)"},
        color_continuous_scale="Blues"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(title="Georgia Data Center Water Use by County")
    fig.show()
    '''

    '''
    def water_data_map():
        # Load Georgia counties shapefile (or USA if needed)
        gdf = gpd.read_file("path/to/ga_counties_shapefile.shp")

        # Aggregate water consumption by county
        county_usage = df.groupby("County")["Water Consumption"].sum().reset_index()

        # Merge shapefile with data
        gdf = gdf.merge(county_usage, left_on="NAME", right_on="County")

        # Plot choropleth
        fig, ax = plt.subplots(figsize=(12, 8))
        gdf.plot(column="Water Consumption", cmap="Blues", legend=True, ax=ax, edgecolor='black')

        # Add labels
        for idx, row in gdf.iterrows():
            plt.annotate(text=int(row["Water Consumption"]), xy=(row.geometry.centroid.x, row.geometry.centroid.y),
                        ha='center', fontsize=8, color='black')

        plt.title("Water Consumption by County in Georgia")
        plt.axis("off")
        plt.show()
    '''

def bar_chart_visualization():
    script_dir = Path(__file__).resolve().parent
    data_center_path = script_dir.parent / "Data" / "data_center.csv"
    #county_data_path = script_dir.parent / "Data" / "GA_county_centroids.csv"
    df = pd.read_csv(data_center_path)  # or use pd.read_excel() if Excel
    df["Water Consumption/Loss"] = pd.to_numeric(df["Water Consumption/Loss"], errors="coerce")
    df["Water Consumption/Loss"] = df["Water Consumption/Loss"].fillna(0)
    project_breakdown = df.groupby(["County", "Project Name"])["Water Consumption/Loss"].sum().reset_index()

    # Sort counties by total usage
    county_totals = df.groupby("County")["Water Consumption/Loss"].sum().sort_values(ascending=False)
    ordered_counties = county_totals.index.tolist()
    project_breakdown["County"] = pd.Categorical(project_breakdown["County"], categories=ordered_counties, ordered=True)

    fig = px.bar(
        project_breakdown,
        x="County",
        y="Water Consumption/Loss",
        color="Project Name",
        title="Stacked Water Use by County and Project"
    )
    fig.update_layout(xaxis_title="County", yaxis_title="Water (mgd)")
    fig.show()
    folder = "visualizations"
    filename = "data_center_water_data_bar_chart.png"
    full_path = os.path.join(folder, filename)
    #fig.write_image(full_path)
    fig.write_image(full_path, width=1200, height=900, scale=3)
    fig.write_html(os.path.join(folder, "data_center_water_data_bar_chart.html"))


#map_visualization()
#bar_chart_visualization()
map_visualzation_matplotlib()