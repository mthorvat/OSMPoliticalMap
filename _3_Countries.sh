#!/bin/bash

#TODO: clean unnecessary files

cd ./PK

echo "--------------------------------------------------------------------------------------------------------"
echo "Creating countries ..."
echo "RESULTING FILE FOR COUNTRIES POLYGONS: 03_countries/countries_final.shp"
echo "RESULTING FILE FOR ADMIN BOUNDARIES LINES: 03_countries/admin_final.shp"
echo "WARNING: At one point script will pause and expect user input!!!"
echo "--------------------------------------------------------------------------------------------------------"
echo "This part of script filters relation objects from osm file tagged with boundary=administrative and
admin_level=2 and tagged with ISO3166-1:alpha2 country code matching
ISO3166-1 list published at https://raw.githubusercontent.com/datasets/country-list/master/data.csv

Hopefully, this will extract all objects needed to proceed with creation of clean country polygons

Filtering countries from OSM planet file..."

python ../_3_1_filter_countries.py >filter_countries.sh
chmod +x filter_countries.sh
./filter_countries.sh
rm filter_countries.sh

#TODO: check config osmconf.ini to include tags: name,name:en,name:hr,ISO3166-1:alpha2
echo "Converting countries to shapefile..."
ogr2ogr -f "ESRI Shapefile" -where "('ISO3166-1:alpha2'!='' OR 'ISO3166-1'!='') AND admin_level='2'" -overwrite -skipfailures -nlt MULTIPOLYGON -lco ENCODING=UTF-8 03_countries osm_countries.osm

echo "Cleaning unnecessary files: OGR shapefiles ..."
rm 03_countries/lines.* -f
rm 03_countries/multilinestrings.* -f
rm 03_countries/points.* -f
rm 03_countries/other_relations.* -f
  
echo "Dealing with exceptions, e.g. admin_level!=2 or boundary!=administrative as for territories etc."
python ../_3_2_filter_missing_iso.py 03_countries/multipolygons.shp >missing_iso.sh
chmod +x missing_iso.sh
./missing_iso.sh
rm missing_iso.sh

echo "Merging shapefiles from first and second step ..."
ogr2ogr -f "ESRI Shapefile" -update -append 03_countries/multipolygons.shp 03_countries_ex/multipolygons.shp
ogr2ogr -f "ESRI Shapefile" -lco ENCODING=UTF-8 03_countries/countries_polygons.shp 03_countries/multipolygons.shp

echo "Cleaning unnecessary files: OGR shapefiles, bash script ..."
rm 03_countries_ex/lines.* -f
rm 03_countries_ex/multilinestrings.* -f
rm 03_countries_ex/points.* -f
rm 03_countries_ex/other_relations.* -f
rm 03_countries/multipolygons.* -f
rm 03_countries_ex -rf

echo "Finding ISO codes still missing from shapefile and writing them to COUNTRY_ERRORS.log..."
python ../_3_3_list_missing_iso.py 03_countries/countries_polygons.shp >../COUNTRY_ERRORS.log

#TODO: give command line argument to enable skipping this part and performing automatic execution
echo "COUNTRY_ERRORS.log contains ISO codes which are not in final country boundaries.
Check the shapefile ./03_countries/countries_polygons.shp for any other country not shown properly.
Enter ISO Alpha2 codes of those countries not listed in COUNTRY_ERRORS.log one at each line.
When finished press Ctrl+D."

while read line
do
echo $line >>../COUNTRY_ERRORS.log
done

echo "Filtering ISO codes from COUNTRY_ERRORS.log ..."
python ../_3_4_osmtogeojson_for_exceptions.py ../COUNTRY_ERRORS.log >country_exceptions.sh
chmod +x country_exceptions.sh
./country_exceptions.sh

echo "Using osmtogeojson as more robust tool to deal with complicated country polygons ..."
node --max_old_space_size=18000 `which osmtogeojson` osm_countries_add.osm >osm_countries_add.geojson
ogr2ogr -f "ESRI Shapefile" -where "'ISO3166-1'!='' OR 'ISO3166-1:alpha2'!=''" -overwrite -skipfailures -nlt MULTIPOLYGON -lco ENCODING=UTF-8 03_countries_add osm_countries_add.geojson

echo "Cleaning countries shapefiles to avoid duplicates and filling ISO3166-1 attributes ..."
python ../_3_5_clean_countries.py ../COUNTRY_ERRORS.log 03_countries/countries_polygons.shp 03_countries_add/OGRGeoJSON.shp

echo "Merging countries polygons into one file ..."
ogr2ogr -f "ESRI Shapefile" -update -append 03_countries/countries_polygons.shp 03_countries_add/OGRGeoJSON.shp

echo "Extending Antarctica to South pole ..."
python ../_2_2_antarctica.py 03_countries/countries_polygons.shp

echo "Cleaning unnecessary files: OGR shapefiles, filtered data in osm ..."
rm 03_countries_add -rf
rm osm_countries_add.osm -f
rm country_exceptions.sh -f
rm osm_countries_add.geojson

echo "Reprojecting countries to Winkel Tripel projection..."
python ../reproject_to_winkel.py 03_countries/countries_polygons.shp 03_countries/countries_winkel.shp

echo "Clipping countries polygons to coastlines polygons..."
../grass_fake_winkel_location.sh
echo "v.in.ogr -o dsn=./02_coastlines/coastlines_clip.shp output=coastlines_clip min_area=0.0001 snap=1e-6 --overwrite
v.in.ogr -o dsn=./03_countries/countries_winkel.shp output=countries_winkel min_area=0.0001 snap=1e-6 --overwrite
v.overlay ainput=countries_winkel atype=area alayer=1 binput=coastlines_clip btype=area blayer=1 output=countries_clip operator=and olayer=0,1,0 snap=1e-8 --overwrite
v.out.ogr -c input=countries_clip type=area dsn=./03_countries/clip layer=1 format=ESRI_Shapefile lco=ENCODING=UTF-8" >grass_countries.sh
chmod u+x grass_countries.sh
export GRASS_BATCH_JOB=./grass_countries.sh
grass -text $PWD/grassdata/winkel/data
unset GRASS_BATCH_JOB

echo "Cleaning unnecessary files: GRASS location, temporary scripts ..."
rm grassdata -rf
rm grass_countries.sh -f

echo "Cleaning administrative boundaries on Antarctica ..."
python ../_3_6_clean_antarctica.py 03_countries/clip/countries_clip.shp

echo "Creating multipolygons from all parts of countries ..."
python ../_3_7_dissolve_countries_by_iso.py 03_countries/clip/countries_clip.shp 03_countries/countries_multipart.shp

echo "Cleaning small islands and enlarging small countries ..."
python ../_3_8_clean_and_enlarge_countries.py 30000000 1 03_countries/countries_multipart.shp 03_countries/countries_clean.shp

echo "Performing final generalisation of countries ..."
python ../generalize.py 30000000 0 03_countries/countries_clean.shp 03_countries/countries_final.shp

echo "Creating additional coastlines for some island countries ..."
python ../_3_9_extra_coastlines.py 02_coastlines/coastlines_final.shp 03_countries/countries_final.shp 02_coastlines/extra_coastlines.shp

echo "Merging extra coastlines into final coastlines file ..."
ogr2ogr -f "ESRI Shapefile" -update -append 02_coastlines/coastlines_final.shp 02_coastlines/extra_coastlines.shp


echo "Creating administrative boundaries ..."
../grass_fake_winkel_location.sh
echo "v.in.ogr -o --overwrite dsn=./03_countries/countries_winkel.shp output=countries_winkel snap=1e-8
v.type --overwrite input=countries_winkel output=countries_lines type=boundary,line
v.in.ogr -o --overwrite dsn=./02_coastlines/coastlines_winkel.shp output=coastlines_winkel snap=1e-8
v.overlay -t ainput=countries_lines atype=line binput=coastlines_winkel output=admin_clip operator=and
v.out.ogr input=admin_clip dsn=./03_countries olayer=admin_clip" >grass_admin.sh
chmod u+x grass_admin.sh
export GRASS_BATCH_JOB=./grass_admin.sh
grass -text $PWD/grassdata/winkel/data
unset GRASS_BATCH_JOB

echo "Performing generalisation of administrative boundaries ..."
python ../generalize.py 30000000 0 03_countries/admin_clip.shp 03_countries/admin_final.shp

echo "Cleaning administrative boundaries on Antarctica ..."
python ../_3_6_clean_antarctica.py 03_countries/admin_final.shp

echo "Cleaning unnecessary files, GRASS location files and temporary scripts ..."
rm grassdata -rf
rm grass_admin.sh -f
rm 02_coastlines/coastlines_simplified.* -f
rm 02_coastlines/coastlines_clip.* -f
rm 02_coastlines/extra_coastlines.* -f
rm 02_coastlines/coastlines_winkel.* -f
rm 03_countries/admin_clip.* -f
rm 03_countries/clip -rf
rm 03_countries/countries_clean.* -f
rm 03_countries/countries_multipart.* -f
rm 03_countries/countries_winkel.* -f
rm 03_countries/countries_polygons.* -f

echo "Setting attribute fields ..."
python ../set_fields.py osm_id,name,name_en,name_hr,cat,ISO3166_1,admin_leve labels=yes 03_countries/countries_final.shp


echo "Countries ... Done!"
echo "--------------------------------------------------------------------------------------------------------"
