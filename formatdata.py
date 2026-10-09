import pandas as pd

# File names
dataset_file = "2023_import.csv"
category_file = "categorized_commodities_final - Sheet5.csv"
output_file = "category_2023.csv"

# Load datasets
dataset = pd.read_csv(dataset_file, skiprows=4)  # Assuming headers start from 5th row
category_data = pd.read_csv(category_file)

# Rename columns for consistency
category_data.columns = ["Count", "Commodity", "Category"]

dataset = dataset.merge(category_data[["Commodity", "Category"]], on="Commodity", how="left")

dataset["Category"].fillna("Unknown", inplace=True)  # Handle unmatched commodities

# Aggregate trade values
df_aggregated = dataset.groupby(["Year", "Reporter Country", "Partner Country", "Category"], as_index=False)["Trade Value"].sum()

# Save to CSV
df_aggregated.to_csv(output_file, index=False)

print(f"Aggregation completed. Results saved to {output_file}")