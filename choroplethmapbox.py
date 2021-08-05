import shapefile
import pyproj
import plotly.graph_objs as go
import json
import os
import numpy as np
from shapely.geometry.polygon import Polygon
import shapely.ops as ops
from functools import partial


def get_area_in_km2_for_stat_zones() -> dict:
    """
    Get areas of statistical zones in km^2
    :return: dictionary with statistical zones codes as keys and area in km^2 as values
    """
    import warnings
    warnings.filterwarnings("ignore")

    shp_path = 'StatZones/Stat_Zones.shp'
    stat_zones_names_dict = {
        611: "הדר מערב - רח' אלמותנבי",
        612: 'גן הבהאים',
        613: "הדר מערב - רח' מסדה",
        621: 'הדר עליון -בי"ח בני ציון',
        622: "הדר עליון - רח' הפועל",
        623: "רמת הדר - רח' המיימוני",
        631: 'הדר מרכז - התיאטרון העירוני',
        632: "הדר מרכז - רח' הרצליה",
        633: 'הדר מרכז - בית העירייה',
        634: 'הדר מרכז - שוק תלפיות',
        641: 'הדר מזרח - רח\' יל"ג',
        642: 'הדר מזרח - גאולה',
        643: "רמת ויז'ניץ",
        644: 'מעונות גאולה'
    }
    geo_json_dict = shape_file_to_featurecollection(shp_path, stat_zones_names_dict)

    areas = dict()
    for feature in geo_json_dict['features']:
        zone_code = feature['properties']['stat_zone_code']
        poly = Polygon(feature['geometry']['coordinates'][0])

        geom_area = ops.transform(
            partial(
                pyproj.transform,
                pyproj.Proj(init='EPSG:4326'),
                pyproj.Proj(
                    proj='aea',
                    lat_1=poly.bounds[1],
                    lat_2=poly.bounds[3]
                )
            ),
            poly)
        areas[zone_code] = geom_area.area * 1e-6  # from m^2 to km^2
    return areas


def shape_file_to_featurecollection(shp_path, stat_zones_names, save_geojson_to_file=False) -> dict:
    """
        Parse shp file to dictionary (geojson like)
    """
    # Read shape file
    shape = shapefile.Reader(shp_path)
    # Parse shape file
    stat_zones_polygons = {r.record[1]: r.shape for r in shape.shapeRecords()}  # {stat_zone_code : shape}

    # project Israel TM Grid to wgs84
    proj = pyproj.Proj(
        "+proj=tmerc +lat_0=31.7343936111111 +lon_0=35.2045169444445 +k=1.0000067 +x_0=219529.584 +y_0=626907.39 +ellps=GRS80 +towgs84=-24.002400,-17.103200,-17.844400,-0.33077,-1.852690,1.669690,5.424800 +units=m +no_defs")

    stat_zones_polygons = {stat_zone_code: [list(proj(x, y, inverse=True)) for (x, y) in polygon.points]
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


def get_choroplethmap_fig(values_dict: dict, map_title: str,
                          stat_zones_names_dict: dict = {
                              611: "הדר מערב - רח' אלמותנבי",
                              612: 'גן הבהאים',
                              613: "הדר מערב - רח' מסדה",
                              621: 'הדר עליון -בי"ח בני ציון',
                              622: "הדר עליון - רח' הפועל",
                              623: "רמת הדר - רח' המיימוני",
                              631: 'הדר מרכז - התיאטרון העירוני',
                              632: "הדר מרכז - רח' הרצליה",
                              633: 'הדר מרכז - בית העירייה',
                              634: 'הדר מרכז - שוק תלפיות',
                              641: 'הדר מזרח - רח\' יל"ג',
                              642: 'הדר מזרח - גאולה',
                              643: "רמת ויז'ניץ",
                              644: 'מעונות גאולה'
                          },
                          shp_path: str = os.path.join("StatZones", "Stat_Zones.shp"),
                          is_safety_map: bool = False,
                          colorscale=None,
                          hovertemplate=None,
                          add_stat_numbers_to_map: bool = True,
                          scores_dicts=None,
                          changes_map=True):
    """
    Creates and returns a plotly pig of Choroplethmapbox (map)
    Hadar StatZones polygons are used for the heatmap

    :param colorscale: wanted color scale
    :param hovertemplate: hovertemplate for text of hover
    :param add_stat_numbers_to_map: whether to
    :param values_dict: The heatmap values (can be any values)
    :type values_dict: dict
    :param map_title: The title of the map
    :type map_title: str
    :param stat_zones_names_dict: dictionary like {612: 'גן הבהאים' ...}
    :type stat_zones_names_dict: dict
    :param shp_path: path to shap file with polygons for Hadar statistical zones
    :type shp_path: str
    :param is_safety_map: True if this is the
    :type is_safety_map: bool
    :param scores_dicts: list of two dictionaries with the safety scores
    :param changes_map: bool - if True the map shows the percentage of change
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
    text = [f"{feat['properties']['stat_zone_code']} - {feat['properties']['stat_zone_name'][::-1]}"
            for feat in geo_json_dict['features']]
    # Define the heatmap values
    z = list(values_dict.values())

    if changes_map:
        if not is_safety_map:
            max_abs_val = max(abs(max(z)), abs(min(z)))
            z.append(- max_abs_val)
            z.append(max_abs_val)
        else:
            z.append(0)
            z.append(100)
            colorscale = [[0, 'red'], [0.5, 'white'], [1, 'green']]  # 'greens'  # 'reds_r'

        chosen_color_scale = colorscale if colorscale is not None else (
            [[0, 'red'], [0.5, 'white'], [1, 'green']])  # colorscale for safety tab
    else:
        chosen_color_scale = 'tealgrn'

    # my mapbox_access_token must be used only for special mapbox style
    mapboxt = open(".mapbox_token").read()

    if is_safety_map:
        prev_scores, cur_scores = scores_dicts[0], scores_dicts[1]

        up = "+"
        customdata = []
        for old, new in zip(prev_scores.values(), cur_scores.values()):
            val = int(100 * (new - old) / old)
            if val == 0:
                customdata.append('  (0% change)')
            else:
                customdata.append(f'  ({up}{val}% change)' if val > 0 else f'  ({val}% change)')
        hovertemplate = '<b>StatZone</b>: %{text}' + '<br>🛡️<b>Safety Score</b>🛡️: <b>%{z}</b>%{customdata}'
    else:
        if changes_map:
            customdata = [str(val) if val < 0 else (f'+{val}' if val > 0 else f'{val}') for val in z]
        else:
            customdata = [str(val) if val < 0 else (f'{val}' if val > 0 else f'{val}') for val in z]
    fig = go.Figure(go.Choroplethmapbox(z=z,
                                        below=True,
                                        locations=locations,
                                        colorscale=chosen_color_scale,
                                        colorbar=dict(thickness=20, ticklen=3),
                                        geojson=geo_json_dict,
                                        marker=dict(opacity=0.7),
                                        text=text,
                                        hoverinfo='all',
                                        name='',
                                        customdata=customdata,
                                        hovertemplate=
                                        '<b>StatZone</b>: %{text}' + '<br><b>Value</b>: %{customdata}<br>' \
                                            if hovertemplate is None else hovertemplate
                                        )
                    )

    # Add statistical zones numbers to map
    fig.add_trace(go.Scattermapbox(
        mode="text",
        textfont=dict(size=10, color='black'),
        text=list(stat_zones_names_dict.keys()) if add_stat_numbers_to_map else [''] * len(stat_zones_names_dict),
        lat=[Polygon(feature['geometry']['coordinates'][0]).centroid.y
             for feature in geo_json_dict['features']],
        lon=[Polygon(feature['geometry']['coordinates'][0]).centroid.x
             for feature in geo_json_dict['features']],
        name='', hoverinfo='skip'
    ))
    fig.update_layout(title_text=map_title,
                      title_x=0.5,
                      mapbox=dict(center=dict(lat=32.8065, lon=34.993),
                                  accesstoken=mapboxt,
                                  style='light',
                                  zoom=13 if not is_safety_map else 13.1
                                  )
                      )

    return fig


def get_main_tab_map(show_text: bool):
    """
    Creates a map for the main dashboard tab with polygons showing the statistical zones

    :param show_text: boolean, if True shows the statistical zones codes.
                               if False no text is printed on the map
    :return: figure with the map
    """
    shp_path = 'StatZones/Stat_Zones.shp'
    stat_zones_names_dict = {
        611: "הדר מערב - רח' אלמותנבי",
        612: 'גן הבהאים',
        613: "הדר מערב - רח' מסדה",
        621: 'הדר עליון -בי"ח בני ציון',
        622: "הדר עליון - רח' הפועל",
        623: "רמת הדר - רח' המיימוני",
        631: 'הדר מרכז - התיאטרון העירוני',
        632: "הדר מרכז - רח' הרצליה",
        633: 'הדר מרכז - בית העירייה',
        634: 'הדר מרכז - שוק תלפיות',
        641: 'הדר מזרח - רח\' יל"ג',
        642: 'הדר מזרח - גאולה',
        643: "רמת ויז'ניץ",
        644: 'מעונות גאולה'
    }
    geo_json_dict = shape_file_to_featurecollection(shp_path, stat_zones_names_dict)

    fig = go.Figure(go.Scattermapbox(
        mode="text",
        textfont=dict(size=10, color='black'),
        text=list(stat_zones_names_dict.keys()) if show_text else [''] * len(stat_zones_names_dict),
        lat=[Polygon(feature['geometry']['coordinates'][0]).centroid.y
             for feature in geo_json_dict['features']],
        lon=[Polygon(feature['geometry']['coordinates'][0]).centroid.x
             for feature in geo_json_dict['features']],
        customdata=[f"{feat['properties']['stat_zone_code']} - {feat['properties']['stat_zone_name'][::-1]}"
                    for feat in geo_json_dict['features']],
        name=''
    ))

    fig.update_layout(
        mapbox={
            'accesstoken': open(".mapbox_token").read(),
            'style': "light",
            'center': {'lon': 34.993, 'lat': 32.8065},
            'zoom': 13, 'layers': [{
                'source': {
                    'type': "FeatureCollection",
                    'features': [{
                        'type': "Feature",
                        'geometry': {
                            'type': "MultiPolygon",
                            'coordinates': [feature['geometry']['coordinates'] for feature in
                                            geo_json_dict['features']]
                        }
                    }]
                },
                'type': "line", 'below': "traces", 'color': "#8a9bba", 'line': {'width': 5}}]},
        margin={'l': 0, 'r': 0, 'b': 0, 't': 0})

    fig.data[0].hovertemplate = '<b>StatZone</b>: %{customdata}'

    return fig


if __name__ == "__main__":
    """Test the module"""
    values_dict = dict.fromkeys([611, 612, 613, 621, 622, 623, 631, 632, 633, 634, 641, 642, 643, 644], 0.)
    # Generate random number
    for key in values_dict.keys():
        values_dict[key] = max(0, min(100 * np.random.randn(), 100))

    """Heatmap"""
    fig1 = get_choroplethmap_fig(values_dict=values_dict, map_title="Example Title",
                                 colorscale=[[0, '#561162'], [0.5, 'white'], [1, '#0B3B70']],
                                 hovertemplate='<b>StatZone</b>: %{text}' + '<br><b>Percentage of change</b>: %{customdata}%<br>',
                                 is_safety_map=True,
                                 add_stat_numbers_to_map=True
                                 )
    fig1.show()

    """Main tab statzones map"""
    fig2 = get_main_tab_map(show_text=True)
    fig2.show()
