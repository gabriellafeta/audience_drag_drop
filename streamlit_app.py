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

# Sidebar for dynamic filtering
st.sidebar.header("Dynamic Filtering")
selected_feature = st.sidebar.selectbox("Select Feature to Filter", options=df.columns)

# Allow user to pick values for the selected feature
if selected_feature:
    unique_values = df[selected_feature].unique()
    selected_values = st.sidebar.multiselect(f"Select values for {selected_feature}", unique_values)

# Filter data based on user input
filtered_dataframes = {}
if selected_values:
    for value in selected_values:
        filtered_df = df[df[selected_feature] == value]
        filtered_dataframes[value] = filtered_df

# Let users specify file names for each filtered dataset
file_names = {}
if filtered_dataframes:
    st.sidebar.header("File Names")
    for value in filtered_dataframes.keys():
        file_name = st.sidebar.text_input(f"File name for {value} data", f"{value}_stores.csv")
        file_names[value] = file_name

# Display filtered datasets
st.write("Filtered Data:")
for value, filtered_df in filtered_dataframes.items():
    st.write(f"**{value} Stores:**")
    st.dataframe(filtered_df)

# Save filtered datasets as CSV in memory with user-defined file names
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, "w") as zf:
    for value, filtered_df in filtered_dataframes.items():
        csv_buffer = io.StringIO()
        filtered_df.to_csv(csv_buffer, index=False)
        # Use the user-defined file name
        zf.writestr(file_names[value], csv_buffer.getvalue())

zip_buffer.seek(0)

# Download button for ZIP file
if filtered_dataframes:
    st.download_button(
        label="Download Filtered Data as ZIP",
        data=zip_buffer,
        file_name="filtered_data.zip",
        mime="application/zip"
    )