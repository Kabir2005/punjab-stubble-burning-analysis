import streamlit as st
import pandas as pd
import os
import time
from streamlit_folium import folium_static

# Import custom modules
import data_processor as dp
import map_handler as mh
import visualization as vis

# Set page configuration
st.set_page_config(
    page_title="Punjab Stubble Burning Analysis",
    page_icon="🔥",
    layout="wide"
)

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
    # Header with image
    st.title("🔥 Punjab Stubble Burning Analysis")
    st.markdown("""
    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
        <img src="https://images.unsplash.com/photo-1577884994417-ef93c99bad67" alt="Stubble Burning" style="max-width: 100%; height: 200px; object-fit: cover; border-radius: 10px;">
    </div>
    """, unsafe_allow_html=True)

    # App description
    st.markdown("""
    This application visualizes stubble burning fire events across Punjab districts from 2020 onwards. 
    Use the map to select districts of interest, and view temporal trends in the sidebar.
    """)
    
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
    
    # Define layout
    col1, col2 = st.columns([2, 1])
    
    # Sidebar content
    with col2:
        st.sidebar.title("Filters & Statistics")
        
        # District selection
        st.sidebar.subheader("Select Districts")
        selected_districts = st.sidebar.multiselect(
            "Choose districts to analyze:",
            options=districts,
            default=[],
            key="district_multiselect"
        )
        st.session_state.selected_districts = selected_districts
        
        # Apply filters
        filtered_data = dp.filter_data(
            fire_events_df, 
            selected_districts=st.session_state.selected_districts,
            selected_years=st.session_state.selected_years
        )
        
        # Display statistics
        with st.sidebar.container():
            if selected_districts:
                title = f"Statistics for {', '.join(selected_districts)}"
            else:
                title = "Punjab State Statistics"
                
            stats = dp.get_stats(filtered_data)
            vis.render_stats_section(stats, title)
        
        # Year selection buttons
        st.sidebar.markdown("---")
        new_selected_years = vis.render_year_buttons(years, st.session_state.selected_years)
        
        # Update selected years if changed
        if new_selected_years != st.session_state.selected_years:
            st.session_state.selected_years = new_selected_years
            st.rerun()
        
        # Visualizations
        st.sidebar.markdown("---")
        
        # Yearly trend chart
        yearly_data = dp.get_yearly_data(filtered_data)
        yearly_chart = vis.create_yearly_trend_chart(yearly_data)
        st.sidebar.plotly_chart(yearly_chart, use_container_width=True)
        
        # Monthly distribution chart
        monthly_data = dp.get_monthly_data(filtered_data)
        monthly_chart = vis.create_monthly_bar_chart(monthly_data)
        st.sidebar.plotly_chart(monthly_chart, use_container_width=True)
    
    # Main content - Map and district chart
    with col1:
        # Instructions
        st.markdown("""
        ### Interactive Map
        - Click on districts to view fire events
        - Select districts in the sidebar for detailed analysis
        - Zoom and pan to explore different areas
        """)
        
        # Create and display map
        map_obj = mh.render_map(
            geojson_data, 
            districts_dict, 
            filtered_data,
            st.session_state.selected_districts
        )
        
        folium_static(map_obj, width=800, height=500)
        
        # District distribution chart
        st.markdown("### District-wise Fire Events")
        district_chart = vis.create_district_bar_chart(filtered_data)
        st.plotly_chart(district_chart, use_container_width=True)
        
        # Display data info
        st.markdown("### Data Summary")
        st.info(f"""
        - Total districts: {len(districts)}
        - Total fire events: {len(fire_events_df)}
        - Time period: {min(years)} - {max(years)}
        - Currently showing: {len(filtered_data)} fire events
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray; font-size: 0.8em;">
        Data visualization of stubble burning events in Punjab, India.
        Images from Unsplash.
    </div>
    """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()
