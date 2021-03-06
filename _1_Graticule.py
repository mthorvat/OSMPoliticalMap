# create graticule for the whole world
# USAGE: python _1_Graticule.py step density
# "step" is integer distance between meridians and parallels
# "density" is float distance between vertices in meridians and paralles
# output will be in directory PK/01_graticule with shapefiles frame_final.shp, meridians_final.shp, parallels_final.shp, tropics_final.shp

import ogr, osr, sys, os

step = int(sys.argv[1])
density = float(sys.argv[2])

driver = ogr.GetDriverByName('ESRI Shapefile')

# create the spatial reference, WGS84
srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)

#set relative path of output folder
folder = './01_graticule/'

#create output directory
if not os.path.exists(folder):
    os.makedirs(folder)

# MERIDIANS

# create the output layer
outputShapefile = folder+'meridians_wgs84.shp'
if os.path.exists(outputShapefile):
    driver.DeleteDataSource(outputShapefile)
outDataSet = driver.CreateDataSource(outputShapefile)
outLayer = outDataSet.CreateLayer('meridians', srs, geom_type=ogr.wkbLineString, options=['ENCODING=UTF8'])

# Add the field for longitude label
outLayer.CreateField(ogr.FieldDefn('longitude', ogr.OFTInteger))

# get the output layer's feature definition
outLayerDefn = outLayer.GetLayerDefn()

for lon in range(-180,180+1,step):
    line = ogr.Geometry(ogr.wkbLineString)
    lat = -90
    line.AddPoint(lon, lat)
    while lat < 90 - density:
        lat = lat + density
        line.AddPoint(lon, lat)
    lat = 90
    line.AddPoint(lon, lat)
    # create a new feature
    outFeature = ogr.Feature(outLayerDefn)
    # set the geometry and attribute
    outFeature.SetGeometry(line)
    outFeature.SetField('longitude', lon)
    # add the feature to the shapefile
    outLayer.CreateFeature(outFeature)
    # destroy the features and get the next input feature
    outFeature.Destroy()

# close the shapefile
outDataSet.Destroy()  
   

# PARALLELS

# create the output layer
outputShapefile = folder+'parallels_wgs84.shp'
if os.path.exists(outputShapefile):
    driver.DeleteDataSource(outputShapefile)
outDataSet = driver.CreateDataSource(outputShapefile)
outLayer = outDataSet.CreateLayer('parallels', srs, geom_type=ogr.wkbLineString, options=['ENCODING=UTF8'])

# Add the field for longitude label
outLayer.CreateField(ogr.FieldDefn('latitude', ogr.OFTInteger))

# get the output layer's feature definition
outLayerDefn = outLayer.GetLayerDefn()

for lat in range(-90,90+1,step):
    line = ogr.Geometry(ogr.wkbLineString)
    lon = -180
    line.AddPoint(lon, lat)
    while lon < 180 - density:
        lon = lon + density
        line.AddPoint(lon, lat)
    lon = 180
    line.AddPoint(lon, lat)
    # create a new feature
    outFeature = ogr.Feature(outLayerDefn)
    # set the geometry and attribute
    outFeature.SetGeometry(line)
    outFeature.SetField('latitude', lat)
    # add the feature to the shapefile
    outLayer.CreateFeature(outFeature)
    # destroy the features and get the next input feature
    outFeature.Destroy()

# close the shapefile
outDataSet.Destroy()     


# TROPICS

# create the output layer
outputShapefile = folder+'tropics_wgs84.shp'
if os.path.exists(outputShapefile):
    driver.DeleteDataSource(outputShapefile)
outDataSet = driver.CreateDataSource(outputShapefile)
outLayer = outDataSet.CreateLayer('tropics', srs, geom_type=ogr.wkbLineString, options=['ENCODING=UTF8'])

# Add the field for longitude label
field_name = ogr.FieldDefn("name_en", ogr.OFTString)
field_name.SetWidth(30)
outLayer.CreateField(field_name)
field_name = ogr.FieldDefn("name_hr", ogr.OFTString)
field_name.SetWidth(30)
outLayer.CreateField(field_name)

# get the output layer's feature definition
outLayerDefn = outLayer.GetLayerDefn()

#Antarctic Circle
lat = -66.56083   
line = ogr.Geometry(ogr.wkbLineString)
lon = -180
line.AddPoint(lon, lat)
while lon < 180 - density:
    lon = lon + density
    line.AddPoint(lon, lat)
lon = 180
line.AddPoint(lon, lat)
# create a new feature
outFeature = ogr.Feature(outLayerDefn)
# set the geometry and attribute
outFeature.SetGeometry(line)
outFeature.SetField('name_en', 'Antarctic Circle')
outFeature.SetField('name_hr', u'Ju\u017Ena polarnica'.encode('utf-8'))
# add the feature to the shapefile
outLayer.CreateFeature(outFeature)
# destroy the features and get the next input feature
outFeature.Destroy()

#Tropic of Capricorn
lat = -23.45
line = ogr.Geometry(ogr.wkbLineString)
lon = -180
line.AddPoint(lon, lat)
while lon < 180 - density:
    lon = lon + density
    line.AddPoint(lon, lat)
lon = 180
line.AddPoint(lon, lat)
# create a new feature
outFeature = ogr.Feature(outLayerDefn)
# set the geometry and attribute
outFeature.SetGeometry(line)
outFeature.SetField('name_en', 'Tropic of Capricorn')
outFeature.SetField('name_hr', u'Ju\u017Ena obratnica'.encode('utf-8'))
# add the feature to the shapefile
outLayer.CreateFeature(outFeature)
# destroy the features and get the next input feature
outFeature.Destroy()

#Equator
lat = 0
line = ogr.Geometry(ogr.wkbLineString)
lon = -180
line.AddPoint(lon, lat)
while lon < 180 - density:
    lon = lon + density
    line.AddPoint(lon, lat)
lon = 180
line.AddPoint(lon, lat)
# create a new feature
outFeature = ogr.Feature(outLayerDefn)
# set the geometry and attribute
outFeature.SetGeometry(line)
outFeature.SetField('name_en', 'Equator')
outFeature.SetField('name_hr', 'Ekvator')
# add the feature to the shapefile
outLayer.CreateFeature(outFeature)
# destroy the features and get the next input feature
outFeature.Destroy()

#Tropic of Cancer
lat = 23.45
line = ogr.Geometry(ogr.wkbLineString)
lon = -180
line.AddPoint(lon, lat)
while lon < 180 - density:
    lon = lon + density
    line.AddPoint(lon, lat)
lon = 180
line.AddPoint(lon, lat)
# create a new feature
outFeature = ogr.Feature(outLayerDefn)
# set the geometry and attribute
outFeature.SetGeometry(line)
outFeature.SetField('name_en', 'Tropic of Cancer')
outFeature.SetField('name_hr', 'Sjeverna obratnica')
# add the feature to the shapefile
outLayer.CreateFeature(outFeature)
# destroy the features and get the next input feature
outFeature.Destroy()

#Arctic Circle
lat = 66.56083
line = ogr.Geometry(ogr.wkbLineString)
lon = -180
line.AddPoint(lon, lat)
while lon < 180 - density:
    lon = lon + density
    line.AddPoint(lon, lat)
lon = 180
line.AddPoint(lon, lat)
# create a new feature
outFeature = ogr.Feature(outLayerDefn)
# set the geometry and attribute
outFeature.SetGeometry(line)
outFeature.SetField('name_en', 'Arctic Circle')
outFeature.SetField('name_hr', 'Sjeverna polarnica')
# add the feature to the shapefile
outLayer.CreateFeature(outFeature)
# destroy the features and get the next input feature
outFeature.Destroy()

# close the shapefile
outDataSet.Destroy()     


# FRAME

# create the output layer
outputShapefile = folder+'frame_wgs84.shp'
if os.path.exists(outputShapefile):
    driver.DeleteDataSource(outputShapefile)
outDataSet = driver.CreateDataSource(outputShapefile)
outLayer = outDataSet.CreateLayer('frame', srs, geom_type=ogr.wkbPolygon, options=['ENCODING=UTF8'])

# Add the field for longitude label
outLayer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))

# get the output layer's feature definition
outLayerDefn = outLayer.GetLayerDefn()

#create polygon
poly = ogr.Geometry(ogr.wkbPolygon)
ring = ogr.Geometry(ogr.wkbLinearRing)

lat = -90
lon = -180
ring.AddPoint(lon, lat)
while lon < 180 - density:
    lon = lon + density
    ring.AddPoint(lon, lat)
lon = 180
ring.AddPoint(lon, lat)

lon = 180
lat = -90
while lat < 90 - density:
    lat = lat + density
    ring.AddPoint(lon, lat)
lat = 90
ring.AddPoint(lon, lat)

lat = 90
lon = 180
while lon > -180 + density:
    lon = lon - density
    ring.AddPoint(lon, lat)
lon = -180
ring.AddPoint(lon, lat)

lon = -180
lat = 90
while lat > -90 + density:
    lat = lat - density
    ring.AddPoint(lon, lat)
lat = -90
ring.AddPoint(lon, lat)
poly.AddGeometry(ring)

# create a new feature
outFeature = ogr.Feature(outLayerDefn)
# set the geometry and attribute
outFeature.SetGeometry(poly)
outFeature.SetField('id', 1)
# add the feature to the shapefile
outLayer.CreateFeature(outFeature)
# destroy the features and get the next input feature
outFeature.Destroy()

# close the shapefile
outDataSet.Destroy() 

