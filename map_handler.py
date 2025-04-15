import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import branca.colormap as cm
import pandas as pd
import numpy as np

def point_in_polygon(point, polygon):
    """
    Check if a point is inside a polygon using the ray casting algorithm
    
    Args:
        point (tuple): (lon, lat) coordinates
        polygon (list): List of (lon, lat) points forming the polygon
        
    Returns:
        bool: True if point is inside polygon, False otherwise
    """
    x, y = point
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside

def create_base_map():
    """
    Create a base map centered on Punjab with strict boundaries
    
    Returns:
        folium.Map: Base map object
    """
    # Center coordinates for Punjab
    center_lat, center_lon = 31.1471, 75.3412
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=8,
        tiles='CartoDB positron',
        max_bounds=True,  # Limit panning to Punjab area
        min_zoom=7,       # Prevent zooming out too far
        max_zoom=12,      # Prevent zooming in too much
        zoom_control=True,
        scrollWheelZoom=True
    )
    
    # Define Punjab boundary more precisely - strictly limit to Punjab region
    # These coordinates are adjusted to focus only on the Punjab state area
    bounds = [
        [30.4, 73.9],  # Southwest corner (very tight to Punjab borders)
        [32.5, 76.0]   # Northeast corner (very tight to Punjab borders)
    ]
    m.fit_bounds(bounds)
    
    # Set the max bounds to prevent panning outside of Punjab
    options = {
        'maxBounds': bounds,
        'maxBoundsViscosity': 1.0  # Makes the bounds "hard" - can't drag outside
    }
    m.options.update(options)
    
    return m

def add_district_layers(m, geojson_data, districts_dict, selected_districts=None):
    """
    Add district boundaries to the map
    
    Args:
        m (folium.Map): Base map object
        geojson_data (dict): GeoJSON data
        districts_dict (dict): Dictionary of district features
        selected_districts (list): List of selected district names
        
    Returns:
        folium.Map: Map with district layers
    """
    # Function to style the districts
    def style_function(feature):
        district_name = feature['properties']['district']
        
        if selected_districts and district_name in selected_districts:
            return {
                'fillColor': '#FF4B4B',
                'color': '#FF0000',
                'weight': 2,
                'fillOpacity': 0.3
            }
        else:
            return {
                'fillColor': '#AAAAAA',
                'color': '#000000',
                'weight': 1,
                'fillOpacity': 0.1
            }
    
    # Function to highlight districts on hover
    def highlight_function(feature):
        return {
            'fillColor': '#FF4B4B',
            'color': '#FF0000',
            'weight': 3,
            'fillOpacity': 0.5
        }
    
    # Add GeoJSON layer with districts
    district_layer = folium.GeoJson(
        geojson_data,
        name='Districts',
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['district'],
            aliases=['District:'],
            localize=True
        )
    )
    
    district_layer.add_to(m)
    
    return m

def add_fire_markers(m, fire_data):
    """
    Add fire event markers to the map
    
    Args:
        m (folium.Map): Map object
        fire_data (pd.DataFrame): Filtered fire event data
        
    Returns:
        folium.Map: Map with fire markers
    """
    # Create a marker cluster for better performance with many points
    marker_cluster = MarkerCluster(
        name='Fire Events',
        icon_create_function="""
        function(cluster) {
            var count = cluster.getChildCount();
            var size = 35;
            if (count > 100) {
                size = 45;
            } else if (count > 50) {
                size = 40;
            }
            
            return L.divIcon({
                html: '<div style="background-color: rgba(255, 0, 0, 0.7); color: white; border-radius: 50%; width: ' + size + 'px; height: ' + size + 'px; line-height: ' + size + 'px; text-align: center; font-weight: bold;">' + count + '</div>',
                className: 'marker-cluster-custom',
                iconSize: L.point(size, size)
            });
        }
        """
    ).add_to(m)
    
    # Add each fire event as a marker
    for _, row in fire_data.iterrows():
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 180px;">
            <h4 style="margin: 0; color: #d32f2f; border-bottom: 1px solid #eee; padding-bottom: 5px;">Fire Event</h4>
            <p style="margin: 5px 0;"><b>Date:</b> {row['date'].strftime('%Y-%m-%d')}</p>
            <p style="margin: 5px 0;"><b>District:</b> {row['district']}</p>
            <p style="margin: 5px 0;"><b>Location:</b> {row['lat']:.4f}, {row['long']:.4f}</p>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['lat'], row['long']],
            radius=5,
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.7,
            weight=1.5,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(marker_cluster)
    
    return m

def zoom_to_districts(m, geojson_data, selected_districts):
    """
    Zoom the map to fit the selected districts
    
    Args:
        m (folium.Map): Map object
        geojson_data (dict): GeoJSON data
        selected_districts (list): List of selected district names
        
    Returns:
        folium.Map: Map zoomed to selected districts
    """
    if not selected_districts:
        return m
    
    # Get coordinates of all selected districts
    all_coords = []
    for feature in geojson_data['features']:
        district_name = feature['properties']['district']
        if district_name in selected_districts:
            if feature['geometry']['type'] == 'Polygon':
                coords = feature['geometry']['coordinates'][0]
                all_coords.extend(coords)
            elif feature['geometry']['type'] == 'MultiPolygon':
                for polygon in feature['geometry']['coordinates']:
                    all_coords.extend(polygon[0])
    
    if not all_coords:
        return m
    
    # Get bounds
    lats = [coord[1] for coord in all_coords]
    lons = [coord[0] for coord in all_coords]
    
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)
    
    # Add padding
    padding = 0.05
    min_lat -= padding
    max_lat += padding
    min_lon -= padding
    max_lon += padding
    
    # Fit bounds
    m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])
    
    return m

def add_legend(m):
    """
    Add a legend to the map
    
    Args:
        m (folium.Map): Map object
        
    Returns:
        folium.Map: Map with legend
    """
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; 
                border:2px solid grey; z-index:9999; 
                background-color:white;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                ">
      <p><i class="fa fa-circle" style="color:red"></i> Fire Event</p>
      <p><div style="width: 20px; height: 20px; background-color: #FF4B4B; 
                    opacity: 0.3; display: inline-block; vertical-align: middle;
                    border: 1px solid #FF0000;"></div> Selected District</p>
      <p><div style="width: 20px; height: 20px; background-color: #AAAAAA; 
                    opacity: 0.1; display: inline-block; vertical-align: middle;
                    border: 1px solid #000000;"></div> District Boundary</p>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m

def render_map(geojson_data, districts_dict, fire_data, selected_districts=None):
    """
    Render the full map with all components
    
    Args:
        geojson_data (dict): GeoJSON data
        districts_dict (dict): Dictionary of district features
        fire_data (pd.DataFrame): Filtered fire event data
        selected_districts (list): List of selected district names
        
    Returns:
        folium.Map: Complete map
    """
    # Create base map
    m = create_base_map()
    
    # Add district boundaries
    m = add_district_layers(m, geojson_data, districts_dict, selected_districts)
    
    # Add fire markers
    m = add_fire_markers(m, fire_data)
    
    # Zoom to selected districts
    if selected_districts and len(selected_districts) > 0:
        m = zoom_to_districts(m, geojson_data, selected_districts)
    
    # Add legend
    m = add_legend(m)
    
    # Add layer control - position it on the top right to avoid console overlap
    folium.LayerControl(position='topright', collapsed=True).add_to(m)
    
    return m
