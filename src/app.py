import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
import os

# Set page configuration
st.set_page_config(
    page_title="NYC Sidewalk Wellness Score", page_icon="🚶", layout="wide"
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
    else:
        geo_df = None
        has_geo = False

    return wellness_df, geo_df, has_geo


# Main function
def main():
    # Add title and description
    st.title("NYC Sidewalk Wellness Score")
    st.markdown(
        """
    This dashboard visualizes the "health" or overall maintenance intensity of sidewalks in New York City by ZIP code.
    The Sidewalk Wellness Score is calculated based on inspection records - a lower inspection count corresponds to a higher wellness score.
    """
    )

    # Load data
    with st.spinner("Loading data..."):
        wellness_df, geo_df, has_geo = load_data()

    # Show data overview
    st.subheader("Data Overview")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total ZIP Codes", len(wellness_df))
        st.metric(
            "Average Wellness Score", f"{wellness_df['wellness_score'].mean():.2f}%"
        )

    with col2:
        st.metric(
            "Highest Wellness Score", f"{wellness_df['wellness_score'].max():.2f}%"
        )
        st.metric(
            "Lowest Wellness Score", f"{wellness_df['wellness_score'].min():.2f}%"
        )

    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Map", "Rankings", "Data Table"])

    # Tab 1: Map view
    with tab1:
        if has_geo:
            st.subheader("Sidewalk Wellness Score by ZIP Code")

            # Create a folium map centered on NYC
            m = folium.Map(location=[40.7128, -74.0060], zoom_start=10)

            # Add a choropleth layer
            folium.Choropleth(
                geo_data=geo_df,
                data=wellness_df,
                columns=["zipcode", "wellness_score"],
                key_on="feature.properties.zipcode",  # This might need adjustment based on the actual GeoJSON structure
                fill_color="YlGn",
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name="Wellness Score (%)",
                highlight=True,
            ).add_to(m)

            # Display the map using streamlit-folium
            folium_static(m, width=1000, height=600)

            st.caption(
                "A higher wellness score (darker green) indicates better sidewalk conditions."
            )
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
                color_continuous_scale="YlGn",
            )
            st.plotly_chart(fig, use_container_width=True)

    # Tab 2: Rankings
    with tab2:
        st.subheader("ZIP Code Rankings")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Top 10 ZIP Codes (Highest Wellness Score)")
            st.dataframe(
                wellness_df.sort_values("wellness_score", ascending=False)
                .head(10)
                .reset_index(drop=True)
                .style.background_gradient(subset=["wellness_score"], cmap="YlGn")
            )

        with col2:
            st.markdown("### Bottom 10 ZIP Codes (Lowest Wellness Score)")
            st.dataframe(
                wellness_df.sort_values("wellness_score")
                .head(10)
                .reset_index(drop=True)
                .style.background_gradient(subset=["wellness_score"], cmap="YlOrRd_r")
            )

        # Show distribution of wellness scores
        st.subheader("Distribution of Wellness Scores")
        fig = px.histogram(
            wellness_df,
            x="wellness_score",
            nbins=20,
            labels={"wellness_score": "Wellness Score (%)"},
            title="Distribution of Sidewalk Wellness Scores Across NYC ZIP Codes",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Tab 3: Data table
    with tab3:
        st.subheader("Complete Dataset")

        # Add a search box
        search_zip = st.text_input("Search by ZIP Code", "")

        if search_zip:
            filtered_df = wellness_df[
                wellness_df["zipcode"].astype(str).str.contains(search_zip)
            ]
        else:
            filtered_df = wellness_df

        # Show the data
        st.dataframe(
            filtered_df.sort_values("zipcode").style.background_gradient(
                subset=["wellness_score"], cmap="YlGn"
            ),
            height=600,
        )

        # Download option
        st.download_button(
            label="Download Data as CSV",
            data=wellness_df.to_csv(index=False).encode("utf-8"),
            file_name="nyc_sidewalk_wellness_scores.csv",
            mime="text/csv",
        )

    # Footer
    st.markdown("---")
    st.markdown(
        """
    **About the Wellness Score**: A lower number of inspections (implying fewer defects) corresponds to a higher score.
    The formula used is: `wellness_score = (1 - (inspection_count / max_inspection_count)) * 100`
    
    **Data Source**: NYC Sidewalk Management Database (Lot Info)
    """
    )


if __name__ == "__main__":
    main()
