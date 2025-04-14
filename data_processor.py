import pandas as pd
import geopandas as gpd
import json
from datetime import datetime
import os

def load_geojson(file_path):
    """
    Load and process GeoJSON data for Punjab districts
    
    Args:
        file_path (str): Path to the GeoJSON file
        
    Returns:
        dict: Processed GeoJSON data
    """
    try:
        with open(file_path, 'r') as f:
            geojson_data = json.load(f)
        
        # Create a dictionary to store district information
        districts = {}
        for feature in geojson_data['features']:
            district_name = feature['properties']['district']
            districts[district_name] = feature
            
        return geojson_data, districts
    except Exception as e:
        print(f"Error loading GeoJSON: {e}")
        return None, {}

def load_fire_events(file_path):
    """
    Load and process fire event data from CSV
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Processed fire event data
    """
    try:
        # Load CSV data
        df = pd.read_csv(file_path)
        
        # Handle missing values
        df['district'].fillna('Unknown', inplace=True)
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Drop rows with invalid dates
        df = df.dropna(subset=['date'])
        
        # Extract year and month for filtering
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['month_name'] = df['date'].dt.strftime('%b')
        
        # Filter out rows with missing lat or long
        df = df.dropna(subset=['lat', 'long'])
        
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return pd.DataFrame()

def filter_data(df, selected_districts=None, selected_years=None):
    """
    Filter the data based on selected districts and years
    
    Args:
        df (pd.DataFrame): Fire event data
        selected_districts (list): List of selected district names
        selected_years (list): List of selected years
        
    Returns:
        pd.DataFrame: Filtered data
    """
    filtered_df = df.copy()
    
    # Filter by district if selected
    if selected_districts and len(selected_districts) > 0:
        filtered_df = filtered_df[filtered_df['district'].isin(selected_districts)]
    
    # Filter by year if selected
    if selected_years and len(selected_years) > 0:
        filtered_df = filtered_df[filtered_df['year'].isin(selected_years)]
    
    return filtered_df

def get_district_list(df):
    """
    Get a sorted list of all districts in the dataset
    
    Args:
        df (pd.DataFrame): Fire event data
        
    Returns:
        list: Sorted list of district names
    """
    districts = sorted(df['district'].unique().tolist())
    # Remove 'Unknown' from the list and add it at the end if it exists
    if 'Unknown' in districts:
        districts.remove('Unknown')
        districts.append('Unknown')
    return districts

def get_year_list(df):
    """
    Get a sorted list of all years in the dataset
    
    Args:
        df (pd.DataFrame): Fire event data
        
    Returns:
        list: Sorted list of years
    """
    return sorted(df['year'].unique().tolist())

def get_monthly_data(df):
    """
    Aggregate data by month for bar chart
    
    Args:
        df (pd.DataFrame): Fire event data
        
    Returns:
        pd.DataFrame: Monthly aggregated data
    """
    monthly_data = df.groupby(['month', 'month_name']).size().reset_index(name='count')
    monthly_data = monthly_data.sort_values('month')
    return monthly_data

def get_yearly_data(df):
    """
    Aggregate data by year for line chart
    
    Args:
        df (pd.DataFrame): Fire event data
        
    Returns:
        pd.DataFrame: Yearly aggregated data
    """
    yearly_data = df.groupby('year').size().reset_index(name='count')
    yearly_data = yearly_data.sort_values('year')
    return yearly_data

def get_stats(df, district=None):
    """
    Get statistics for the given district or whole state
    
    Args:
        df (pd.DataFrame): Fire event data
        district (str, optional): District name
        
    Returns:
        dict: Statistics
    """
    filtered_df = df
    if district:
        filtered_df = df[df['district'] == district]
    
    total_events = len(filtered_df)
    yearly_counts = filtered_df.groupby('year').size().to_dict()
    monthly_counts = filtered_df.groupby(['month', 'month_name']).size().reset_index(name='count')
    
    # Find peak month and year
    if not monthly_counts.empty:
        peak_month_idx = monthly_counts['count'].idxmax()
        peak_month = monthly_counts.loc[peak_month_idx, 'month_name']
    else:
        peak_month = "N/A"
    
    if yearly_counts:
        peak_year = max(yearly_counts.items(), key=lambda x: x[1])[0]
    else:
        peak_year = "N/A"
    
    return {
        'total_events': total_events,
        'yearly_counts': yearly_counts,
        'monthly_counts': monthly_counts,
        'peak_month': peak_month,
        'peak_year': peak_year
    }
