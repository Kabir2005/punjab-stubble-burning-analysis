# Punjab Stubble Burning Analysis

An interactive Streamlit web application for visualizing and analyzing stubble burning fire events across Punjab districts in India.

## Features

- **Interactive Map**: Visual representation of Punjab districts with fire event markers
- **District Selection**: Click district buttons to analyze specific areas
- **Time Filtering**: Filter data by years (2020-2025)
- **Statistical Analysis**: View trends, monthly patterns, and district-level statistics
- **Data Visualization**: Charts showing yearly trends, monthly distribution, and seasonal patterns

## Data Sources

- **Punjab District Boundaries**: GeoJSON data for district boundaries
- **Fire Events**: CSV data containing satellite-detected fire events with coordinates and dates

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/punjab-stubble-burning-analysis.git
cd punjab-stubble-burning-analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. **District Selection**: Use the district buttons below the map or the dropdown in the sidebar
2. **Year Filtering**: Select specific years using the year selection dropdown
3. **View Statistics**: District-specific statistics appear automatically in the sidebar
4. **Analyze Trends**: Review charts showing temporal patterns and distributions

## Project Structure

```
├── app.py                 # Main Streamlit application
├── data_processor.py      # Data loading and processing utilities
├── map_handler.py         # Map creation and visualization functions
├── visualization.py       # Chart and graph creation functions
├── attached_assets/
│   ├── punjab.geojson    # Punjab district boundaries
│   └── stubble_with_district_full_final.csv  # Fire events data
└── README.md
```

## Technologies Used

- **Streamlit**: Web application framework
- **Folium**: Interactive map creation
- **Plotly**: Data visualization and charts
- **Pandas**: Data manipulation and analysis
- **GeoPandas**: Geospatial data processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## Data Attribution

Fire event data is derived from satellite imagery and processed for agricultural analysis purposes.