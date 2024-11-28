import streamlit as st
import pandas as pd
import io
import zipfile
from azure.storage.blob import BlobServiceClient
from io import StringIO

# Azure connection string
connection_string = "DefaultEndpointsProtocol=https;AccountName=beesexpansion0001;AccountKey=QBAsqeUnSwNe7hKHJwWrKfH1XE0LpERqc/N/x5jg51pKCvoOgaZw0NvIgxKwyciZ2JxnnjdBbu0b+ASt9jRAaA==;EndpointSuffix=core.windows.net"

if connection_string is None:
    raise Exception("Environment variable AZURE_STORAGE_CONNECTION_STRING is not set.")

blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_name = 'expansionbees0001'
blob_name = 'audiences_pd.csv'

# Download the CSV from Azure Blob Storage
blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
blob_content = blob_client.download_blob().content_as_text()
audiences_pd = StringIO(blob_content)
df = pd.read_csv(audiences_pd)

# Sidebar for SKU input
st.sidebar.header("Input SKU Codes")
typed_skus = st.sidebar.text_input("Type SKU codes (comma-separated)")
sku_list = [sku.strip() for sku in typed_skus.split(",")] if typed_skus else []

# Column selection dropdown
column_to_output = st.sidebar.selectbox(
    "Select the column to include in output files",
    ["poc_id", "bees_account_id"]
)

# Segmentation column
segmentation_column = 'Segmentation'

# Apply filtering and generate files
if sku_list:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for sku in sku_list:
            for segment in df[segmentation_column].unique():
                # Filter dataset for the current SKU and segment
                filtered_df = df[(df['sku'] == sku) & (df[segmentation_column] == segment)]
                
                # Debug output: Show the filtered dataset for verification
                st.write(f"sku: {sku}, Segmentation: {segment}")
                st.write(filtered_df)
                
                # Extract only the selected column
                filtered_column_df = filtered_df[[column_to_output]] if not filtered_df.empty else pd.DataFrame()

                # Only add non-empty datasets to the ZIP file
                if not filtered_column_df.empty:
                    csv_buffer = io.StringIO()
                    file_name = f"{sku}_{segment}.csv"
                    filtered_column_df.to_csv(csv_buffer, index=False)
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