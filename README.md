## BuildingDetecion

This repository contains the code and results of the Building detection from point cloud


## Requirements

### Environment

1. Python 3.8.*
2. pandas
3. geopandas
4. fiona
5. overpass
6. shapely
7. scikit-learn
8. alphashape

### Install
Create a  virtual environment and activate it.
```shell
conda create -n 3Dseg python=3.8
conda activate 3Dseg
conda install geopandas
conda install scikit-learn
pip install alphashape

```


### Dataset
To evaluate the proposed code, you will need to prepared required datasets as the folder structure shows bellow. The provided raw .laz file will format into .las in the folder ./data, and the results will store in./results. According to our test, we select an area of interest in size of 1000*1000 meter in EPSG:7415 to test the codes.


```Shell
├── yuan_proj
    ├── data
    ├── results
    

```

### Extraction results
![alt text](./clusteredbuilding.png)
![alt text](./clusteredbuilding_overlay_raw.png)
![alt text](./clusteredbuilding_overlay_satellite.png)
![alt text](./buildingpoly_raw.png)
![alt text](./buildingpoly_cluster.png)
![alt text](./Buildingpoly_Satellite.png)

Results are shown in six different ways, segment interest object (building) point clouds/polygons  with Google satellite image background, with raw points classify index and without any background. All the results are visualized in QGIS.


###  Interest Objects Search strategies
First, visualize the given points cloud in QGIS.
According to the visualization results, the .las file has already been classified. Then choose to clustering the Building object.

![alt text](./overlay_point_Satellite.png)
![alt text](./ground.png)
![alt text](./building.png)
![alt text](./water.png)


#### 1. preprosessing the data for ML based clustering   
```function
building_pts
building_pts_gdf
```
#### 2. using OPTIC method clustering the extracted building points for individual building segmentation
```function
clustering = OPTICS(min_samples=80).fit(building_pts_crop)
```
#### 3. Using the segmented results for individual object boundary extraction
```function
building_poly=alphashape.alphashape(building_to_poly.geometry, alpha=1)
```

### Acknowledgment
```
If you have any questions please find contacts Dr. Yuan at: milowei304@gmail.com
}
```
