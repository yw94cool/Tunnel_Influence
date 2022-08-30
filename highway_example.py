#!/usr/bin/env python
# coding: utf-8

# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"><li><span><a href="#load-highway-data" data-toc-modified-id="load-highway-data-1"><span class="toc-item-num">1&nbsp;&nbsp;</span>load highway data</a></span></li><li><span><a href="#tunnel-buffer-generation" data-toc-modified-id="tunnel-buffer-generation-2"><span class="toc-item-num">2&nbsp;&nbsp;</span>tunnel buffer generation</a></span></li><li><span><a href="#get-osm-buildings-and-write-to-shapfile" data-toc-modified-id="get-osm-buildings-and-write-to-shapfile-3"><span class="toc-item-num">3&nbsp;&nbsp;</span>get osm buildings and write to shapfile</a></span></li></ul></div>

# In[75]:


import pandas as pd
import geopandas as gpd
from shapely.geometry import *
from fiona.crs import from_epsg
import overpass
from shapely.wkt import loads

type_dict = {'node':1,'way':3,'relation':5}

### osm code
def simple_osm_gdf(bounding_txt='(35.5209663320001,139.562782238,35.8176034620001,139.918904167)',filter_attr='',geotype='way'):
    api = overpass.API()
    final_query = "%s%s%s" % (geotype,filter_attr,bounding_txt)
    features = api.Get(final_query,responseformat="geojson",verbosity='geom')
    feature_list = get_geojson_features_by_query_result(features,type=geotype)
    return gpd.GeoDataFrame.from_features(feature_list)

def get_geojson_features_by_query_result(response,type='relation',geometry_list=['multipolygon']):
    try:
        if (type == "relation") :
            # response = api.Get('%s(%s)' % (type, str(poi.id)), responseformat="json")
            elements = response['elements']
            feature_list = [get_relation_geojson_feature(element,geometry_list) for element in elements]
        else:
            features = response.get("features")
            feature_list = [update_geojson_feature_for_gdf(feature,['type'],poi_type=type_dict[type]) for feature in features]
        return feature_list
    except Exception as inst:
        print(inst)
        return []
    
def get_relation_geojson_feature(element,geometry_list=['multipolygon']):
    geometry_members = element['members']
    properties = element['tags']
    properties['id'] = element['id']
    assert properties['type'] in geometry_list
    properties['geotype'] = 5
    linelist = []
    for member in geometry_members :
        if member['type'] == 'way':
            geometry = get_geometry_by_id(member['ref'])
            linelist.append(geometry)
    try:
        geometry = MultiPolygon([Polygon(line) for line in list(linemerge(linelist))])
    except:
        try:
            geometry = Polygon(linemerge(linelist))
        except:
            geometry = linemerge(linelist)
    return {'geometry':geometry,'properties':properties,'id':element['id']}

def get_geojson_features_by_query_result(response,type='relation',geometry_list=['multipolygon']):
    try:
        if (type == "relation") :
            # response = api.Get('%s(%s)' % (type, str(poi.id)), responseformat="json")
            elements = response['elements']
            feature_list = [get_relation_geojson_feature(element,geometry_list) for element in elements]
        else:
            features = response.get("features")
            feature_list = [update_geojson_feature_for_gdf(feature,['type'],poi_type=type_dict[type]) for feature in features]
        return feature_list
    except Exception as inst:
        print(inst)
        return []

def update_geojson_feature_for_gdf(feature, filter_df=None,is_centroid=False,poi_type=None,if_total_info=False) :
    other_attributes = {key : value for key, value in feature.items() if key not in
                        (['geometry', 'properties'] if filter_df is None else ['geometry', 'properties'] + filter_df)}
    feature['properties'].update(other_attributes)
    feature['poi_type'] = poi_type
    return feature


# ## load highway data

# In[23]:


highway_gdf = gpd.read_file('highway/highway.shp')
tunnel_gdf = gpd.read_file('tunnel/tunnel.shp')


# ## tunnel buffer generation

# In[122]:


tunnel_buffer = tunnel_gdf.geometry.to_crs(from_epsg(7415)).buffer(350).to_crs(from_epsg(4326)).iloc[0]
xmin,ymin,xmax,ymax = tunnel_buffer.buffer(0.01).bounds


# ## get osm buildings and write to shapfile

# In[76]:


building_gdf_way = simple_osm_gdf(f'({ymin}, {xmin}, {ymax}, {xmax})',filter_attr='[building]',geotype='way')
building_gdf_way['geometry'] = building_gdf_way['geometry'].apply(lambda x:Polygon(x))
building_gdf_target = building_gdf_way[building_gdf_way.intersects(tunnel_buffer)]
building_gdf_target.geometry =  building_gdf_target['geometry'].apply(loads)
building_gdf_target[['geometry','building','id','source']].to_file('final_buildings/target_buildings.shp')


# In[80]:


### this returns blank value so there seems to be no buildings: 
building_gdf_relation = simple_osm_gdf(f'({ymin}, {xmin}, {ymax}, {xmax})',filter_attr='[building]',geotype='relation')

