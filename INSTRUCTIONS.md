============================================================
SIDEWALK WELLNESS SCORE ASSIGNMENT – NYC SIDEWALK DATA
============================================================

## Objective:

Develop a data project that transforms the NYC Sidewalk Management Database
(Lot Info) into an interactive tool named “Sidewalk Wellness Score.” The tool
will analyze the sidewalk inspection records to compute and visualize a score
for each ZIP code in NYC. This score will represent the “health” or overall
maintenance intensity of sidewalks in each area. A lower inspection count
(perceived as fewer defects or issues) corresponds to a higher wellness score.

## Dataset:

File: Sidewalk_Management_Database-Lot_Info_20250408.csv

Columns:

- bblid : Unique identifier for the sidewalk inspection location.
- block : Unique tax block number.
- boro : One-digit NYC borough code.
- lot : Unique lot number.
- zipcode : Postal ZIP code.

Note: Each row represents one sidewalk defect inspection location.

## Tools & Technologies:

- Python 3.x
- Pandas for data manipulation
- (Optional) GeoPandas for geospatial integration
- Streamlit for creating an interactive web app dashboard
- Folium or Plotly for map visualizations
- Git & GitHub for version control and portfolio showcasing

---

## STEP-BY-STEP INSTRUCTIONS

## Step 1: Project Setup (approx. 5 minutes)

a. ive created a github repository for this project.
b. understand the project's objective and dataset, and create an appropriate project folder structure for employers
c. Set up a Python virtual environment and activate it:
$ python -m venv venv
$ source venv/bin/activate (On Windows: venv\Scripts\activate)
d. Install required libraries:
$ pip install pandas streamlit
(For geospatial mapping, also install geopandas and folium or plotly)

## Step 2: Data Loading and Cleaning (approx. 20 minutes)

a. Place the provided CSV file (Sidewalk_Management_Database-Lot_Info_20250408.csv)
in your project directory.
b. Create a new Python script (e.g., data_cleaning.py).
c. In data_cleaning.py, load the CSV file using Pandas:

---

import pandas as pd

# Load CSV file

df = pd.read_csv("Sidewalk_Management_Database-Lot_Info_20250408.csv")
print(df.head())

---

d. Check for any missing values or anomalies. Since the file is from the DOT,
you may assume the data is largely complete. However, include commands to drop
or flag any missing rows if necessary.
e. Aggregate the data by 'zipcode'. For each ZIP code, calculate the number of
inspections (count of rows). This number will be used to compute the wellness score.

---

# Group by zipcode and count inspections

zipcode_counts = df.groupby('zipcode').size().reset_index(name='inspection_count')
print(zipcode_counts.head())

---

## Step 3: Compute the Sidewalk Wellness Score (approx. 10 minutes)

a. Define the wellness score such that a lower number of inspections (implying fewer defects)
corresponds to a higher score. One way to calculate the score is:

      wellness_score = (1 - (inspection_count / max_inspection_count)) * 100

b. Extend the previous script:

---

max_count = zipcode_counts['inspection_count'].max()
zipcode_counts['wellness_score'] = (1 - (zipcode_counts['inspection_count'] / max_count)) \* 100
print(zipcode_counts.head())

---

## Step 4: Geospatial Integration (optional, approx. 10 minutes)

a. Download a NYC ZIP code boundaries shapefile or GeoJSON file (available from NYC Open Data or other sources).
b. Use GeoPandas to merge the zipcode_counts DataFrame with geospatial data:

---

import geopandas as gpd

# Load ZIP code boundaries file (e.g., nyc_zipcodes.geojson)

nyc_zips = gpd.read_file("nyc_zipcodes.geojson")
merged = nyc_zips.merge(zipcode_counts, left_on="ZIPCODE_FIELD", right_on="zipcode")
print(merged.head())

---

Replace "ZIPCODE_FIELD" with the correct property name from the geospatial file.

## Step 5: Building an Interactive Visualization Dashboard (approx. 20 minutes)

a. Create a new script (e.g., app.py) that uses Streamlit to display the results.
b. Use an interactive map to show the Sidewalk Wellness Score across NYC:
Example using Folium:

---

import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("NYC Sidewalk Wellness Score")

# Create a base map centered on NYC

m = folium.Map(location=[40.7128, -74.0060], zoom_start=11)

# Add a choropleth layer if geospatial merge is complete

folium.Choropleth(
geo_data=merged,
data=merged,
columns=['zipcode', 'wellness_score'],
key_on='feature.properties.ZIPCODE_FIELD', # Adjust as needed
fill_color='YlGn',
legend_name='Sidewalk Wellness Score (%)'
).add_to(m)

st_folium(m, width=700, height=500)

---

c. If you do not use geospatial visualization, create tables or plots that depict
the wellness scores by ZIP code using Streamlit’s built-in functions.

## Step 6: Documentation and GitHub Submission (approx. 5 minutes)

a. Write a README.md file that includes:

- Project Title and Overview
- Description of the dataset and its columns
- Detailed instructions for setting up the environment and running your project
- Screenshots of the dashboard (if applicable)
- Explanation of the Sidewalk Wellness Score calculation
  b. Commit all files to Git:
  $ git add .
  $ git commit -m "Initial commit: Added data cleaning, computation, and dashboard"
  $ git push origin main
  c. Optionally, deploy your Streamlit app using Streamlit Cloud and include the deployment
  link in the README.

## Additional Tips:

- Use inline comments in your code to explain each processing step.
- Experiment with different visualizations (bar charts, tables, interactive maps)
  to represent the wellness score data more effectively.
- Maintain a clean and organized project directory.
- Check that your repository is well-documented to impress potential employers and
  showcase your technical skills in data wrangling, geospatial analysis, and dashboard design.

============================================================
END OF INSTRUCTIONS
============================================================
