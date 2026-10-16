# Geospatial-Temporal Excess Deaths Lab Project

## Contents
- `geospatial_temporal_excess_deaths_lab.ipynb` — self-contained notebook with all code and all assignment question answers in Markdown cells.
- `all_weekly_excess_deaths.csv` — the supplied dataset.
- `requirements.txt` — Python packages needed by the notebook.
- `lab_report.md` — report-ready narrative and references.
- `outputs/` — generated charts, profile tables, and result CSVs from the analysis.

## Run the notebook
1. Extract/open this whole folder in Jupyter Notebook or JupyterLab.
2. Install dependencies in a terminal from this folder: `python -m pip install -r requirements.txt`.
3. Open `geospatial_temporal_excess_deaths_lab.ipynb` and run **Run All** from top to bottom.
4. The CSV should stay beside the notebook. If you move it, change the `CSV` variable in the first code cell.
5. The choropleth obtains Natural Earth country boundaries online. If that fetch fails or you are offline, the notebook reports the map limitation; the other analyses still run.

The code was executed against the included CSV before delivery. The `outputs/` folder includes the resulting 300-DPI figures and CSV result tables. Running the notebook will recreate/update them.
