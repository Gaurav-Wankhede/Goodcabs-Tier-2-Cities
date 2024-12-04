# Removed unnecessary parts of the file
# Retain only the essential methods and imports
import pandas as pd
import altair as alt
import streamlit as st
from config.__init__ import DataPaths

class RatingAnalysisService:
    @staticmethod
    def show_charts():
        # Data Import
        fact_trips = pd.read_csv(DataPaths.FACT_TRIPS)
        dim_city = pd.read_csv(DataPaths.DIM_CITY)

        # Merge trips with city information
        trips_analysis = fact_trips.merge(dim_city, on='city_id')

        # Calculate average ratings by city and passenger type
        rating_metrics = trips_analysis.groupby(['city_name', 'passenger_type']).agg({
            'passenger_rating': 'mean',
            'driver_rating': 'mean'
        }).round(2).reset_index()

        # Create a heatmap with Altair
        heatmap = alt.Chart(rating_metrics).mark_rect().encode(
            x=alt.X('passenger_type:N', title='Passenger Type'),
            y=alt.Y('city_name:N', title='City'),
            color=alt.Color('passenger_rating:Q', scale=alt.Scale(scheme='goldorange'), title='Passenger Rating'),
            tooltip=['city_name:N', 'passenger_type:N', 'passenger_rating:Q']
        ).properties(
            title='Passenger Ratings Comparison (New vs Repeat Passengers)',
            width=600,
            height=400
        ).configure_axis(
            labelColor='white',
            titleColor='white'
        ).configure_title(
            color='white'
        )

        # Display the heatmap
        st.altair_chart(heatmap, use_container_width=True)

    @staticmethod
    def show_dataframes():
        # Data Import
        fact_trips = pd.read_csv(DataPaths.FACT_TRIPS)
        dim_city = pd.read_csv(DataPaths.DIM_CITY)

        # Merge trips with city information
        trips_analysis = fact_trips.merge(dim_city, on='city_id')

        # Calculate average ratings by city and passenger type
        rating_metrics = trips_analysis.groupby(['city_name', 'passenger_type']).agg({
            'passenger_rating': 'mean',
            'driver_rating': 'mean'
        }).round(2).reset_index()

        # Create detailed ratings table
        detailed_ratings = rating_metrics.pivot(index='city_name', 
                                                columns='passenger_type', 
                                                values=['passenger_rating', 'driver_rating'])
        detailed_ratings.columns = [f'{col[1]}_{col[0]}' for col in detailed_ratings.columns]

        # Display detailed ratings
        st.subheader('Detailed Ratings by City and Passenger Type')
        st.dataframe(detailed_ratings)

        # Calculate overall city ratings
        city_overall = rating_metrics.groupby('city_name').agg({
            'passenger_rating': 'mean',
            'driver_rating': 'mean'
        }).round(2)

        # Display top and bottom cities by passenger rating
        st.subheader('Top 3 Cities by Passenger Rating')
        st.dataframe(city_overall.nlargest(3, 'passenger_rating')[['passenger_rating']])

        st.subheader('Bottom 3 Cities by Passenger Rating')
        st.dataframe(city_overall.nsmallest(3, 'passenger_rating')[['passenger_rating']])

    @staticmethod
    def show_insights():
        # Calculate insights
        fact_trips = pd.read_csv(DataPaths.FACT_TRIPS)
        dim_city = pd.read_csv(DataPaths.DIM_CITY)
        trips_analysis = fact_trips.merge(dim_city, on='city_id')
        rating_metrics = trips_analysis.groupby(['city_name', 'passenger_type']).agg({
            'passenger_rating': 'mean',
            'driver_rating': 'mean'
        }).round(2).reset_index()
        
        city_overall = rating_metrics.groupby('city_name').agg({
            'passenger_rating': 'mean',
            'driver_rating': 'mean'
        }).round(2)
        
        top_city = city_overall['passenger_rating'].idxmax()
        bottom_city = city_overall['passenger_rating'].idxmin()
        avg_rating = city_overall['passenger_rating'].mean()
        rating_range = city_overall['passenger_rating'].max() - city_overall['passenger_rating'].min()
        
        st.subheader('Rating Analysis Insights')
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Top Rated City", top_city, f"{city_overall.loc[top_city, 'passenger_rating']:.2f}")
        col2.metric("Lowest Rated City", bottom_city, f"{city_overall.loc[bottom_city, 'passenger_rating']:.2f}")
        col3.metric("Average City Rating", f"{avg_rating:.2f}")
        col4.metric("Rating Range", f"{rating_range:.2f}")
        
        # Insights in Points
        st.subheader('Key Insights')
        st.markdown(f"""
        - 🌟 **Rating Spread**: A {rating_range:.2f} point difference exists between the highest and lowest rated cities.
        - 📊 **Top Performer**: {top_city} leads with a {city_overall.loc[top_city, 'passenger_rating']:.2f} average passenger rating.
        - 🔍 **Improvement Target**: {bottom_city} shows potential for enhancement with a {city_overall.loc[bottom_city, 'passenger_rating']:.2f} average rating.
        - 📈 **Overall Performance**: The average city rating stands at {avg_rating:.2f}, indicating general satisfaction levels.
        """)
        
        # Story Telling
        st.subheader('The Rating Analysis')
        st.markdown(f"""
        My analysis of the ratings data reveals a landscape of varying passenger satisfaction across different cities:

        1. **Rating Distribution**: 
           The ratings span a range of {rating_range:.2f} points, highlighting significant differences in passenger experiences between cities.

        2. **City Performance Spectrum**:
           - At the top: {top_city} excels with an average passenger rating of {city_overall.loc[top_city, 'passenger_rating']:.2f}.
           - At the bottom: {bottom_city} faces challenges, averaging {city_overall.loc[bottom_city, 'passenger_rating']:.2f} in passenger ratings.

        3. **Industry Benchmark**:
           With an overall average rating of {avg_rating:.2f}, this sets a baseline for city performance evaluation.

        4. **Opportunities for Improvement**:
           The gap between the highest and lowest rated cities suggests potential for standardizing service quality across all locations.

        These insights provide a data-driven foundation for targeted service enhancements and strategic decision-making to elevate passenger satisfaction across all service areas.
        """)
