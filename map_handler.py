import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import branca.colormap as cm
import pandas as pd

def create_base_map():
    """
    Create a base map centered on Punjab
    
    Returns:
        folium.Map: Base map object
    """
    # Center coordinates for Punjab
    center_lat, center_lon = 31.1471, 75.3412
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=8,
        tiles='CartoDB positron'
    )
    
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
    marker_cluster = MarkerCluster(name='Fire Events').add_to(m)
    
    # Add each fire event as a marker
    for _, row in fire_data.iterrows():
        popup_html = f"""
        <b>Date:</b> {row['date'].strftime('%Y-%m-%d')}<br>
        <b>District:</b> {row['district']}<br>
        <b>Location:</b> {row['lat']:.4f}, {row['long']:.4f}
        """
        
        folium.CircleMarker(
            location=[row['lat'], row['long']],
            radius=4,
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.7,
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
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m
