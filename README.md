# NYC Sidewalk Wellness Score

![Sidewalk Banner](https://images.unsplash.com/photo-1553614738-4230655f7639?auto=format&fit=crop&q=80)

## Project Overview

The NYC Sidewalk Wellness Score is an interactive data visualization tool that transforms the NYC Sidewalk Management Database into an informative dashboard. This project analyzes sidewalk inspection records to compute and visualize a "wellness score" for each ZIP code in New York City, representing the overall maintenance intensity of sidewalks in each area.

A **higher wellness score** indicates **better maintained sidewalks** (fewer inspections, implying fewer defects or issues requiring attention).

## Dataset Description

The project uses the **NYC Sidewalk Management Database (Lot Info)** dataset, which contains information about sidewalk inspection locations throughout New York City.

Key columns in the dataset:

- `bblid`: Unique identifier for the sidewalk inspection location
- `block`: Unique tax block number
- `boro`: One-digit NYC borough code
- `lot`: Unique lot number
- `zipcode`: Postal ZIP code

Each row represents one sidewalk defect inspection location.

## Features

- **Interactive Map**: Visualize the wellness score distribution across NYC ZIP codes
- **Ranking Tables**: View the best and worst-performing ZIP codes
- **Data Explorer**: Search, filter, and download the complete dataset
- **Score Distribution**: Analyze the overall distribution of wellness scores
- **Geospatial Integration**: (Optional) Map visualization with NYC ZIP code boundaries

## How the Wellness Score is Calculated

The wellness score is calculated using the following formula:

```
wellness_score = (1 - (inspection_count / max_inspection_count)) * 100
```

Where:

- `inspection_count` is the number of inspections for a given ZIP code
- `max_inspection_count` is the highest number of inspections across all ZIP codes

This calculation ensures that ZIP codes with fewer inspections (potentially indicating better sidewalk conditions) receive higher wellness scores.

## Project Structure

```
nyc_sidewalks/
│
├── data/                           # Data files
│   ├── Sidewalk_Management_Database-Lot_Info_20250408.csv  # Raw data
│   ├── wellness_scores.csv         # Processed data
│   └── geo/                        # Geospatial data files
│       ├── nyc_zipcodes.geojson    # ZIP code boundaries
│       └── nyc_wellness_scores.geojson  # Merged geospatial data
│
├── src/                            # Source code
│   ├── data_cleaning.py            # Data loading and cleaning script
│   ├── geo_integration.py          # Geospatial integration script
│   └── app.py                      # Streamlit dashboard
│
├── notebooks/                      # Jupyter notebooks (optional, for exploration)
│
├── venv/                           # Virtual environment (not committed to Git)
│
├── README.md                       # Project documentation
└── requirements.txt                # Dependencies
```

## Setup and Installation

1. **Clone the repository**:

   ```
   git clone https://github.com/yourusername/nyc_sidewalks.git
   cd nyc_sidewalks
   ```

2. **Create and activate a virtual environment**:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```
   pip install -r requirements.txt
   ```

4. **Process the data**:

   ```
   python src/data_cleaning.py
   python src/geo_integration.py  # Optional, for geospatial visualization
   ```

5. **Run the Streamlit dashboard**:

   ```
   streamlit run src/app.py
   ```

6. **Open the dashboard** in your web browser at http://localhost:8501

## Screenshots

![Dashboard Screenshot](screenshots/dashboard.png)
_(Add screenshots once the application is running)_

## Dependencies

- Python 3.x
- pandas
- streamlit
- folium
- plotly
- geopandas (optional, for geospatial visualization)
- streamlit-folium (optional, for interactive maps)

## Future Enhancements

- Integration with additional NYC datasets for deeper analysis
- Time-series analysis of sidewalk maintenance over different periods
- Enhanced filtering capabilities by borough, neighborhood, etc.
- Mobile-optimized dashboard

## License

This project is open source and available under the [MIT License](LICENSE).

## Author

[Your Name] - [your.email@example.com]

---

**Note**: This project was developed as a data analysis and visualization exercise using public NYC data.
