import streamlit as st
import pandas as pd
import io
import zipfile

# Example dataset
data = {
    'SKU': ['S1', 'S2', 'S3', 'S4', 'S5', 'S1', 'S2', 'S3', 'S4', 'S5'],
    'Type': ['Big', 'Small', 'Big', 'Small', 'Big', 'Big', 'Small', 'Big', 'Small', 'Big'],
    'Location': ['North', 'South', 'East', 'West', 'North', 'North', 'South', 'East', 'West', 'North'],
    'Segmentation': ['Segment1', 'Segment2', 'Segment1', 'Segment2', 'Segment3', 'Segment2', 'Segment3', 'Segment2', 'Segment1', 'Segment3'],
    'Sales': [1000, 500, 1200, 400, 1100, 900, 600, 1300, 450, 1150]
}
df = pd.DataFrame(data)

# Sidebar for SKU input
st.sidebar.header("Input SKU Codes")
typed_skus = st.sidebar.text_input("Type SKU codes (comma-separated)")
sku_list = [sku.strip() for sku in typed_skus.split(",")] if typed_skus else []

# Segmentation column
segmentation_column = 'Segmentation'

# Apply filtering and generate files
if sku_list:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for sku in sku_list:
            for segment in df[segmentation_column].unique():
                # Filter dataset for the current SKU and segment
                filtered_df = df[(df['SKU'] == sku) & (df[segmentation_column] == segment)]
                
                # Debug output: Show the filtered dataset for verification
                st.write(f"SKU: {sku}, Segmentation: {segment}")
                st.write(filtered_df)
                
                # Only add non-empty datasets to the ZIP file
                if not filtered_df.empty:
                    csv_buffer = io.StringIO()
                    file_name = f"filtered_data_{sku}_{segment}.csv"
                    filtered_df.to_csv(csv_buffer, index=False)
                    zf.writestr(file_name, csv_buffer.getvalue())
                else:
                    st.write(f"No data for SKU: {sku}, Segmentation: {segment}")
    
    zip_buffer.seek(0)
    
    # Download ZIP file
    st.download_button(
        label="Download SKU and Segmentation Filtered Data as ZIP",
        data=zip_buffer,
        file_name="sku_segmented_filtered_data.zip",
        mime="application/zip"
    )
else:
    st.write("Please input SKU codes to generate filtered files.")