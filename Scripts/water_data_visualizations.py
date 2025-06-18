import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd
import plotly.express as px
from pathlib import Path
import os
import plotly.graph_objects as go
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


map_visualization()
bar_chart_visualization()