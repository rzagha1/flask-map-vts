drop table if exists us_points;
create table us_points as
SELECT ST_SetSRID(ST_MakePoint(
    random() * (max_lon - min_lon) + min_lon,
    random() * (max_lat - min_lat) + min_lat
), 4326) AS geom
FROM (
    SELECT -125 AS min_lon, -66 AS max_lon, 24 AS min_lat, 49 AS max_lat
) AS bbox
CROSS JOIN generate_series(1, 10000) AS id;
alter table us_points add column id serial primary key;
alter table us_points add column geom_mercator geometry;
ALTER TABLE us_points ALTER COLUMN geom TYPE geometry (Point, 4326);
update us_points set geom_mercator =st_transform(geom,3857);
create index idxgpt on us_points using gist(geom);
create index idxgpt2 on us_points using gist(geom_mercator);
