import pandas as pd

# Load CSV file
print("Loading data...")
df = pd.read_csv("data/Sidewalk_Management_Database-Lot_Info_20250408.csv")
print("Data loaded successfully.")
print(f"Dataset shape: {df.shape}")
print("\nFirst 5 rows:")
print(df.head())

# Check for column names and rename if necessary
print("\nColumn names:")
print(df.columns.tolist())

# Rename columns to match expected names in the instructions
column_mapping = {
    "Borough, Block and Lot (BBL) ID": "bblid",
    "Block": "block",
    "Borough": "boro",
    "Lot": "lot",
    "ZIP Code": "zipcode",
}

df = df.rename(columns=column_mapping)
print("\nRenamed columns:")
print(df.columns.tolist())

# Check for missing values
print("\nChecking for missing values:")
missing_values = df.isnull().sum()
print(
    missing_values[missing_values > 0]
    if any(missing_values > 0)
    else "No missing values found."
)

# Group by zipcode and count inspections
print("\nAggregating data by zipcode...")
# Clean the zipcode column - extract just the 5-digit ZIP code
df["zipcode"] = df["zipcode"].str.extract(r"(\d{5})", expand=False)
# Drop rows with missing zipcodes
df = df.dropna(subset=["zipcode"])
print(f"After cleaning zipcode, dataset shape: {df.shape}")

zipcode_counts = df.groupby("zipcode").size().reset_index(name="inspection_count")
print("Data aggregated successfully.")
print("\nFirst 5 rows of zipcode counts:")
print(zipcode_counts.head())

# Compute the Sidewalk Wellness Score
print("\nComputing Sidewalk Wellness Score...")
max_count = zipcode_counts["inspection_count"].max()
zipcode_counts["wellness_score"] = (
    1 - (zipcode_counts["inspection_count"] / max_count)
) * 100
print("Wellness scores computed successfully.")
print("\nFirst 5 rows with wellness scores:")
print(zipcode_counts.head())

# Save processed data to CSV
print("\nSaving processed data...")
zipcode_counts.to_csv("data/wellness_scores.csv", index=False)
print("Data saved to 'data/wellness_scores.csv'")

# Print summary statistics
print("\nSummary statistics for wellness scores:")
print(zipcode_counts["wellness_score"].describe())
