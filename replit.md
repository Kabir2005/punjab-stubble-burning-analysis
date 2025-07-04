# Punjab Stubble Burning Analysis

## Overview

This project is an interactive Streamlit web application for visualizing and analyzing stubble burning fire events across Punjab districts in India. The application provides geographic visualization, temporal analysis, and statistical insights into fire event patterns using satellite-detected data.

## System Architecture

The application follows a modular architecture with separate concerns for data processing, map handling, and visualization. It uses Streamlit as the web framework with Folium for interactive mapping and Plotly for data visualization.

### Frontend Architecture
- **Framework**: Streamlit web application
- **Interactive Components**: Folium maps with district selection, sidebar controls, and filters
- **Visualization**: Plotly charts for trends and statistical analysis
- **Layout**: Wide layout with sidebar for controls and main area for map and charts

### Backend Architecture
- **Data Processing**: Pandas for CSV processing, GeoPandas for spatial data
- **Geospatial Analysis**: Point-in-polygon algorithms for district assignment
- **File Handling**: JSON for GeoJSON boundaries, CSV for fire event data

## Key Components

### 1. Main Application (`app.py`)
- Entry point for the Streamlit application
- Handles page configuration and custom CSS styling
- Orchestrates the interaction between data processing, mapping, and visualization modules

### 2. Data Processor (`data_processor.py`)
- **Purpose**: Centralizes data loading and preprocessing operations
- **GeoJSON Processing**: Loads Punjab district boundaries and creates district lookup dictionary
- **Fire Event Processing**: Loads CSV data, handles missing values, and converts date formats
- **Data Validation**: Includes error handling for file loading operations

### 3. Map Handler (`map_handler.py`)
- **Purpose**: Creates and manages interactive Folium maps
- **Geospatial Functions**: Implements point-in-polygon algorithm for district assignment
- **Map Creation**: Generates base map centered on Punjab with appropriate zoom levels
- **Interactive Features**: Supports district selection and fire event marker clustering

### 4. Visualization (`visualization.py`)
- **Purpose**: Creates statistical charts and graphs using Plotly
- **Chart Types**: Yearly trends, monthly patterns, seasonal analysis
- **Styling**: Consistent color schemes and responsive design
- **Data Handling**: Includes empty state handling for filtered datasets

## Data Flow

1. **Data Loading**: Application loads GeoJSON district boundaries and CSV fire event data
2. **Preprocessing**: Date conversion, missing value handling, and district mapping
3. **User Interaction**: District selection through map clicks or sidebar controls
4. **Filtering**: Year-based filtering applied to fire event dataset
5. **Spatial Analysis**: Point-in-polygon calculations to assign events to districts
6. **Visualization**: Real-time chart updates based on selected district and filters
7. **Statistics**: Automatic calculation and display of district-level metrics

## External Dependencies

### Python Packages
- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **geopandas**: Geospatial data processing
- **folium**: Interactive mapping
- **streamlit-folium**: Streamlit-Folium integration
- **plotly**: Interactive data visualization
- **branca**: Color mapping utilities

### Data Sources
- **Punjab District Boundaries**: GeoJSON format with district polygons
- **Fire Events Dataset**: CSV format with coordinates, dates, and district information
- **Satellite Data**: Fire detection events from satellite imagery (2020-2025)

## Deployment Strategy

### Local Development
- Standard Python environment with pip package installation
- Streamlit development server for local testing
- File-based data storage (GeoJSON and CSV files)

### Production Considerations
- Streamlit Cloud or similar platform deployment
- Static file serving for GeoJSON and CSV data
- Performance optimization for large datasets
- Responsive design for various screen sizes

### Scalability
- Modular architecture supports easy extension
- Separate data processing allows for database integration
- Visualization components can be reused for other regions

## Changelog

- July 04, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.