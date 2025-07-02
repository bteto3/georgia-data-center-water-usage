from pathlib import Path

fig_paths = [
    Path("visualizations/data_center_water_data_county_map_matplotlib.png"),
    Path("visualizations/data_center_water_data_bar_chart_matplotlib.png"),
    Path("visualizations/visualizations/quarterly_data_center_submissions.png"),
    Path("visualizations/data_center_water_consumption_histogram_matplotlib.png"),
    Path("visualizations/data_center_water_consumption_log_histogram_matplotlib.png")
]

placeholder_map = {
    "<!-- FIGURE_1 -->": "visualizations/data_center_water_data_county_map_matplotlib.png",
    "<!-- FIGURE_2 -->": "visualizations/data_center_water_data_bar_chart_matplotlib.png",
    "<!-- FIGURE_3 -->": "visualizations/visualizations/quarterly_data_center_submissions.png",
    "<!-- FIGURE_4 -->": "visualizations/data_center_water_consumption_histogram_matplotlib.png",
    "<!-- FIGURE_5 -->": "visualizations/data_center_water_consumption_log_histogram_matplotlib.png"
}

readme_path = Path("README.md")
readme = readme_path.read_text()

for placeholder, fig_path in placeholder_map.items():
    img_md = f"![{Path(fig_path).stem}]({fig_path})"
    readme = readme.replace(placeholder, img_md)

readme_path.write_text(readme)
