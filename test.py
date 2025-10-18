# %%
import os
import requests
from osgeo import gdal
import boto3

# Function to download a file from a URL
def download_file(url, local_path):
    response = requests.get(url)
    response.raise_for_status()
    with open(local_path, 'wb') as f:
        f.write(response.content)
    print(f"Downloaded {url} to {local_path}")

# Function to convert ASC to GeoTIFF using GDAL
def convert_asc_to_tiff(asc_path, tiff_path):
    gdal.Translate(tiff_path, asc_path, format='GTiff')
    print(f"Converted {asc_path} to {tiff_path}")

# Function to upload file to S3
def upload_to_s3(local_path, bucket_name, s3_key):
    s3_client = boto3.client('s3')
    s3_client.upload_file(local_path, bucket_name, s3_key)
    print(f"Uploaded {local_path} to s3://{bucket_name}/{s3_key}")

# Main process
def process_asc_files(asc_urls, local_dir, bucket_name):
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    for url in asc_urls:
        filename = url.split('/')[-1]
        asc_path = os.path.join(local_dir, filename)
        tiff_filename = filename.replace('.asc', '.tif')
        tiff_path = os.path.join(local_dir, tiff_filename)

        # Download ASC file
        download_file(url, asc_path)

        # Convert ASC to GeoTIFF
        convert_asc_to_tiff(asc_path, tiff_path)

        # Upload GeoTIFF to S3
        upload_to_s3(tiff_path, bucket_name, tiff_filename)
# %%

# Example usage
asc_urls = [
    'https://example.com/elevation1.asc',
    'https://example.com/elevation2.asc'
]
local_directory = 'downloaded_asc'
s3_bucket = 'your-s3-bucket-name'

process_asc_files(asc_urls, local_directory, s3_bucket)



https://data.geopf.fr/telechargement/download/BDALTI/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D001_2023-08-08/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D001_2023-08-08.7z



