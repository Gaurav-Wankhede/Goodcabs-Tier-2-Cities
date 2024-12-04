import pandas as pd
import altair as alt
import streamlit as st
from config.__init__ import DataPaths
import math

class CityPerformanceService:
    @staticmethod
    @st.cache_data
    def analyze_city_performance():
        """
        Analyze city performance metrics.
        Returns metrics and insights.
        """
        try:
            trips_df = pd.read_csv(DataPaths.FACT_TRIPS)
            cities_df = pd.read_csv(DataPaths.DIM_CITY)
            analysis_df = trips_df.merge(cities_df[['city_id', 'city_name']], on='city_id')
            
            city_metrics = analysis_df.groupby('city_name').agg({
                'trip_id': 'count',
                'fare_amount': 'mean',
                'distance_travelled(km)': 'mean',
                'passenger_rating': 'mean'
            }).round(2)
            
            city_metrics.columns = ['Total Trips', 'Avg Fare', 'Avg Distance', 'Avg Rating']
            city_metrics['Fare per KM'] = (city_metrics['Avg Fare'] / city_metrics['Avg Distance']).round(2)
            
            summary_stats = {
                "total_trips": city_metrics['Total Trips'].sum(),
                "average_fare": city_metrics['Avg Fare'].mean(),
                "average_distance": city_metrics['Avg Distance'].mean(),
                "average_rating": city_metrics['Avg Rating'].mean()
            }
            
            return city_metrics, summary_stats
        except Exception as e:
            raise Exception(f"Error analyzing city performance: {str(e)}")

    @staticmethod
    @st.cache_data
    def show_charts(city_metrics):
        # Define color scheme
        color_scheme = alt.Scale(scheme='dark2')

        # Create function to generate chart
        def create_chart(data, title, sort_order='descending'):
            return alt.Chart(data).mark_bar().encode(
                x=alt.X('city_name:N', title='City', sort='-y'),
                y=alt.Y('Total Trips:Q', title='Total Trips', sort=sort_order),
                color=alt.Color('city_name:N', scale=color_scheme),
                tooltip=[
                    alt.Tooltip('city_name:N', title='City'),
                    alt.Tooltip('Total Trips:Q', title='Total Trips', format=',')
                ]
            ).properties(
                title=title,
                height=300
            ).configure_axis(
                labelColor='white',
                titleColor='white'
            ).configure_title(
                color='white'
            )

        # Top 3 Cities Chart
        top_3_cities = city_metrics.nlargest(3, 'Total Trips').reset_index()
        top_chart = create_chart(top_3_cities, 'Top 3 Cities by Total Trips')

        # Bottom 3 Cities Chart
        bottom_3_cities = city_metrics.nsmallest(3, 'Total Trips').reset_index()
        bottom_chart = create_chart(bottom_3_cities, 'Bottom 3 Cities by Total Trips', 'ascending')

        # Display charts in two columns
        col1, col2 = st.columns(2)
        with col1:
            st.altair_chart(top_chart, use_container_width=True)
        with col2:
            st.altair_chart(bottom_chart, use_container_width=True)

    @staticmethod
    @st.cache_data
    def show_dataframes(city_metrics):
        st.subheader('City Performance Data')
        st.dataframe(city_metrics.style.format({
            'Total Trips': '{:,.0f}',
            'Avg Fare': '${:.2f}',
            'Avg Distance': '{:.2f} km',
            'Avg Rating': '{:.2f}',
            'Fare per KM': '${:.2f}'
        }))

    @staticmethod
    @st.cache_data
    def show_insights(city_metrics):
        st.subheader('City Performance Insights')
        total_trips = city_metrics['Total Trips'].sum()
        top_3_cities = city_metrics.nlargest(3, 'Total Trips')
        bottom_3_cities = city_metrics.nsmallest(3, 'Total Trips')
        top_3_trips = top_3_cities['Total Trips'].sum()
        bottom_3_trips = bottom_3_cities['Total Trips'].sum()
        top_3_percentage = (top_3_trips / total_trips) * 100
        bottom_3_percentage = (bottom_3_trips / total_trips) * 100

        st.markdown("### 🔑 Key Metrics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Top 3 Cities Trips", f"{top_3_trips:,}")
        with col2:
            st.metric("Bottom 3 Cities Trips", f"{bottom_3_trips:,}")

        st.markdown("### 📊 Performance Distribution")
        st.markdown(f"""
        - Top 3 cities account for **{top_3_percentage:.2f}%** of all trips
        - Bottom 3 cities represent **{bottom_3_percentage:.2f}%** of total trips
        """)

        st.markdown("### 📖 The Performance Story")
        st.markdown(f"""
        My analysis reveals significant performance disparities across cities:

        1. **Market Concentration**: The top 3 cities dominate, handling {top_3_percentage:.1f}% of all trips.
           This suggests a need for strategies to maintain the strong position in these key markets.

        2. **Growth Potential**: The bottom 3 cities contribute only {bottom_3_percentage:.1f}% of total trips.
           This highlights substantial growth opportunities if performance in these areas can be improved.

        3. **Strategic Focus**: The {top_3_percentage - bottom_3_percentage:.1f}% gap between top and bottom performers 
           indicates a need for targeted strategies and resource allocation to address unique market challenges and opportunities.
        """)

    @staticmethod
    @st.cache_data
    def show_overview(view_mode="Charts"):
        """
        Show overview of city performance metrics
        """
        try:
            city_metrics, summary_stats = CityPerformanceService.analyze_city_performance()
            
            if view_mode == "Charts":
                CityPerformanceService.show_charts(city_metrics)
            elif view_mode == "Dataframes":
                CityPerformanceService.show_dataframes(city_metrics)
            else:
                CityPerformanceService.show_insights(city_metrics)
        except Exception as e:
            st.error(f"Error showing city overview: {str(e)}")
            return None
