# %%
import numpy as np
import matplotlib.pyplot as plt
import os
from osgeo import gdal

os.system(f"mc cp s3/oliviermeslin/BDALTI/BDALTI_D075.tif BDALTI.tif")

# Open the TIFF file
dataset = gdal.Open('BDALTI.tif', gdal.GA_ReadOnly)
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
from osgeo import gdal
import numpy as np
import pandas as pd

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

df = pd.DataFrame({
    'x': x_flat,
    'y': y_flat,
    'value': values_flat
})




# %%
import matplotlib.pyplot as plt
import numpy as np

# Assuming df columns: x, y, value
# Pivot to wide format to get 2D array for plotting
pivot_table = df.pivot(index='y', columns='x', values='value')

plt.figure()
plt.imshow(pivot_table, origin='lower', cmap='terrain', aspect='auto')
plt.colorbar(label='Raster value')
plt.xlabel('X coordinate')
plt.ylabel('Y coordinate')
plt.title('Raster Plot from Pandas DataFrame')
plt.show()


# %%
