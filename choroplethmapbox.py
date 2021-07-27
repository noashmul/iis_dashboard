import shapefile
import pyproj
import plotly.graph_objs as go
import json
import os


def shape_file_to_featurecollection(shp_path, stat_zones_names, save_geojson_to_file=False) -> dict:
    """
        Parse shp file to dictionary (geojson like)
    """
    # Read shape file
    shape = shapefile.Reader(shp_path)
    # Parse shape file
    stat_zones_polygons = {r.record[1]: r.shape for r in shape.shapeRecords()}  # {stat_zone_code : shape}

    # project Israel TM Grid to wgs84
    proj2 = pyproj.Proj(
        "+proj=tmerc +lat_0=31.7343936111111 +lon_0=35.2045169444445 +k=1.0000067 +x_0=219529.584 +y_0=626907.39 +ellps=GRS80 +towgs84=-24.002400,-17.103200,-17.844400,-0.33077,-1.852690,1.669690,5.424800 +units=m +no_defs")

    stat_zones_polygons = {stat_zone_code: [list(proj2(x, y, inverse=True)) for (x, y) in polygon.points]
                           for stat_zone_code, polygon in stat_zones_polygons.items()}

    buffer = []
    for stat_zone_code, poly in stat_zones_polygons.items():
        atr = dict(stat_zone_code=stat_zone_code, stat_zone_name=stat_zones_names[stat_zone_code])
        geom = dict(type='Polygon', coordinates=[poly])
        buffer.append(dict(type="Feature", id=stat_zone_code, properties=atr, geometry=geom))

    geo_json_dict = {"type": "FeatureCollection", "features": buffer}

    if save_geojson_to_file:
        # Save locally so we can open with https://kepler.gl or similar
        geo_json = open("hadar.json", "w")
        geo_json.write(json.dumps(geo_json_dict, indent=2) + "\n")
        geo_json.close()

    return geo_json_dict


def get_choroplethmap_fig(stat_zones_names_dict: dict, values_dict: dict, map_title: str,
                          shp_path: str = os.path.join("StatZones", "Stat_Zones.shp")):
    """
    Creates and returns a plotly pig of Choroplethmapbox (map)
    Hadar StatZones polygons are used for the heatmap

    :param stat_zones_names_dict: dictionary like {612: 'גן הבהאים' ...}
    :type stat_zones_names_dict: dict
    :param values_dict: The heatmap values (can be any values)
    :type values_dict: dict
    :param map_title: The title of the map
    :type map_title: str
    :param shp_path: path to shap file with polygons for Hadar statistical zones
    :type shp_path: str
    :return: plotly fig map
    """
    # Verify stat_zones_names_dict is sorted by key
    stat_zones_names_dict = {int(k): stat_zones_names_dict[k] for k in sorted(stat_zones_names_dict)}
    # Verify values_dict is sorted by key
    values_dict = {int(k): values_dict[k] for k in sorted(values_dict)}

    # Create a dictionary of featurecollection (geojson like)
    geo_json_dict = shape_file_to_featurecollection(shp_path, stat_zones_names_dict)

    # Define inputs for Choroplethmapbox
    locations = list(stat_zones_names_dict.keys())
    text = [f"{feat['properties']['stat_zone_code']} - {feat['properties']['stat_zone_name']}"
            for feat in geo_json_dict['features']]
    # Define the heatmap values
    z = list(values_dict.values())
    max_abs_val = max(abs(max(z)), abs(min(z)))
    z.append(- max_abs_val)
    z.append(max_abs_val)

    fig = go.Figure(go.Choroplethmapbox(z=z,
                                        locations=locations,
                                        colorscale=[[0, 'red'], [0.5, 'white'], [1, 'green']],
                                        colorbar=dict(thickness=20, ticklen=3),
                                        geojson=geo_json_dict,
                                        text=text,
                                        hoverinfo='all',
                                        name=''))

    # my mapbox_access_token must be used only for special mapbox style
    mapboxt = open(".mapbox_token").read()

    fig.update_layout(title_text=map_title,
                      title_x=0.5,
                      # TODO possibly change width, height
                      width=700,  # height=700,
                      mapbox=dict(center=dict(lat=32.8065, lon=34.993),
                                  accesstoken=mapboxt,
                                  # TODO choose style from the below:
                                  #  open-street-map, light, carto-positron, white-bg, dark
                                  style='carto-positron',
                                  zoom=13))

    # TODO this is the format of the hover string - possibly change
    fig.data[0].hovertemplate = '<b>StatZone</b>: %{text}' + '<br><b>Value</b>: %{z}<br>'

    return fig


if __name__ == "__main__":
    pass
