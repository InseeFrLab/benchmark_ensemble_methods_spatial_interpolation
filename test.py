# %%
import os
import glob
import re
import requests
from osgeo import gdal
import s3fs
import py7zr

# Function to download a file from a URL
def download_file(url, local_path):
    response = requests.get(url)
    with open(local_path+url.rsplit('/', 1)[-1], 'wb') as f:
        f.write(response.content)
    print(f"Downloaded {url} to {local_path+url.rsplit('/', 1)[-1]}")

# Function to extract files to a path
def extract_files(archive_path, path, pattern = ""):
    # Extract all .asc files
    with py7zr.SevenZipFile(archive_path, mode='r') as archive:
        archive.extract(
            path=path, 
            targets=[f for f in archive.namelist() if re.search(pattern, f)]
        )

# Function to convert ASC to GeoTIFF using GDAL
def convert_asc_to_tiff(asc_path, tiff_path):
    gdal.Translate(tiff_path, asc_path, format='GTiff')
    print(f"Converted {asc_path} to {tiff_path}")

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
os.mkdir("./rawdata")
os.mkdir("./data")
os.mkdir("./finaldata")

# %%
# URL of the BD ALTI page
url = "https://geoservices.ign.fr/bdalti"

# Fetch the HTML content
html = requests.get(url).text

# Regex pattern to find all BDALTI download links
pattern = r"https://data\.geopf\.fr/telechargement/download/BDALTI/[^\s\"']+7z"

# Extract all matching URLs
urls = re.findall(pattern, html)

# Remove duplicates and sort
urls = sorted(set(urls))

# %%
archivename = asc_urls[0].rsplit('/', 1)[-1]
download_file(asc_urls[0], "./rawdata/")
# %%
# Extract all .asc files
with py7zr.SevenZipFile("./rawdata/"+archivename, mode='r') as archive:
    list_compressed_files = [f for f in archive.namelist() if re.search('1_DONNEES_LIVRAISON.*\\.asc', f)]
    archive.extract(path='./data/', targets=list_compressed_files)

# %% List the files
list_asc_files = glob.glob("data/**/*.asc", recursive=True)
print(list_asc_files)
# %%
# Convert the files to GeoTiff
convert_asc_to_tiff(
    list_asc_files[0],
    list_asc_files[0].rsplit('/', 1)[-1]
)

# %%

gdal.BuildVRT('out.vrt',glob.glob("data/**/*.asc", recursive=True))
gdal.Translate('out.tif','out.vrt',format='gtiff')
# %%
import numpy as np
import matplotlib.pyplot as plt

# Open the TIFF file
dataset = gdal.Open('out.tif', gdal.GA_ReadOnly)
band = dataset.GetRasterBand(1)
# Get NODATA value
nodata = band.GetNoDataValue()

# Read raster data as array
array = band.ReadAsArray()

# Mask nodata values by setting them to np.nan
if nodata is not None:
    array = np.where(array == nodata, np.nan, array)

# Plot using matplotlib
plt.imshow(array, cmap='terrain')
plt.colorbar()
plt.title('Map from GeoTIFF using GDAL')
plt.show()

# %%
local_directory = 'downloaded_asc'
s3_bucket = 'your-s3-bucket-name'

process_asc_files(asc_urls, local_directory, s3_bucket)



https://data.geopf.fr/telechargement/download/BDALTI/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D001_2023-08-08/BDALTIV2_2-0_25M_ASC_LAMB93-IGN69_D001_2023-08-08.7z




# %%
