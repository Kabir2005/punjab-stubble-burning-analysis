import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
import numpy as np

def create_yearly_trend_chart(yearly_data):
    """
    Create a line chart showing yearly fire event trends
    
    Args:
        yearly_data (pd.DataFrame): Yearly aggregated data
        
    Returns:
        plotly.graph_objects.Figure: Line chart figure
    """
    if yearly_data.empty:
        return create_empty_chart("No data available for selected filters")
    
    # Create a more visually appealing line chart
    fig = px.line(
        yearly_data, 
        x='year', 
        y='count',
        markers=True,
        line_shape='linear',
        labels={'year': 'Year', 'count': 'Number of Fire Events'},
        title='Yearly Fire Event Trends',
        color_discrete_sequence=['#8b4513'],  # Brown color to match theme
    )
    
    # Customize styling
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8, line=dict(width=2, color='#ffffff'))
    )
    
    # Add a subtle area fill
    fig.add_traces(
        go.Scatter(
            x=yearly_data['year'], 
            y=yearly_data['count'],
            mode='none',
            fill='tozeroy',
            fillcolor='rgba(139, 69, 19, 0.1)',
            showlegend=False
        )
    )
    
    # Improve layout
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=yearly_data['year'].tolist(),
            ticktext=[str(int(year)) for year in yearly_data['year'].tolist()],
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            zeroline=False
        ),
        plot_bgcolor='white',
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        title_font=dict(size=16, color='#8b4513'),
        title_x=0.5,
        hovermode='x unified'
    )
    
    return fig

def create_monthly_bar_chart(monthly_data):
    """
    Create a bar chart showing monthly fire event counts
    
    Args:
        monthly_data (pd.DataFrame): Monthly aggregated data
        
    Returns:
        plotly.graph_objects.Figure: Bar chart figure
    """
    if monthly_data.empty:
        return create_empty_chart("No data available for selected filters")
    
    # Create month-name order
    month_order = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    
    # Sort by month number
    monthly_data = monthly_data.sort_values('month')
    
    # Create color gradient - earthy tones for stubble burning theme
    colors = ['#f8d5c0', '#efb28c', '#e49066', '#d97149', '#c94c26', '#a63b1f', '#8b4513']
    
    # Calculate color based on relative count
    max_count = monthly_data['count'].max()
    monthly_data['color_idx'] = monthly_data['count'].apply(
        lambda x: min(int(6 * x / max_count) if max_count > 0 else 0, 6)
    )
    monthly_data['color'] = monthly_data['color_idx'].apply(lambda x: colors[x])
    
    # Create bar chart with custom colors
    fig = go.Figure()
    
    # Add bars with custom styling
    fig.add_trace(go.Bar(
        x=monthly_data['month_name'],
        y=monthly_data['count'],
        marker_color=monthly_data['color'],
        text=monthly_data['count'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Fire Events: %{y}<extra></extra>'
    ))
    
    # Custom x-axis order based on month
    month_names = [month_order.get(m, 'Unknown') for m in range(1, 13)]
    present_months = monthly_data['month_name'].unique()
    ordered_months = [m for m in month_names if m in present_months]
    
    # Enhanced styling
    fig.update_layout(
        title={
            'text': 'Monthly Fire Event Distribution',
            'font': {'size': 16, 'color': '#8b4513'},
            'x': 0.5
        },
        xaxis={
            'categoryorder': 'array', 
            'categoryarray': ordered_months,
            'title': 'Month',
            'showgrid': False,
            'tickangle': 0
        },
        yaxis={
            'title': 'Number of Fire Events',
            'showgrid': True,
            'gridcolor': 'rgba(0,0,0,0.05)',
            'zeroline': False
        },
        plot_bgcolor='white',
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode='x unified'
    )
    
    return fig

def create_district_bar_chart(df):
    """
    Create a bar chart showing fire events by district
    
    Args:
        df (pd.DataFrame): Fire event data
        
    Returns:
        plotly.graph_objects.Figure: Bar chart figure
    """
    if df.empty:
        return create_empty_chart("No data available for selected filters")
    
    district_counts = df.groupby('district').size().reset_index(name='count')
    district_counts = district_counts.sort_values('count', ascending=False)
    
    fig = px.bar(
        district_counts, 
        x='district', 
        y='count',
        labels={'district': 'District', 'count': 'Number of Fire Events'},
        title='Fire Events by District',
        color='count',
        color_continuous_scale=px.colors.sequential.Reds
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400,
        margin=dict(l=20, r=20, t=50, b=100)
    )
    
    return fig

def create_empty_chart(message="No data available"):
    """
    Create an empty chart with a message
    
    Args:
        message (str): Message to display
        
    Returns:
        plotly.graph_objects.Figure: Empty figure with message
    """
    fig = go.Figure()
    
    fig.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 18
                }
            }
        ],
        height=300
    )
    
    return fig

def render_stats_section(stats, title):
    """
    Render the statistics section in the sidebar
    
    Args:
        stats (dict): Statistics dictionary
        title (str): Title for the section
    """
    st.subheader(title)
    
    st.metric("Total Fire Events", stats['total_events'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Peak Year", stats['peak_year'])
    with col2:
        st.metric("Peak Month", stats['peak_month'])

def create_seasonal_pattern_chart(df):
    """
    Create a heatmap showing seasonal patterns by month and year
    
    Args:
        df (pd.DataFrame): Fire event data
        
    Returns:
        plotly.graph_objects.Figure: Heatmap figure
    """
    if df.empty:
        return create_empty_chart("No data available for selected filters")
    
    # Group by year and month, count occurrences
    year_month_counts = df.groupby(['year', 'month']).size().reset_index(name='count')
    
    # Create a pivot table
    pivot_data = year_month_counts.pivot_table(
        index='month', 
        columns='year', 
        values='count',
        fill_value=0
    )
    
    # Get month names in order
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    
    # Create heatmap
    fig = px.imshow(
        pivot_data,
        labels=dict(x="Year", y="Month", color="Fire Events"),
        x=pivot_data.columns,
        y=[month_names[m] for m in pivot_data.index],
        color_continuous_scale='Reds',
        title='Seasonal Fire Event Patterns'
    )
    
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        coloraxis_colorbar=dict(
            title="Count",
            thicknessmode="pixels", 
            thickness=15,
            lenmode="pixels", 
            len=300
        )
    )
    
    fig.update_xaxes(
        tickvals=list(pivot_data.columns),
        ticktext=[str(int(year)) for year in pivot_data.columns]
    )
    
    return fig

def render_year_buttons(available_years, selected_years):
    """
    Render year selection buttons
    
    Args:
        available_years (list): List of available years
        selected_years (list): List of currently selected years
        
    Returns:
        list: Updated list of selected years
    """
    st.write("Select Years:")
    
    # Use columns for buttons
    columns = st.columns(len(available_years))
    new_selected_years = selected_years.copy()
    
    for i, year in enumerate(available_years):
        with columns[i]:
            year_str = str(int(year))
            if st.button(
                year_str,
                key=f"year_btn_{year}",
                help=f"Toggle {year_str}",
                type="primary" if year in selected_years else "secondary"
            ):
                if year in new_selected_years:
                    new_selected_years.remove(year)
                else:
                    new_selected_years.append(year)
    
    return new_selected_years
