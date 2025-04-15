import streamlit as st
import pandas as pd
import os
import time
from streamlit_folium import st_folium
import json

# Import custom modules
import data_processor as dp
import map_handler as mh
import visualization as vis

# Set page configuration
st.set_page_config(
    page_title="Punjab Stubble Burning Analysis",
    page_icon="🌾",
    layout="wide"
)

# Add custom CSS to make the map container larger and improve the UI
st.markdown("""
<style>
    /* Hide developer console overlay */
    .stDeployButton, .viewerBadge_container__1QSob, header {
        display: none !important;
    }
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    .stStatusWidget, .stDecoration {
        display: none !important;
    }
    .stWarning {
        display: none !important;
    }
    
    /* Improved styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    .stApp {
        background-color: #f8f9fa;
    }
    
    .stSidebar {
        background-color: #ffffff;
        border-left: 1px solid #e9ecef;
    }
    
    .stButton>button {
        border-radius: 20px;
        font-size: 12px;
        height: 28px;
        padding: 0px 15px;
        margin: 0px 2px;
        background-color: #f1f3f5;
        border: 1px solid #dee2e6;
        color: #495057;
    }
    
    .stButton>button:hover {
        background-color: #e9ecef;
        border-color: #ced4da;
    }
    
    .stButton>button[data-baseweb="button"][kind="primary"] {
        background-color: #8b4513;
        color: white;
    }
    
    .stButton>button[data-baseweb="button"][kind="primary"]:hover {
        background-color: #7d3913;
    }
    
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        gap: 5px !important;
    }
    
    .map-container {
        height: calc(100vh - 80px);
        width: 100%;
        margin-bottom: 20px;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .year-selector {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: #8b4513;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Metrics styling */
    div[data-testid="metric-container"] {
        background-color: #fff;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    div[data-testid="metric-container"] > div:first-child {
        color: #8b4513;
    }
    
    div[data-testid="stHorizontalBlock"] {
        gap: 10px;
    }
    
    /* Chart styling */
    div[data-testid="stPlotlyChart"] {
        background-color: white;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Divider styling */
    hr {
        border-color: #e9ecef;
        margin: 1rem 0;
    }
    
    /* Info box styling */
    div[data-testid="stAlert"] {
        background-color: #f1f8ff;
        border-color: #bee3f8;
        color: #2a4365;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Cache data loading to improve performance
@st.cache_data(ttl=3600)
def load_data():
    """
    Load and cache the GeoJSON and CSV data
    
    Returns:
        tuple: GeoJSON data, districts dictionary, fire events dataframe
    """
    geojson_path = "attached_assets/punjab.geojson"
    csv_path = "attached_assets/stubble_with_district_full_final.csv"
    
    # Load GeoJSON data
    geojson_data, districts_dict = dp.load_geojson(geojson_path)
    
    # Load fire events data
    fire_events_df = dp.load_fire_events(csv_path)
    
    return geojson_data, districts_dict, fire_events_df

# Main function
def main():
    """
    Main application function
    """
    # Initialize session state
    if 'map_clicked' not in st.session_state:
        st.session_state.map_clicked = False
    
    if 'clicked_district' not in st.session_state:
        st.session_state.clicked_district = None
    
    # Load data with loading spinner
    with st.spinner("Loading data..."):
        geojson_data, districts_dict, fire_events_df = load_data()
    
    # If data loading fails, show error
    if geojson_data is None or fire_events_df.empty:
        st.error("Failed to load data. Please check the data files and try again.")
        return
    
    # Get available districts and years
    districts = dp.get_district_list(fire_events_df)
    years = dp.get_year_list(fire_events_df)
    
    # Setup session state for selections
    if 'selected_districts' not in st.session_state:
        st.session_state.selected_districts = []
    
    if 'selected_years' not in st.session_state:
        st.session_state.selected_years = years.copy()
    
    # Define layout - less space for sidebar, more for map
    left_col, right_col = st.columns([7, 3])
    
    # Main content - Map and interactive elements
    with left_col:
        # App title & brief description
        st.title("Punjab Stubble Burning Analysis")
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #8b4513;">
            <p style="margin: 0; color: #495057;">Interactive visualization of stubble burning across Punjab districts. 
            Click on districts or use filters to explore fire events data.</p>
        </div>
        """, unsafe_allow_html=True)

        # Create and display map
        map_obj = mh.render_map(
            geojson_data, 
            districts_dict, 
            fire_events_df.query('year.isin(@st.session_state.selected_years)'),
            st.session_state.selected_districts
        )
        
        # Use st_folium instead of folium_static for improved interaction
        map_data = st_folium(
            map_obj, 
            width="100%",
            height=550,
            returned_objects=["last_active_drawing", "last_clicked"],
            key="folium_map"
        )
        
        # Handle map click events to update selected districts
        if map_data["last_clicked"]:
            if st.session_state.map_clicked is False:
                st.session_state.map_clicked = True
                # Get clicked coordinates
                lat, lng = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
                
                # Find which district was clicked
                clicked_district = None
                for district_name, feature in districts_dict.items():
                    # Skip if not a valid district
                    if district_name == 'Unknown' or not district_name:
                        continue
                        
                    # Check if point is within district boundary
                    coordinates = feature["geometry"]["coordinates"][0]
                    if mh.point_in_polygon((lng, lat), coordinates):
                        clicked_district = district_name
                        break
                
                if clicked_district:
                    st.session_state.clicked_district = clicked_district
                    # Toggle the district selection
                    if clicked_district in st.session_state.selected_districts:
                        st.session_state.selected_districts.remove(clicked_district)
                    else:
                        st.session_state.selected_districts.append(clicked_district)
                    st.rerun()
        else:
            st.session_state.map_clicked = False
        
        # Data summary and district distribution
        st.markdown("### Fire Events by District")
        
        # Apply filters
        filtered_data = dp.filter_data(
            fire_events_df, 
            selected_districts=st.session_state.selected_districts,
            selected_years=st.session_state.selected_years
        )
        
        # District distribution chart
        district_chart = vis.create_district_bar_chart(filtered_data)
        st.plotly_chart(district_chart, use_container_width=True)
    
    # Sidebar content
    with right_col:
        st.markdown("## Filters & Analytics")
        
        # Year selection using a more compact UI
        st.markdown("### Year Selection")
        with st.container():
            year_selection = st.multiselect(
                "Select years to display:",
                options=years,
                default=st.session_state.selected_years,
                key="year_multiselect"
            )
            
            # Update selected years if changed
            if year_selection != st.session_state.selected_years:
                st.session_state.selected_years = year_selection
                st.rerun()
        
        # District selection
        st.markdown("### District Selection")
        selected_districts = st.multiselect(
            "Choose districts to analyze:",
            options=districts,
            default=st.session_state.selected_districts,
            key="district_multiselect"
        )
        
        # Update selected districts if changed via multiselect
        if selected_districts != st.session_state.selected_districts:
            st.session_state.selected_districts = selected_districts
            st.rerun()
        
        # Display statistics
        st.markdown("---")
        with st.container():
            if st.session_state.selected_districts:
                if len(st.session_state.selected_districts) == 1:
                    title = f"Statistics for {st.session_state.selected_districts[0]}"
                else:
                    title = f"Statistics for Selected Districts ({len(st.session_state.selected_districts)})"
            else:
                title = "Punjab State Statistics"
                
            stats = dp.get_stats(filtered_data)
            vis.render_stats_section(stats, title)
        
        # Visualizations
        st.markdown("---")
        
        # Yearly trend chart
        yearly_data = dp.get_yearly_data(filtered_data)
        yearly_chart = vis.create_yearly_trend_chart(yearly_data)
        st.plotly_chart(yearly_chart, use_container_width=True)
        
        # Monthly distribution chart
        monthly_data = dp.get_monthly_data(filtered_data)
        monthly_chart = vis.create_monthly_bar_chart(monthly_data)
        st.plotly_chart(monthly_chart, use_container_width=True)
        
        # Seasonal pattern chart
        seasonal_chart = vis.create_seasonal_pattern_chart(filtered_data)
        st.plotly_chart(seasonal_chart, use_container_width=True)
        
        # Display data info
        st.markdown("### Data Summary")
        st.info(f"""
        - Total districts: {len(districts)}
        - Fire events: {len(filtered_data)} / {len(fire_events_df)}
        - Time period: {min(years)} - {max(years)}
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray; font-size: 0.8em;">
        Data visualization of stubble burning events in Punjab, India.
    </div>
    """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()
