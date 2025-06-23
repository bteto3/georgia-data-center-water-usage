from pathlib import Path

fig_paths = [
    Path("visualizations/data_center_water_data_county_map_matplotlib.png"),
    Path("visualizations/data_center_water_data_bar_chart_matplotlib.png"),
    Path("visualizations/data_center_data_center_timeline_matplotlib.png"),
    Path("visualizations/data_center_water_consumption_histogram_matplotlib.png")
]
fig_md_block = "\n".join([f"![{fig.stem}]({fig.as_posix()})" for fig in fig_paths])
readme_path = Path("README.md")
readme = readme_path.read_text()

if "<!-- FIGURE_PLACEHOLDER -->" in readme:
    updated = readme.replace("<!-- FIGURE_PLACEHOLDER -->", fig_md_block)
else:
    updated = readme + "\n\n" + fig_md_block

readme_path.write_text(updated)
