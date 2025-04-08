import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import os
import json
import numpy as np
from branca.colormap import LinearColormap

# Set page configuration
st.set_page_config(
    page_title="NYC Sidewalk Wellness Score",
    page_icon="🚶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better aesthetics
st.markdown(
    """
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    h1 {
        color: #1E88E5;
    }
    h2 {
        color: #005CB2;
    }
    h3 {
        color: #0D47A1;
    }
    .stMetric {
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stMetric label {
        font-weight: bold;
    }
    .stDataFrame {
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    footer {
        visibility: hidden;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Function to load data
@st.cache_data
def load_data():
    """Load the wellness score data and geospatial data if available"""
    wellness_df = pd.read_csv("data/wellness_scores.csv")

    # Check if geospatial data exists
    geo_path = "data/geo/nyc_wellness_scores.geojson"
    if os.path.exists(geo_path):
        import geopandas as gpd

        geo_df = gpd.read_file(geo_path)
        has_geo = True

        # Check the actual properties in the GeoJSON
        property_fields = list(geo_df.columns)
        zipcode_field = None
        for field in property_fields:
            if field.lower() in [
                "postalcode",
                "zipcode",
                "zip",
                "postal_code",
                "zip_code",
            ]:
                zipcode_field = field
                break
    else:
        geo_df = None
        has_geo = False
        zipcode_field = None

    return wellness_df, geo_df, has_geo, zipcode_field


# Custom function to get color based on wellness score
def get_color(score):
    if score is None:
        return "#CCCCCC"  # Gray for missing data
    elif score >= 90:
        return "#006400"  # Dark green
    elif score >= 75:
        return "#228B22"  # Forest green
    elif score >= 60:
        return "#32CD32"  # Lime green
    elif score >= 45:
        return "#ADFF2F"  # Green yellow
    elif score >= 30:
        return "#FFFF00"  # Yellow
    elif score >= 15:
        return "#FFA500"  # Orange
    else:
        return "#FF0000"  # Red


# Main function
def main():
    # Add title and description
    st.title("NYC Sidewalk Wellness Score")
    st.markdown(
        """
    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
    This dashboard visualizes the "health" or overall maintenance intensity of sidewalks in New York City by ZIP code.
    The Sidewalk Wellness Score is calculated based on inspection records - a lower inspection count corresponds to a higher wellness score.
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Load data
    with st.spinner("Loading data..."):
        wellness_df, geo_df, has_geo, zipcode_field = load_data()

    # Show data overview
    st.subheader("Data Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total ZIP Codes", len(wellness_df))

    with col2:
        st.metric(
            "Average Wellness Score", f"{wellness_df['wellness_score'].mean():.2f}%"
        )

    with col3:
        st.metric(
            "Highest Wellness Score", f"{wellness_df['wellness_score'].max():.2f}%"
        )

    with col4:
        st.metric(
            "Lowest Wellness Score", f"{wellness_df['wellness_score'].min():.2f}%"
        )

    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Map", "Rankings", "Data Table"])

    # Tab 1: Map view
    with tab1:
        if has_geo and zipcode_field:
            st.subheader("Sidewalk Wellness Score by ZIP Code")

            # Display the correct zipcode field being used
            st.info(
                f"Using '{zipcode_field}' as the ZIP code field in the geospatial data."
            )

            # Create a folium map centered on NYC
            m = folium.Map(
                location=[40.7128, -74.0060], zoom_start=10, tiles="CartoDB positron"
            )

            # Create a custom colormap from red to green
            colors = [
                "#FF0000",
                "#FFA500",
                "#FFFF00",
                "#ADFF2F",
                "#32CD32",
                "#228B22",
                "#006400",
            ]
            custom_cm = LinearColormap(
                colors, vmin=0, vmax=100, caption="Wellness Score (%)"
            )

            # Create a lookup dictionary for easier access to wellness scores
            score_dict = dict(
                zip(wellness_df["zipcode"].astype(str), wellness_df["wellness_score"])
            )
            inspection_dict = dict(
                zip(wellness_df["zipcode"].astype(str), wellness_df["inspection_count"])
            )

            # Define style function
            def style_function(feature):
                zipcode = feature["properties"].get(zipcode_field)
                if zipcode in score_dict:
                    score = score_dict[zipcode]
                    color = get_color(score)
                else:
                    color = "#CCCCCC"  # Gray for missing data

                return {
                    "fillColor": color,
                    "color": "#000000",
                    "weight": 1,
                    "fillOpacity": 0.7,
                }

            # Add GeoJSON layer with custom styling
            geojson = folium.GeoJson(
                data=geo_df, style_function=style_function, name="Wellness Scores"
            )

            # Add tooltips to show information when hovering over a ZIP code
            tooltip = folium.GeoJsonTooltip(
                fields=[zipcode_field, "wellness_score", "inspection_count"],
                aliases=["ZIP Code:", "Wellness Score (%):", "Inspection Count:"],
                localize=True,
                sticky=False,
                labels=True,
                style="""
                    background-color: #F0F0F0;
                    border: 2px solid black;
                    border-radius: 3px;
                    box-shadow: 3px;
                """,
            )
            tooltip.add_to(geojson)
            geojson.add_to(m)

            # Add a legend
            custom_cm.add_to(m)

            # Display the map using streamlit-folium
            st_folium(m, width=1000, height=600, returned_objects=[])

            st.caption(
                "A higher wellness score (darker green) indicates better sidewalk conditions."
            )

            # Add a description of the color scale
            st.markdown(
                """
            <div style="margin-top: 20px;">
            <h4>Color Scale Interpretation:</h4>
            <ul>
                <li><span style="color: #006400; font-weight: bold;">Dark Green</span>: Excellent (90-100%)</li>
                <li><span style="color: #228B22; font-weight: bold;">Forest Green</span>: Very Good (75-89%)</li>
                <li><span style="color: #32CD32; font-weight: bold;">Lime Green</span>: Good (60-74%)</li>
                <li><span style="color: #ADFF2F; font-weight: bold;">Green Yellow</span>: Above Average (45-59%)</li>
                <li><span style="color: #FFFF00; font-weight: bold;">Yellow</span>: Average (30-44%)</li>
                <li><span style="color: #FFA500; font-weight: bold;">Orange</span>: Below Average (15-29%)</li>
                <li><span style="color: #FF0000; font-weight: bold;">Red</span>: Poor (0-14%)</li>
                <li><span style="color: #CCCCCC; font-weight: bold;">Gray</span>: No Data</li>
            </ul>
            </div>
            """,
                unsafe_allow_html=True,
            )
        elif has_geo:
            st.error(
                "Cannot identify ZIP code field in the geospatial data. Please check the GeoJSON structure."
            )

            # Show a bar chart instead
            fig = px.bar(
                wellness_df.sort_values("wellness_score", ascending=False).head(20),
                x="zipcode",
                y="wellness_score",
                title="Top 20 ZIP Codes by Wellness Score",
                labels={"zipcode": "ZIP Code", "wellness_score": "Wellness Score (%)"},
                color="wellness_score",
                color_continuous_scale="RdYlGn",  # Red-Yellow-Green scale
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(
                "Geospatial data is not available. Please run the geo_integration.py script first."
            )

            # Show a bar chart instead
            fig = px.bar(
                wellness_df.sort_values("wellness_score", ascending=False).head(20),
                x="zipcode",
                y="wellness_score",
                title="Top 20 ZIP Codes by Wellness Score",
                labels={"zipcode": "ZIP Code", "wellness_score": "Wellness Score (%)"},
                color="wellness_score",
                color_continuous_scale="RdYlGn",  # Red-Yellow-Green scale
            )
            st.plotly_chart(fig, use_container_width=True)

    # Tab 2: Rankings
    with tab2:
        st.subheader("ZIP Code Rankings")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Top 10 ZIP Codes (Highest Wellness Score)")
            top_df = (
                wellness_df.sort_values("wellness_score", ascending=False)
                .head(10)
                .reset_index(drop=True)
            )
            st.dataframe(
                top_df.style.background_gradient(
                    subset=["wellness_score"], cmap="YlGn"
                ),
                height=400,
            )

            # Add a visualization
            fig = px.bar(
                top_df,
                x="zipcode",
                y="wellness_score",
                color="wellness_score",
                color_continuous_scale="YlGn",
                title="Top 10 ZIP Codes by Wellness Score",
                labels={"zipcode": "ZIP Code", "wellness_score": "Wellness Score (%)"},
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Bottom 10 ZIP Codes (Lowest Wellness Score)")
            bottom_df = (
                wellness_df.sort_values("wellness_score")
                .head(10)
                .reset_index(drop=True)
            )
            st.dataframe(
                bottom_df.style.background_gradient(
                    subset=["wellness_score"], cmap="YlOrRd_r"
                ),
                height=400,
            )

            # Add a visualization
            fig = px.bar(
                bottom_df,
                x="zipcode",
                y="wellness_score",
                color="wellness_score",
                color_continuous_scale="YlOrRd_r",
                title="Bottom 10 ZIP Codes by Wellness Score",
                labels={"zipcode": "ZIP Code", "wellness_score": "Wellness Score (%)"},
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        # Show distribution of wellness scores
        st.subheader("Distribution of Wellness Scores")
        col1, col2 = st.columns(2)

        with col1:
            # Histogram
            fig = px.histogram(
                wellness_df,
                x="wellness_score",
                nbins=20,
                labels={"wellness_score": "Wellness Score (%)"},
                title="Distribution of Sidewalk Wellness Scores",
                color_discrete_sequence=["#1E88E5"],
            )
            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Box plot
            fig = px.box(
                wellness_df,
                y="wellness_score",
                labels={"wellness_score": "Wellness Score (%)"},
                title="Box Plot of Wellness Scores",
                color_discrete_sequence=["#1E88E5"],
            )
            st.plotly_chart(fig, use_container_width=True)

        # Add statistics table
        st.subheader("Statistical Summary")
        stats_df = pd.DataFrame(
            {
                "Statistic": [
                    "Mean",
                    "Median",
                    "Standard Deviation",
                    "Minimum",
                    "25th Percentile",
                    "75th Percentile",
                    "Maximum",
                ],
                "Value": [
                    f"{wellness_df['wellness_score'].mean():.2f}%",
                    f"{wellness_df['wellness_score'].median():.2f}%",
                    f"{wellness_df['wellness_score'].std():.2f}%",
                    f"{wellness_df['wellness_score'].min():.2f}%",
                    f"{wellness_df['wellness_score'].quantile(0.25):.2f}%",
                    f"{wellness_df['wellness_score'].quantile(0.75):.2f}%",
                    f"{wellness_df['wellness_score'].max():.2f}%",
                ],
            }
        )
        st.table(stats_df)

    # Tab 3: Data table
    with tab3:
        st.subheader("Complete Dataset")

        # Filter options
        col1, col2 = st.columns([1, 2])

        with col1:
            # Add a search box
            search_zip = st.text_input("Search by ZIP Code", "")

        with col2:
            # Add a range slider for filtering by wellness score
            wellness_range = st.slider(
                "Filter by Wellness Score Range (%)",
                min_value=float(wellness_df["wellness_score"].min()),
                max_value=float(wellness_df["wellness_score"].max()),
                value=(
                    float(wellness_df["wellness_score"].min()),
                    float(wellness_df["wellness_score"].max()),
                ),
            )

        # Apply filters
        filtered_df = wellness_df.copy()

        if search_zip:
            filtered_df = filtered_df[
                filtered_df["zipcode"].astype(str).str.contains(search_zip)
            ]

        filtered_df = filtered_df[
            (filtered_df["wellness_score"] >= wellness_range[0])
            & (filtered_df["wellness_score"] <= wellness_range[1])
        ]

        # Sort options
        sort_options = st.radio(
            "Sort by:",
            [
                "ZIP Code (Ascending)",
                "ZIP Code (Descending)",
                "Wellness Score (Highest First)",
                "Wellness Score (Lowest First)",
            ],
            horizontal=True,
        )

        if sort_options == "ZIP Code (Ascending)":
            filtered_df = filtered_df.sort_values("zipcode")
        elif sort_options == "ZIP Code (Descending)":
            filtered_df = filtered_df.sort_values("zipcode", ascending=False)
        elif sort_options == "Wellness Score (Highest First)":
            filtered_df = filtered_df.sort_values("wellness_score", ascending=False)
        else:  # "Wellness Score (Lowest First)"
            filtered_df = filtered_df.sort_values("wellness_score")

        # Show the data with styling
        st.dataframe(
            filtered_df.style.background_gradient(
                subset=["wellness_score"], cmap="RdYlGn", vmin=0, vmax=100
            ),
            height=500,
            use_container_width=True,
        )

        # Add count of filtered records
        st.markdown(f"**Showing {len(filtered_df)} of {len(wellness_df)} records**")

        # Download options
        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="📥 Download All Data as CSV",
                data=wellness_df.to_csv(index=False).encode("utf-8"),
                file_name="nyc_sidewalk_wellness_scores.csv",
                mime="text/csv",
            )

        with col2:
            st.download_button(
                label="📥 Download Filtered Data as CSV",
                data=filtered_df.to_csv(index=False).encode("utf-8"),
                file_name="nyc_sidewalk_wellness_scores_filtered.csv",
                mime="text/csv",
                disabled=len(filtered_df) == 0,
            )

    # Footer
    st.markdown("---")

    # About section
    st.subheader("About This Project")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        ### About the Wellness Score
        
        The Sidewalk Wellness Score is calculated based on the following formula:
        
        ```
        wellness_score = (1 - (inspection_count / max_inspection_count)) * 100
        ```
        
        A lower number of inspections (implying fewer defects) corresponds to a higher score. This means:
        
        - 100% = Perfect score (no inspections recorded)
        - 0% = Lowest possible score (maximum number of inspections)
        """
        )

    with col2:
        st.markdown(
            """
        ### Data Source
        
        **NYC Sidewalk Management Database (Lot Info)**
        
        This dataset contains information about sidewalk inspection locations throughout New York City.
        Each row represents one sidewalk defect inspection location.
        
        The project analyzes these inspection records to compute and visualize a "wellness score"
        for each ZIP code, representing the overall maintenance intensity of sidewalks in each area.
        """
        )

    # Credits section
    st.markdown(
        """
    <div style="text-align: center; margin-top: 30px; color: #888;">
    <small>Created with ❤️ using Streamlit, Pandas, and Folium | Data from NYC Open Data</small>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
