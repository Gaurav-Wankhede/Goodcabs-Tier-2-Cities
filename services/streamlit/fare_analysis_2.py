import pandas as pd
import altair as alt
import streamlit as st
from config.__init__ import DataPaths

class FareAnalysisService:
    @staticmethod
    def _load_data():
        trips_df = pd.read_csv(DataPaths.FACT_TRIPS)
        cities_df = pd.read_csv(DataPaths.DIM_CITY)
        return trips_df, cities_df

    @staticmethod
    def _calculate_metrics(trips_df, cities_df):
        city_metrics = trips_df.groupby('city_id').agg({
            'fare_amount': 'mean',
            'distance_travelled(km)': 'mean'
        }).reset_index()
        city_metrics = city_metrics.merge(cities_df, on='city_id', how='left')
        city_metrics['fare_per_km'] = city_metrics['fare_amount'] / city_metrics['distance_travelled(km)']
        return city_metrics

    @staticmethod
    def show_charts():
        trips_df, cities_df = FareAnalysisService._load_data()
        city_metrics = FareAnalysisService._calculate_metrics(trips_df, cities_df)

        scatter_plot = alt.Chart(city_metrics).mark_circle(size=100).encode(
            x=alt.X('distance_travelled(km):Q', title='Average Distance Travelled (km)'),
            y=alt.Y('fare_amount:Q', title='Average Fare Amount'),
            color=alt.value('goldenrod'),
            tooltip=['city_name:N', 'fare_amount:Q', 'distance_travelled(km):Q']
        ).properties(
            title='Average Fare vs Distance Travelled per City',
            width=600,
            height=400
        ).configure_axis(
            labelColor='white',
            titleColor='white'
        ).configure_title(
            color='white'
        )

        st.altair_chart(scatter_plot, use_container_width=True)

    @staticmethod
    def show_dataframes():
        trips_df, cities_df = FareAnalysisService._load_data()
        city_metrics = FareAnalysisService._calculate_metrics(trips_df, cities_df)

        st.subheader('City Analysis - Sorted by Average Fare')
        st.dataframe(city_metrics[['city_name', 'fare_amount', 'distance_travelled(km)']]
                     .sort_values('fare_amount', ascending=False)
                     .round(2))

    @staticmethod
    def show_insights():
        trips_df, cities_df = FareAnalysisService._load_data()
        city_metrics = FareAnalysisService._calculate_metrics(trips_df, cities_df)

        st.subheader("Fare Analysis Insights")

        # Key Metrics
        total_cities = len(city_metrics)
        avg_fare = city_metrics['fare_amount'].mean()
        avg_distance = city_metrics['distance_travelled(km)'].mean()
        avg_fare_per_km = city_metrics['fare_per_km'].mean()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cities Analyzed", f"{total_cities}")
        col2.metric("Avg Fare", f"₹{avg_fare:.2f}")
        col3.metric("Avg Distance", f"{avg_distance:.2f} km")
        col4.metric("Avg Fare/km", f"₹{avg_fare_per_km:.2f}")

        # Key Points
        st.write("### Key Points")
        st.markdown(f"""
        - Analysis covers {total_cities} cities
        - Average fare across all cities: ₹{avg_fare:.2f}
        - Average trip distance: {avg_distance:.2f} km
        - Average fare per kilometer: ₹{avg_fare_per_km:.2f}
        """)

        # City-specific Insights
        st.write("### City-specific Insights")
        for _, row in city_metrics.iterrows():
            with st.expander(f"**{row['city_name']}**"):
                st.write(f"- Average Fare: ₹{row['fare_amount']:.2f}")
                st.write(f"- Average Distance: {row['distance_travelled(km)']:.2f} km")
                st.write(f"- Fare Efficiency: ₹{row['fare_per_km']:.2f} per km")

        # Story Telling
        st.write("### The Fare Analysis Story")
        highest_fare_city = city_metrics.loc[city_metrics['fare_amount'].idxmax()]
        lowest_fare_city = city_metrics.loc[city_metrics['fare_amount'].idxmin()]
        st.markdown(f"""
        My analysis reveals a diverse fare landscape across {total_cities} cities. The average fare stands at ₹{avg_fare:.2f}, 
        with trips covering an average distance of {avg_distance:.2f} km. This translates to an average fare of ₹{avg_fare_per_km:.2f} per kilometer.

        The fare story unfolds with {highest_fare_city['city_name']} leading the chart with the highest average fare of 
        ₹{highest_fare_city['fare_amount']:.2f}, while {lowest_fare_city['city_name']} offers the most economical rides 
        at ₹{lowest_fare_city['fare_amount']:.2f}. This stark contrast highlights the need for city-specific pricing strategies.

        These insights pave the way for potential fare structure optimizations, considering factors such as distance traveled, 
        city-specific dynamics, and overall fare efficiency. The data suggests opportunities for improving fare structures in 
        certain cities to align with the average fare per kilometer of ₹{avg_fare_per_km:.2f}.
        """)
