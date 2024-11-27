import streamlit as st
import pandas as pd
import io
import zipfile
import pandas as pd
import streamlit as st
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.core.exceptions import ResourceExistsError
from io import StringIO
import os
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime



connection_string = "DefaultEndpointsProtocol=https;AccountName=beesexpansion0001;AccountKey=QBAsqeUnSwNe7hKHJwWrKfH1XE0LpERqc/N/x5jg51pKCvoOgaZw0NvIgxKwyciZ2JxnnjdBbu0b+ASt9jRAaA==;EndpointSuffix=core.windows.net"

if connection_string is None:
    raise Exception("Environment variable AZURE_STORAGE_CONNECTION_STRING is not set.")

blob_service_client = BlobServiceClient.from_connection_string(connection_string)

container_name = 'expansionbees0001'
container_client = blob_service_client.get_container_client(container_name)

blob_name = 'audiences_pd.csv'
blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
blob_content = blob_client.download_blob().content_as_text()
audiences_pd = StringIO(blob_content)
audiences_pd_df = pd.read_csv(audiences_pd)

df = pd.DataFrame(audiences_pd_df)

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
