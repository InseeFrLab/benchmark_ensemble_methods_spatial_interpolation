# %%
import numpy as np
import polars as pl
import matplotlib.pyplot as plt
import os
from osgeo import gdal
import s3fs
import re
# %%
# Connect to S3
fs = s3fs.S3FileSystem(anon=False)  # set anon=True for public buckets

# Define your S3 path
path = 's3://oliviermeslin/BDALTI/'

# List all files recursively
files = fs.ls(path, detail=False)
# %%
for file in files[0:1]:
    print(file)

    # Extract the area
    area = re.search(r'(\w{2})\.tif$', file).group(1)
    print(area)

    # Download the data
    os.system(f"mc cp s3/{file} BDALTI.tif")

    # Open the TIFF file
    dataset = gdal.Open('BDALTI.tif', gdal.GA_ReadOnly)
    band = dataset.GetRasterBand(1)
    
    # Read raster data
    data = band.ReadAsArray()

    # Get NODATA value
    nodata = band.GetNoDataValue()

    # Create mask for valid data pixels
    if nodata is not None:
        valid_mask = data != nodata
    else:
        # If no nodata value assigned, create mask with non-zero data (optional)
        valid_mask = np.ones(data.shape, dtype=bool)

    # Geotransform
    gt = dataset.GetGeoTransform()
    rows, cols = data.shape
    col_indices = np.arange(cols)
    row_indices = np.arange(rows)
    col_grid, row_grid = np.meshgrid(col_indices, row_indices)

    # Calculate coordinates for all pixels
    x_coords = gt[0] + col_grid * gt[1] + row_grid * gt[2]
    y_coords = gt[3] + col_grid * gt[4] + row_grid * gt[5]

    # Flatten all arrays
    x_flat = x_coords.flatten()
    y_flat = y_coords.flatten()
    values_flat = data.flatten()
    mask_flat = valid_mask.flatten()

    # Assign NaN to invalid pixels
    values_flat = np.where(mask_flat, values_flat, np.nan)

    # Convert to Polars
    df = pl.DataFrame(
        {
            'x': x_flat,
            'y': y_flat,
            'value': values_flat,
            'departement': area
        }
    )

    # Write to S3
    with fs.open(path, "wb") as f:
        df.write_parquet(
            "s3://oliviermeslin/BDALTI_parquet/",
            use_pyarrow=True,
            pyarrow_options={"partition_cols": ["departement"]}
        )

# %%
from osgeo import gdal, ogr

# Open the raster
src_ds = gdal.Open("BDALTI.tif")
src_band = src_ds.GetRasterBand(1)

# Create output shapefile
driver = ogr.GetDriverByName("ESRI Shapefile")
out_ds = driver.CreateDataSource("BDALTI.shp")
out_layer = out_ds.CreateLayer("polygons", geom_type=ogr.wkbPolygon, srs=None)

# Add an attribute field to the shapefile
field_defn = ogr.FieldDefn("value", ogr.OFTReal)
out_layer.CreateField(field_defn)

# Perform polygonization
gdal.Polygonize(src_band, None, out_layer, 0, [], callback=None)
# %%
os.system("mc cp BDALTI.shp s3/oliviermeslin/BDALTI2/BDALTI_D035.shp")
os.system("mc cp BDALTI.dbf s3/oliviermeslin/BDALTI2/BDALTI_D035.dbf")
os.system("mc cp BDALTI.shx s3/oliviermeslin/BDALTI2/BDALTI_D035.shx")

# %%
ds = gdal.Open("BDALTI.tif")
band = ds.GetRasterBand(1)

# Read raster data
data = band.ReadAsArray()
nodata = band.GetNoDataValue()

# Create mask for valid data pixels
if nodata is not None:
    valid_mask = data != nodata
else:
    # If no nodata value assigned, create mask with non-zero data (optional)
    valid_mask = np.ones(data.shape, dtype=bool)

# Geotransform
gt = ds.GetGeoTransform()
rows, cols = data.shape
col_indices = np.arange(cols)
row_indices = np.arange(rows)
col_grid, row_grid = np.meshgrid(col_indices, row_indices)

# Calculate coordinates for all pixels
x_coords = gt[0] + col_grid * gt[1] + row_grid * gt[2]
y_coords = gt[3] + col_grid * gt[4] + row_grid * gt[5]

# Flatten all arrays
x_flat = x_coords.flatten()
y_flat = y_coords.flatten()
values_flat = data.flatten()
mask_flat = valid_mask.flatten()

# Assign NaN to invalid pixels
values_flat = np.where(mask_flat, values_flat, np.nan)

# %%
# Convert to Polars
df = pl.DataFrame({
    'x': x_flat,
    'y': y_flat,
    'value': values_flat,
    'departement': "A AJOUTER"
})
df.head(10)

# Write to S3


# %%
import matplotlib.pyplot as plt
import numpy as np

# Assuming df columns: x, y, value
# Pivot to wide format to get 2D array for plotting
pivot_table = df.to_pandas().pivot(index='y', columns='x', values='value')

plt.figure()
plt.imshow(pivot_table, origin='lower', cmap='terrain', aspect='auto')
plt.colorbar(label='Raster value')
plt.xlabel('X coordinate')
plt.ylabel('Y coordinate')
plt.title('Raster Plot from Pandas DataFrame')
plt.show()


# %%
