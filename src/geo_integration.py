import geopandas as gpd
import pandas as pd


def integrate_geo_data():
    """
    Merge the wellness scores with the geospatial data for NYC ZIP codes.
    """
    print("Loading wellness scores data...")
    wellness_df = pd.read_csv("data/wellness_scores.csv")
    print(f"Loaded {len(wellness_df)} ZIP code wellness scores.")

    print("\nLoading NYC ZIP code boundary data...")
    nyc_zips = gpd.read_file("data/geo/nyc_zipcodes.geojson")
    print(f"Loaded {len(nyc_zips)} ZIP code boundaries.")

    # Look at the zipcode field in the geojson file
    print("\nZIP code field in geospatial data:")
    for col in nyc_zips.columns:
        if "zip" in col.lower() or "post" in col.lower():
            print(f"Potential zipcode field: {col}")

    # Check the first few rows to identify the zip code field
    print("\nFirst few rows of geospatial data:")
    print(nyc_zips.head())

    # Determine the correct field for ZIP codes in the geospatial data
    # (We'll assume it's 'postalCode' based on typical GeoJSON standards,
    # but will need to adjust if the field name is different)
    zipcode_field = "postalCode"
    if zipcode_field not in nyc_zips.columns:
        # If our assumption is wrong, try to find it
        potential_fields = [
            col
            for col in nyc_zips.columns
            if "zip" in col.lower() or "postal" in col.lower() or "code" in col.lower()
        ]
        if potential_fields:
            zipcode_field = potential_fields[0]
            print(f"\nUsing '{zipcode_field}' as the ZIP code field.")
        else:
            print(
                "\nCouldn't identify ZIP code field. Please check the GeoJSON file structure."
            )
            return None

    # Merge the wellness scores with the geospatial data
    print(f"\nMerging data on {zipcode_field}...")
    # Ensure the ZIP codes are treated as strings in both datasets for merging
    nyc_zips[zipcode_field] = nyc_zips[zipcode_field].astype(str)
    wellness_df["zipcode"] = wellness_df["zipcode"].astype(str)

    # Merge the datasets
    merged = nyc_zips.merge(
        wellness_df, left_on=zipcode_field, right_on="zipcode", how="left"
    )

    print(f"Merged data has {len(merged)} rows.")

    # Check for ZIP codes that didn't match
    missing_scores = merged[merged["wellness_score"].isna()]
    if len(missing_scores) > 0:
        print(
            f"\nWarning: {len(missing_scores)} ZIP codes in the geospatial data don't have wellness scores."
        )

    # Save the merged data
    print("\nSaving merged geospatial data with wellness scores...")
    merged.to_file("data/geo/nyc_wellness_scores.geojson", driver="GeoJSON")
    print("Saved to 'data/geo/nyc_wellness_scores.geojson'")

    return merged


if __name__ == "__main__":
    integrate_geo_data()
