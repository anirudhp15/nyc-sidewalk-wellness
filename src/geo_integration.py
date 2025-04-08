import geopandas as gpd
import pandas as pd
import json


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

    # Look at all columns to find zipcode field
    print("\nAll columns in geospatial data:")
    for col in nyc_zips.columns:
        print(f" - {col}")

    # Look at the zipcode field in the geojson file
    print("\nPotential ZIP code fields in geospatial data:")
    potential_fields = []
    for col in nyc_zips.columns:
        if any(term in col.lower() for term in ["zip", "post", "code", "postal"]):
            print(f" - {col}")
            potential_fields.append(col)

    # Check the first few rows to identify the zip code field
    print("\nFirst few rows of geospatial data:")
    print(nyc_zips.head())

    # Determine the correct field for ZIP codes in the geospatial data
    zipcode_field = None

    # First try exact matches for common field names
    common_zipcode_fields = [
        "postalCode",
        "zipcode",
        "ZIPCODE",
        "ZIP",
        "zip_code",
        "postal_code",
    ]
    for field in common_zipcode_fields:
        if field in nyc_zips.columns:
            zipcode_field = field
            print(f"\nFound exact match for ZIP code field: '{zipcode_field}'")
            break

    # If no exact match, check the potential fields
    if not zipcode_field and potential_fields:
        # Sample some values to check if they match expected ZIP code format
        for field in potential_fields:
            sample_values = nyc_zips[field].dropna().astype(str).head(5).tolist()
            print(f"\nSample values for '{field}':")
            print(sample_values)

            # Check if values look like ZIP codes (5 digits or 5+4 digits)
            zip_like = all(
                (len(val) == 5 and val.isdigit())
                or (len(val) == 10 and val[5] == "-" and val.replace("-", "").isdigit())
                for val in sample_values
                if val
            )

            if zip_like:
                zipcode_field = field
                print(
                    f"\nSelected '{zipcode_field}' as it contains ZIP code-like values."
                )
                break

    # If still no match, use the first potential field as a fallback
    if not zipcode_field and potential_fields:
        zipcode_field = potential_fields[0]
        print(f"\nUsing '{zipcode_field}' as the ZIP code field (best guess).")

    # If no potential fields found at all, examine the GeoJSON directly
    if not zipcode_field:
        print(
            "\nCouldn't identify ZIP code field from column names. Examining GeoJSON properties directly..."
        )

        # Load the GeoJSON file to examine its structure
        with open("data/geo/nyc_zipcodes.geojson", "r") as f:
            geojson_data = json.load(f)

        if "features" in geojson_data and len(geojson_data["features"]) > 0:
            # Examine properties of the first feature
            if "properties" in geojson_data["features"][0]:
                properties = geojson_data["features"][0]["properties"]
                print("\nProperties in the first GeoJSON feature:")
                for key, value in properties.items():
                    print(f" - {key}: {value}")

                # Look for ZIP code-like fields in properties
                for key, value in properties.items():
                    if isinstance(value, (str, int)) and any(
                        term in key.lower()
                        for term in ["zip", "post", "code", "postal"]
                    ):
                        zipcode_field = key
                        print(f"\nSelected '{zipcode_field}' from GeoJSON properties.")
                        break

        # If we found a property but it's not in the DataFrame columns, add it
        if zipcode_field and zipcode_field not in nyc_zips.columns:
            print(f"\nAdding '{zipcode_field}' from GeoJSON properties to DataFrame.")
            nyc_zips[zipcode_field] = nyc_zips.apply(
                lambda row: (
                    row["geometry"].properties.get(zipcode_field)
                    if hasattr(row["geometry"], "properties")
                    else None
                ),
                axis=1,
            )

    # Final check - if still no field found, create a new field from first potential ZIP code found
    if not zipcode_field:
        print(
            "\nCouldn't identify ZIP code field. Creating a new field based on the first 5-digit value in each row..."
        )

        # Examine all string columns for 5-digit values
        for col in nyc_zips.columns:
            if nyc_zips[col].dtype == "object":  # String columns
                # Try to extract 5-digit values
                nyc_zips["extracted_zipcode"] = (
                    nyc_zips[col].astype(str).str.extract(r"(\d{5})", expand=False)
                )
                if (
                    nyc_zips["extracted_zipcode"].notna().sum() > len(nyc_zips) * 0.5
                ):  # If more than 50% rows have values
                    zipcode_field = "extracted_zipcode"
                    print(
                        f"\nCreated 'extracted_zipcode' field from values in '{col}'."
                    )
                    break

    # If we still don't have a zipcode field, we need to create one
    if not zipcode_field:
        print(
            "\nWARNING: Couldn't identify or create a ZIP code field. Merging will fail."
        )
        return None

    print(f"\nUsing '{zipcode_field}' as the ZIP code field for merging.")

    # Merge the wellness scores with the geospatial data
    print(f"\nMerging data on {zipcode_field}...")
    # Ensure the ZIP codes are treated as strings in both datasets for merging
    nyc_zips[zipcode_field] = nyc_zips[zipcode_field].astype(str)
    wellness_df["zipcode"] = wellness_df["zipcode"].astype(str)

    # Add zipcode as a separate column if it doesn't match the zipcode_field name
    if zipcode_field != "zipcode":
        nyc_zips["zipcode"] = nyc_zips[zipcode_field]

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
        if len(missing_scores) < 10:
            print("Missing ZIP codes:")
            for idx, row in missing_scores.iterrows():
                print(f" - {row[zipcode_field]}")

    # Save the merged data
    print("\nSaving merged geospatial data with wellness scores...")
    merged.to_file("data/geo/nyc_wellness_scores.geojson", driver="GeoJSON")
    print("Saved to 'data/geo/nyc_wellness_scores.geojson'")

    return merged


if __name__ == "__main__":
    integrate_geo_data()
