import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from config.__init__ import DataPaths
import streamlit as st
import altair as alt
from typing import Dict, List
import numpy as np

class RepeatPassengerAnalysisService:
    @staticmethod
    def analyze_passenger_frequency():
        """
        Analyze repeat passenger frequency patterns across cities.
        Returns visualizations and detailed frequency metrics.
        """
        try:
            # 1. Data Import using configured paths
            repeat_dist = pd.read_csv(DataPaths.DIM_REPEAT_TRIP_DISTRIBUTION)
            cities_df = pd.read_csv(DataPaths.DIM_CITY)

            # 2. Merge data and prepare
            trip_freq = repeat_dist.merge(cities_df, on='city_id')
            trip_freq['trip_number'] = trip_freq['trip_count'].str.extract(r'(\d+)').astype(int)
            trip_freq = trip_freq.sort_values('trip_number')

            # 3. Calculate total repeat passengers per city
            city_totals = trip_freq.groupby('city_name')['repeat_passenger_count'].sum().reset_index()

            # 4. Calculate percentage distribution
            trip_freq_pct = trip_freq.merge(city_totals, on='city_name', suffixes=('', '_total'))
            trip_freq_pct['percentage'] = (
                trip_freq_pct['repeat_passenger_count'] / 
                trip_freq_pct['repeat_passenger_count_total'] * 100
            ).round(2)

            # 5. Analyze high frequency patterns (5 or more trips)
            high_freq_analysis = trip_freq_pct[trip_freq_pct['trip_number'] >= 5].groupby('city_name').agg({
                'repeat_passenger_count': 'sum',
                'repeat_passenger_count_total': 'first'
            }).assign(
                high_freq_percentage=lambda x: (
                    x['repeat_passenger_count'] / x['repeat_passenger_count_total'] * 100
                ).round(2)
            ).sort_values('high_freq_percentage', ascending=False)

            return trip_freq_pct, high_freq_analysis

        except Exception as e:
            raise Exception(f"Error analyzing repeat passenger patterns: {str(e)}")

    @staticmethod
    def analyze_repeat_passengers():
        # Load data
        repeat_dist = pd.read_csv(DataPaths.DIM_REPEAT_TRIP_DISTRIBUTION)
        dim_city = pd.read_csv(DataPaths.DIM_CITY)

        # Merge data
        trip_freq = repeat_dist.merge(dim_city, on='city_id')

        # Extract numeric trip count and sort by it
        trip_freq['trip_number'] = trip_freq['trip_count'].str.extract(r'(\d+)').astype(int)
        trip_freq = trip_freq.sort_values('trip_number')

        # Calculate total repeat passengers per city
        city_totals = trip_freq.groupby('city_name')['repeat_passenger_count'].sum().reset_index()

        # Calculate percentage distribution
        trip_freq_pct = trip_freq.merge(city_totals, on='city_name', suffixes=('', '_total'))
        trip_freq_pct['percentage'] = (trip_freq_pct['repeat_passenger_count'] / 
                                     trip_freq_pct['repeat_passenger_count_total'] * 100).round(2)

        # Analyze high frequency patterns (5 or more trips)
        high_freq_analysis = trip_freq_pct[trip_freq_pct['trip_number'] >= 5].groupby('city_name').agg({
            'repeat_passenger_count': 'sum',
            'repeat_passenger_count_total': 'first'
        }).assign(
            high_freq_percentage=lambda x: (x['repeat_passenger_count'] / x['repeat_passenger_count_total'] * 100).round(2)
        ).sort_values('high_freq_percentage', ascending=False)

        return trip_freq_pct, high_freq_analysis

    @staticmethod
    def show_charts(trip_freq_pct, high_freq_analysis):
        col1, col2 = st.columns(2)

        with col1:
            freq_dist = trip_freq_pct.pivot_table(
                index='city_name',
                columns='trip_number',
                values='percentage',
                aggfunc='mean'
            ).round(2).reset_index().melt(id_vars='city_name')

            heatmap = alt.Chart(freq_dist).mark_rect().encode(
                x=alt.X('trip_number:O', title='Number of Trips per Month'),
                y=alt.Y('city_name:N', title='City'),
                color=alt.Color('value:Q', title='Percentage of Repeat Passengers', scale=alt.Scale(scheme='yelloworangered')),
                tooltip=['city_name', 'trip_number', 'value']
            ).properties(
                width=300,
                height=400,
                title='Trip Frequency Distribution Patterns by City'
            ).configure(background='black')

            st.altair_chart(heatmap, use_container_width=True)

        with col2:
            bar_chart = alt.Chart(high_freq_analysis.reset_index()).mark_bar(color='#00FF7F').encode(
                x=alt.X('city_name:N', title='City', sort='-y'),
                y=alt.Y('high_freq_percentage:Q', title='Percentage of Total Repeat Passengers'),
                tooltip=['city_name', 'high_freq_percentage']
            ).properties(
                width=300,
                height=400,
                title='High-Frequency Repeat Passengers (5+ trips) by City'
            ).configure(background='black')

            st.altair_chart(bar_chart, use_container_width=True)

    @staticmethod
    def show_dataframes(trip_freq_pct, high_freq_analysis):
        # Display detailed frequency distribution table
        freq_dist = trip_freq_pct.pivot_table(
            index='city_name',
            columns='trip_number',
            values='percentage',
            aggfunc='mean'
        ).round(2)

        st.write("## Detailed Trip Frequency Distribution by City (%)")
        st.dataframe(freq_dist)

        # Display high frequency analysis
        high_freq_result = pd.DataFrame({
            'Total Repeat Passengers': high_freq_analysis['repeat_passenger_count_total'],
            'High Freq Passengers': high_freq_analysis['repeat_passenger_count'],
            'High Freq %': high_freq_analysis['high_freq_percentage']
        })

        st.write("## Cities Ranked by High-Frequency Repeat Passengers (5+ trips)")
        st.dataframe(high_freq_result)

    @staticmethod
    def show_insights(high_freq_analysis):
        st.write("### Repeat Passenger Analysis Insights")

        # Key metrics
        total_cities = len(high_freq_analysis)
        avg_high_freq_percentage = high_freq_analysis['high_freq_percentage'].mean()
        top_city = high_freq_analysis.iloc[0]
        bottom_city = high_freq_analysis.iloc[-1]

        # Display key metrics
        st.write("### Key Metrics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Cities", f"{total_cities}")
            st.metric("Top City", f"{top_city.name}: {top_city['high_freq_percentage']:.2f}%")
        with col2:
            st.metric("Avg High-Freq %", f"{avg_high_freq_percentage:.2f}%")
            st.metric("Bottom City", f"{bottom_city.name}: {bottom_city['high_freq_percentage']:.2f}%")

        # Key points
        st.write("#### Key Findings")
        st.markdown(f"""
        - Highest percentage of high-frequency repeat passengers: {top_city.name} ({top_city['high_freq_percentage']:.2f}%)
        - Lowest percentage of high-frequency repeat passengers: {bottom_city.name} ({bottom_city['high_freq_percentage']:.2f}%)
        - Average high-frequency percentage across all cities: {avg_high_freq_percentage:.2f}%
        - Total cities analyzed: {total_cities}
        """)

        # City-specific insights
        st.write("#### City-specific Insights")
        for city, row in high_freq_analysis.iterrows():
            with st.expander(f"{city}"):
                st.write(f"- High-frequency passengers: {row['high_freq_percentage']:.2f}%")
                st.write(f"- Total repeat passengers: {row['repeat_passenger_count_total']:,}")
                st.write(f"- High-frequency passenger count: {row['repeat_passenger_count']:,}")

        # Story
        st.write("#### Analysis Story")
        st.markdown(f"""
        The analysis of repeat passenger behavior across {total_cities} cities reveals significant variations 
        in high-frequency ridership patterns:

        1. **Leading City**: {top_city.name} stands out with {top_city['high_freq_percentage']:.2f}% of its 
           repeat passengers taking 5 or more trips per month. This could indicate:
           - Effective customer retention strategies
           - High service quality
           - Strong market presence

        2. **Opportunity for Improvement**: {bottom_city.name} shows the lowest percentage of high-frequency 
           repeat passengers at {bottom_city['high_freq_percentage']:.2f}%. This suggests potential for:
           - Targeted marketing campaigns
           - Service quality enhancements
           - Customer loyalty program improvements

        3. **Industry Benchmark**: The average high-frequency percentage of {avg_high_freq_percentage:.2f}% 
           across all cities provides a valuable benchmark for assessing individual city performance.

        4. **Strategic Implications**: Cities falling below the average may benefit from:
           - Analyzing successful strategies from top-performing cities
           - Implementing tailored retention programs
           - Focusing on increasing trip frequency among existing repeat customers

        This data-driven analysis provides a foundation for developing targeted strategies to enhance 
        customer loyalty and increase the proportion of high-frequency repeat passengers across all cities.
        """)
