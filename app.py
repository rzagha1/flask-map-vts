from flask_cors import CORS
import psycopg2
from flask import Flask, jsonify, Response

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

params={ 'dbname':'texas',
        'user':'postgres',
        'password':'vv,
        'host':'vv',
        'port':5432
        }

# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@app.route('/tiles/<int:z>/<int:x>/<int:y>.pbf')
def serve_tile(z, x, y):
    query = f'''
        WITH bounds AS (
          SELECT ST_TileEnvelope({z}, {x}, {y}) AS geom
        ),
        mvtgeom AS (
          SELECT ST_AsMVTGeom(ST_Transform(t.geom, 3857), bounds.geom) AS geom,
            t.name
          FROM data.counties t, bounds
          WHERE ST_Intersects(t.geom, ST_Transform(bounds.geom, 4326))
        )
        SELECT ST_AsMVT(mvtgeom, 'data.counties')
        FROM mvtgeom;
    '''
    mvt_tile=None
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            mvt_tile = cur.fetchone()[0]
    response = Response(response=mvt_tile, status=200, content_type='application/vnd.mapbox-vector-tile')
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Cache-Control'] = 'no-cache'
    return response


@app.route('/layer_geojson', methods=['GET'])
def layer_geojson():
    qry = """
        SELECT row_to_json(fc)
        FROM (
            SELECT 'FeatureCollection' AS TYPE,
                array_to_json(array_agg(f)) AS features
            FROM (
                SELECT 'Feature' AS TYPE,
                    ST_AsGeoJSON(ST_Transform(geom, 4326))::JSON AS geometry,
                    row_to_json(
                        (SELECT p
                         FROM (
                             SELECT name
                             ) AS p
                        )
                    ) AS properties
                FROM data.counties
            ) AS f
        ) AS fc
    """
    mvt_tile=None
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute(qry)
            mvt_tile = cur.fetchone()[0]

    return jsonify(mvt_tile)

if __name__ == '__main__':
    app.run()
