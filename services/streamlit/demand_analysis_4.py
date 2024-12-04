import pandas as pd
import altair as alt
import streamlit as st
from config.__init__ import DataPaths

class DemandAnalysisService:
    @staticmethod
    @st.cache_data
    def analyze_demand():
        """
        Analyze demand patterns across cities and time periods.
        """
        try:
            # Load data
            fact_trips = pd.read_csv(DataPaths.FACT_TRIPS)
            dim_city = pd.read_csv(DataPaths.DIM_CITY)
            dim_date = pd.read_csv(DataPaths.DIM_DATE)

            # Merge trips with city and date information
            trips_analysis = fact_trips.merge(dim_city, on='city_id').merge(dim_date[['date', 'month_name', 'start_of_month']], on='date')

            # Calculate monthly trips for each city
            monthly_trips = trips_analysis.groupby(['city_name', 'start_of_month', 'month_name'])['trip_id'].count().reset_index()
            monthly_trips.columns = ['city_name', 'start_of_month', 'month_name', 'total_trips']

            # Find peak and low demand months for each city
            peak_low_demand = monthly_trips.groupby('city_name').agg({
                'total_trips': ['idxmax', 'idxmin']
            }).reset_index()

            # Get the actual months and trip counts
            results = []
            for city in peak_low_demand['city_name']:
                city_data = monthly_trips[monthly_trips['city_name'] == city]
                peak_idx = city_data['total_trips'].idxmax()
                low_idx = city_data['total_trips'].idxmin()
                results.append({
                    'City': city,
                    'Peak Month': city_data.loc[peak_idx, 'month_name'],
                    'Peak Trips': f"{city_data.loc[peak_idx, 'total_trips']:,}",
                    'Low Month': city_data.loc[low_idx, 'month_name'],
                    'Low Trips': f"{city_data.loc[low_idx, 'total_trips']:,}"
                })
            results_df = pd.DataFrame(results)

            return monthly_trips, results_df
        except Exception as e:
            raise Exception(f"Error analyzing demand: {str(e)}")

    @staticmethod
    @st.cache_data
    def show_charts(monthly_trips):
        # Create heatmap using Altair
        heatmap = alt.Chart(monthly_trips).mark_rect().encode(
            x=alt.X('month_name:O', title='Month'),
            y=alt.Y('city_name:O', title='City'),
            color=alt.Color('total_trips:Q', scale=alt.Scale(scheme='goldorange'), title='Number of Trips'),
            tooltip=['city_name', 'month_name', 'total_trips']
        ).properties(
            width=600,
            height=400,
            title='Monthly Trip Distribution by City'
        ).configure(background='black')
        st.altair_chart(heatmap)

    @staticmethod
    @st.cache_data
    def show_dataframes(results_df):
        # Display results in Streamlit
        st.write("## Peak and Low Demand Months by City")
        st.write(results_df)

    @staticmethod
    @st.cache_data
    def show_insights(results_df):
        st.write("### Demand Analysis Insights")
        
        # Key metrics
        total_cities = len(results_df)
        avg_peak_trips = results_df['Peak Trips'].apply(lambda x: int(x.replace(',', ''))).mean()
        avg_low_trips = results_df['Low Trips'].apply(lambda x: int(x.replace(',', ''))).mean()
        avg_variation = ((avg_peak_trips - avg_low_trips) / avg_low_trips) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cities Analyzed", f"{total_cities}")
        col2.metric("Avg Peak Demand", f"{avg_peak_trips:,.0f}")
        col3.metric("Avg Low Demand", f"{avg_low_trips:,.0f}")
        col4.metric("Avg Demand Variation", f"{avg_variation:.1f}%")
        
        st.write("### City-specific Insights")
        for _, row in results_df.iterrows():
            peak_trips = int(row['Peak Trips'].replace(',', ''))
            low_trips = int(row['Low Trips'].replace(',', ''))
            variation = ((peak_trips - low_trips) / low_trips) * 100
            
            with st.expander(f"**{row['City']}**"):
                st.write(f"- Peak demand: {row['Peak Month']} ({row['Peak Trips']} trips)")
                st.write(f"- Low demand: {row['Low Month']} ({row['Low Trips']} trips)")
                st.write(f"- Demand variation: {variation:.1f}%")
        
        st.write("### Key Takeaways")
        st.markdown(f"""
        - The analysis covers {total_cities} cities
        - Average peak demand: {avg_peak_trips:,.0f} trips
        - Average low demand: {avg_low_trips:,.0f} trips
        - Average demand variation: {avg_variation:.1f}%
        
        This data reveals:
        1. Significant demand fluctuations across cities and months
        2. Potential for tailored strategies during high and low periods
        3. Importance of considering local factors influencing demand
        4. Opportunities for demand-based resource optimization
        """)

    @staticmethod
    @st.cache_data
    def show_overview(view_mode="Charts"):
        """
        Show overview of demand analysis
        """
        try:
            monthly_trips, results_df = DemandAnalysisService.analyze_demand()
            
            if view_mode == "Charts":
                DemandAnalysisService.show_charts(monthly_trips)
            elif view_mode == "Dataframes":
                DemandAnalysisService.show_dataframes(results_df)
            else:
                DemandAnalysisService.show_insights(results_df)
        except Exception as e:
            st.error(f"Error showing demand overview: {str(e)}")
            return None
