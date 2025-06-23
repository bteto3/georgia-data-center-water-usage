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
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib import colormaps


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
    ax.set_title("Number of Data Centers by County", fontsize=16)
    ax.axis("off")

    # Save the static image
    folder = "visualizations"
    os.makedirs(folder, exist_ok=True)
    plt.savefig(os.path.join(folder, "data_center_water_data_county_map_matplotlib.png"), dpi=300, bbox_inches='tight')
    plt.close()


def plot_stacked_bar_by_county():
    # Filter out rows with missing water consumption
    script_dir = Path(__file__).resolve().parent
    data_center_path = script_dir.parent / "Data" / "data_center.csv"
    df = pd.read_csv(data_center_path)
    df = df.dropna(subset=["Water Consumption/Loss"])

    # Aggregate total water consumption per county to get sorting order
    county_totals = df.groupby("County")["Water Consumption/Loss"].sum().sort_values(ascending=False)
    sorted_counties = county_totals.index.tolist()

    # Sort the original df by this county order
    df["County"] = pd.Categorical(df["County"], categories=sorted_counties, ordered=True)
    df = df.sort_values("County")

    # Prepare data for stacking:
    # Each data center project will be a segment in the stack.
    # So group by County and some project ID (like "DRI Number")
    projects = df["DRI Number"].unique()

    # Create a pivot table: rows=counties, columns=projects, values=water consumption
    pivot = df.pivot_table(index="County", columns="Project Name", values="Water Consumption/Loss", aggfunc='sum', fill_value=0, observed=False)
    pivot = pivot.apply(pd.to_numeric, errors="coerce").fillna(0)
    project_totals = pivot.sum(axis=0).sort_values(ascending=False)
    pivot = pivot[project_totals.index]  # Reorder columns
    county_totals = pivot.sum(axis=1).sort_values(ascending=False)
    pivot = pivot.loc[county_totals.index]  
    # Plot stacked bar chart
    fig, ax = plt.subplots(figsize=(14, 8))

    project_to_counties = df.groupby("Project Name")["County"].unique()
    bottom = np.zeros(len(pivot))
    for project in pivot.columns:
        values = pivot[project].values
        counties = project_to_counties.get(project, ["Unknown"])
        counties_str = ", ".join(counties)
        ax.bar(pivot.index, values, bottom=bottom, label=f"{project} ({counties_str})")
        bottom += values
    

    # Formatting
    ax.set_xticklabels(pivot.index, rotation=90)
    ax.set_ylabel("Water Consumption (mgd)")
    ax.set_title("Water Consumption by County and Data Center Project")
    ax.legend(title="Project Names", bbox_to_anchor=(1.05, 1), loc='upper left')
    #plt.tight_layout()
    #plt.show()
    folder = "visualizations"
    os.makedirs(folder, exist_ok=True)
    plt.savefig(os.path.join(folder, "data_center_water_data_bar_chart_matplotlib.png"), dpi=300, bbox_inches='tight')

def plot_submission_timeline():
    script_dir = Path(__file__).resolve().parent
    data_center_path = script_dir.parent / "Data" / "data_center.csv"
    df = pd.read_csv(data_center_path)
    # Drop rows without a valid submission date
    #df = df.dropna(subset=["Initial Info Form Submision Date"])
    #df = pd.DataFrame(data, columns=['Project', 'County', 'Date'])

    # Convert the submission date to datetime
    # Convert the submission date to datetime
    df['Initial Info Form Submision Date'] = pd.to_datetime(df['Initial Info Form Submision Date'], format='%m/%d/%Y')

    # Sort by submission date
    df = df.sort_values('Initial Info Form Submision Date')

    # Create the plot
    fig, ax = plt.subplots(figsize=(18, 12))  # Made wider to accommodate legend

    # Create timeline plot
    # Since data is sorted chronologically, y-positions represent cumulative count
    y_positions = range(1, len(df) + 1)  # Start from 1 for cumulative count

    # Create color mapping by county
    unique_counties = df['County'].unique()
    #color_map = plt.cm.Set3(range(len(unique_counties)))
    #county_colors = {county: color_map[i] for i, county in enumerate(unique_counties)}

    cmap = colormaps.get_cmap("tab20")  # or "tab20", "Set3", "hsv", etc.


    color_map = [cmap(i / len(unique_counties)) for i in range(len(unique_counties))]

    # Assign each unique county a distinct color
    county_colors = {county: color_map[i] for i, county in enumerate(unique_counties)}

    # Map colors to each project based on county
    colors = [county_colors[county] for county in df['County']]

    # Plot the timeline points
    scatter = ax.scatter(df['Initial Info Form Submision Date'], y_positions, 
                        c=colors, s=100, alpha=0.7, edgecolors='black', linewidth=0.5)

    # Add project names to the right of each point
    for i, (idx, row) in enumerate(df.iterrows()):
        cumulative_count = i + 1  # i starts at 0, so add 1 for cumulative count
        ax.annotate(f"{row['Project Name']} ({row['County']})", 
                    (row['Initial Info Form Submision Date'], cumulative_count), 
                    xytext=(10, 0), 
                    textcoords='offset points',
                    fontsize=9,
                    va='center',
                    ha='left')

    # Format the plot
    ax.set_yticks(y_positions[::5])  # Show every 5th tick to avoid crowding
    ax.set_ylabel('Cumulative Number of Projects', fontsize=12, fontweight='bold')
    ax.set_xlabel('Initial Form Submission Date', fontsize=12, fontweight='bold')
    ax.set_title('Cumulative Timeline of Project Initial Form Submissions', fontsize=16, fontweight='bold', pad=20)

    # Format x-axis dates
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # Rotate x-axis labels for better readability
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=10)

    # Add more space at bottom for rotated labels
    plt.subplots_adjust(bottom=0.15)

    # Add grid for better readability
    ax.grid(True, alpha=0.3, axis='both')  # Add grid for both axes

    # Add more space at bottom for rotated labels
    plt.subplots_adjust(bottom=0.15, right=0.75)  # Make room for legend on right

    # Create legend for counties
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=county_colors[county], 
                                markersize=8, label=county, markeredgecolor='black', markeredgewidth=0.5) 
                    for county in unique_counties]

    # Add legend outside the plot area
    ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1.02, 0), 
            title='County', title_fontsize=12, fontsize=10)

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Add some styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # Keep left spine visible now since y-axis has meaning

    # Add a subtitle with summary statistics
    earliest_date = df['Initial Info Form Submision Date'].min().strftime('%B %d, %Y')
    latest_date = df['Initial Info Form Submision Date'].max().strftime('%B %d, %Y')
    total_projects = len(df)

    plt.figtext(0.5, 0.02, f'Total Projects: {total_projects} | Date Range: {earliest_date} to {latest_date}', 
                ha='center', fontsize=10, style='italic')

    #plt.figtext(0.5, 0.02, f'Total Projects: {total_projects} | Date Range: {earliest_date} to {latest_date}', ha='center', fontsize=10, style='italic')

    folder = "visualizations"
    os.makedirs(folder, exist_ok=True)
    plt.savefig(os.path.join(folder, "data_center_data_center_timeline_matplotlib.png"), dpi=300, bbox_inches='tight')

def plot_water_consumption_histogram():
    # Load your data
    script_dir = Path(__file__).resolve().parent
    data_center_path = script_dir.parent / "Data" / "data_center.csv"
    df = pd.read_csv(data_center_path)

    # Convert the water usage column to numeric
    df["Water Consumption/Loss"] = pd.to_numeric(df["Water Consumption/Loss"], errors="coerce")

    # Drop missing or invalid values
    df = df.dropna(subset=["Water Consumption/Loss"])

    #bin_width = 0.5
    #max_val = df["Water Consumption/Loss"].max()
    #xticks = np.arange(0, max_val + bin_width, bin_width)    

    # Plot histogram
    bins = np.arange(0, df["Water Consumption/Loss"].max() + 0.25, 0.25)
    plt.figure(figsize=(10, 6))
    #plt.hist(df["Water Consumption/Loss"], bins=20, color="skyblue", edgecolor="black", alpha=0.8)
    plt.hist(
        df["Water Consumption/Loss"],
        bins = bins,                    # or set your own: bins=np.arange(0, 20, 1)
        color="skyblue",
        edgecolor="black",
        alpha=0.8,
        align="mid",               # or 'left' for left-aligned bars
        rwidth = 1.0                 # makes bars narrower, adds spacing
    )

    # Styling
    #plt.xticks(xticks)
    plt.xlabel("Water Consumption (mgd)", fontsize=12, fontweight="bold")
    plt.ylabel("Number of Projects", fontsize=12, fontweight="bold")
    plt.title("Distribution of Water Consumption per Project", fontsize=14, fontweight="bold")
    plt.grid(True, axis='y', linestyle="--", alpha=0.4)

    # Save to file

    folder = "visualizations"
    os.makedirs(folder, exist_ok=True)
    plt.savefig(os.path.join(folder, "data_center_water_consumption_histogram_matplotlib.png"), dpi=300)

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

plot_stacked_bar_by_county()

plot_submission_timeline()

plot_water_consumption_histogram()