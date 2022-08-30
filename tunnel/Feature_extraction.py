import pylas
import numpy as np
from sklearn.cluster import OPTICS
import fiona
from shapely.geometry import Point, Polygon, mapping
import pandas as pd
import geopandas as gpd
import alphashape


# Extract usefull information from input data

def return_xyzc(point):
    x = point[0]
    y = point[1]
    z = point[2]
    c = point[5]
    return [x, y, z, c]

# Input las file

input_las_path = '/data/C_37EZ1_crop1.las'
cloud = pylas.read(input_las_path)

# Extract interests object for futher processing
points = [return_xyzc(i) for i in cloud]
building_pts = [point for point in points if point[3] == 6]

# ML based clustering for indivisual segmentation
building_pts_gdf = [[i[0], i[1]] for i in building_pts]
building_pts_crop = np.array(building_pts_gdf[0:100000])
clustering = OPTICS(min_samples=80).fit(building_pts_crop)
clusteringres = np.column_stack((building_pts_crop, clustering.labels_))

# Write the 3D segmentation for visualization
schema = {'geometry': 'Point',
          'properties': {'BuildingID': 'int'}}


with fiona.open('./results/building.shp', mode='w', driver='ESRI Shapefile',
                schema=schema, crs='EPSG:7415', encoding='utf-8') as layer:
    for i in clusteringres:
        point = Point(i[0]*0.001+80000, i[1]*0.001+437500)
        point = mapping(point)
        buildingindex = int(i[2])
        feature = {'geometry': point,
                   'properties': {'BuildingID': buildingindex}}
        layer.write(feature)

# Preparing data structure for polygon extraction
longitude = [x[0] * 0.001 + 80000 for x in building_pts_crop]
latitude = [x[1]*0.001+437500 for x in building_pts_crop]
df = pd.DataFrame({'BuildingID': clustering.labels_, 'longitude': longitude, 'latitude': latitude})
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longtitude, df.latitude))


schema1 = {'geometry': 'Polygon',
          'properties': {'BuildingID': 'int'}}

# Write the extracted polygon for visualization
with fiona.open('./results/building_poly.shp', mode='w', driver='ESRI Shapefile',
                schema=schema1, crs='EPSG:7415', encoding='utf-8') as layer:
    c = len(gdf.BuildingID.value_counts())
    for i in range(c-1):
        building_to_poly = gdf[gdf.BuildingID == i]
        building_poly = alphashape.alphashape(building_to_poly.geometry, alpha=1)
        poly = mapping(building_poly)
        buildingindex= i
        feature = {'geometry': poly, 'properties': {'BuildingID': buildingindex}}
        layer.write(feature)
del df
del gdf
