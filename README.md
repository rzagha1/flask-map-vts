# flask-map-vts

ogr2ogr -f "geojsonseq" 'uspts.json' PG:"dbname=modiv host=localhost port=5432 user=postgres password=ttt schemas=public" "pts" -progress -overwrite && tippecanoe -zg --projection=EPSG:4326 -o uspts.pmtiles -l uspts uspts.json --force && rm uspts.json
