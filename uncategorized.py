import pandas as pd

# File names
category_file = "uncategorized.csv"
output_file = "categorized_commodities_new.csv"

# Load dataset
category_data = pd.read_csv(category_file)

# Rename columns for consistency
category_data.columns = ["Count", "Description", "Category"]

# Define keyword-based mapping for classification
category_mapping = {
    "Agri-Food & Beverages": ["food", "beverage", "milk", "egg", "whey", "albumin"],
    "Industrial Equipment, Machinery and technology": ["machinery", "equipment", "technology", "industrial"],
    "Consumer Goods": ["consumer", "articles", "plastic", "paper", "books", "printed"],
    "Energy and Fuel Products": ["fuel", "energy", "oil", "gas", "coal"],
    "Natural Resources (Non-Fuel)": ["wood", "metal", "ores", "minerals"],
    "Textile": ["textile", "fabric", "clothing", "vests", "t-shirts", "singlets"],
    "Pharmaceuticals and chemicals": ["chemical", "pharmaceutical", "medicine", "drugs"],
    "Transportation Vehicles and Equipment": ["vehicles", "transportation", "automobile", "aircraft", "train"],
    "Luxury and High-End Products": ["luxury", "high-end", "jewelry", "gold", "silver", "designer"]
}

# Function to categorize based on description
def categorize(description):
    description = str(description).lower()
    for category, keywords in category_mapping.items():
        if any(keyword in description for keyword in keywords):
            return category
    return "Uncategorized"

# Apply categorization
category_data["Category"] = category_data["Description"].apply(categorize)

# Save categorized data
category_data.to_csv(output_file, index=False)

print(f"Categorization completed. Results saved to {output_file}")
