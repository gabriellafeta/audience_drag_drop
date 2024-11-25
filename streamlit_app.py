import streamlit as st
import pandas as pd
import io
import zipfile

# Example dataset
data = {
    'Store': ['A', 'B', 'C', 'D', 'E'],
    'Type': ['Big', 'Small', 'Big', 'Small', 'Big'],
    'Location': ['North', 'South', 'East', 'West', 'North'],
    'Sales': [1000, 500, 1200, 400, 1100]
}
df = pd.DataFrame(data)

# Sidebar for multiple filters
st.sidebar.header("Define Filter Combinations")

# Number of filter combinations
num_filters = st.sidebar.number_input("How many filter combinations?", min_value=1, step=1, value=1)

# Collect filter criteria for each combination
filter_combinations = []
for i in range(num_filters):
    st.sidebar.write(f"Filter Combination {i+1}")
    filters = {}
    selected_features = st.sidebar.multiselect(f"Select Features for Combination {i+1}", options=df.columns, key=f"features_{i}")
    for feature in selected_features:
        unique_values = df[feature].unique()
        selected_values = st.sidebar.multiselect(f"Select values for {feature} in Combination {i+1}", unique_values, key=f"values_{i}_{feature}")
        if selected_values:
            filters[feature] = selected_values
    if filters:
        file_name = st.sidebar.text_input(f"File name for Combination {i+1}", f"filtered_data_{i+1}.csv")
        filter_combinations.append((filters, file_name))

# Apply filters and create files
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, "w") as zf:
    for filters, file_name in filter_combinations:
        filtered_df = df.copy()
        for feature, values in filters.items():
            filtered_df = filtered_df[filtered_df[feature].isin(values)]
        
        if not filtered_df.empty:
            csv_buffer = io.StringIO()
            filtered_df.to_csv(csv_buffer, index=False)
            zf.writestr(file_name, csv_buffer.getvalue())

zip_buffer.seek(0)

# Download ZIP file
if filter_combinations:
    st.download_button(
        label="Download All Filtered Data as ZIP",
        data=zip_buffer,
        file_name="filtered_data.zip",
        mime="application/zip"
    )