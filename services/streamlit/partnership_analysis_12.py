import pandas as pd
import altair as alt
import streamlit as st
from config.__init__ import DataPaths

alt.themes.enable('dark')

class PartnershipAnalysisService:
    @staticmethod
    def load_data():
        return {
            'fact_trips': pd.read_csv(DataPaths.FACT_TRIPS),
            'dim_date': pd.read_csv(DataPaths.DIM_DATE),
            'dim_city': pd.read_csv(DataPaths.DIM_CITY),
            'fact_passenger': pd.read_csv(DataPaths.FACT_PASSENGER_SUMMARY)
        }

    @staticmethod
    def calculate_partnership_metrics(data):
        trips_analysis = data['fact_trips'].merge(data['dim_date'][['date', 'day_type']], on='date')
        trips_analysis = trips_analysis.merge(data['dim_city'][['city_id', 'city_name']], on='city_id')

        partnership_metrics = pd.DataFrame()

        weekend_volume = trips_analysis[trips_analysis['day_type'] == 'Weekend'].groupby('city_name')['trip_id'].count()
        weekday_volume = trips_analysis[trips_analysis['day_type'] == 'Weekday'].groupby('city_name')['trip_id'].count()
        partnership_metrics['weekend_ratio'] = (weekend_volume / weekday_volume * 100).round(2)

        city_passengers = data['fact_passenger'].merge(data['dim_city'][['city_id', 'city_name']], on='city_id')
        new_customer_ratio = city_passengers.groupby('city_name').agg({
            'new_passengers': 'sum',
            'total_passengers': 'sum'
        })
        partnership_metrics['new_customer_ratio'] = (new_customer_ratio['new_passengers'] / new_customer_ratio['total_passengers'] * 100).round(2)

        avg_metrics = trips_analysis.groupby('city_name').agg({
            'fare_amount': 'mean',
            'distance_travelled(km)': 'mean',
            'passenger_rating': 'mean'
        }).round(2)

        partnership_metrics = partnership_metrics.join(avg_metrics)

        partnership_metrics['partnership_score'] = (
            partnership_metrics['weekend_ratio'] * 0.4 +
            partnership_metrics['new_customer_ratio'] * 0.3 +
            partnership_metrics['passenger_rating'] * 30
        ).round(2)

        return partnership_metrics.sort_values('partnership_score', ascending=False)

    @staticmethod
    def show_charts():
        data = PartnershipAnalysisService.load_data()
        partnership_metrics = PartnershipAnalysisService.calculate_partnership_metrics(data)

        chart = alt.Chart(partnership_metrics.reset_index()).mark_bar().encode(
            x=alt.X('city_name:N', title='City'),
            y=alt.Y('partnership_score:Q', title='Partnership Score'),
            color=alt.Color('city_name:N', scale=alt.Scale(scheme='category20'), title='City'),
            tooltip=['city_name:N', 'partnership_score:Q']
        ).properties(
            width=600,
            height=400,
            title='Partnership Potential Score by City'
        ).configure_axis(
            labelColor='white',
            titleColor='white'
        ).configure_title(
            color='white'
        )

        st.altair_chart(chart, use_container_width=True)

    @staticmethod
    def show_dataframes():
        data = PartnershipAnalysisService.load_data()
        partnership_metrics = PartnershipAnalysisService.calculate_partnership_metrics(data)
        st.dataframe(partnership_metrics)

    @staticmethod
    def show_insights():
        data = PartnershipAnalysisService.load_data()
        partnership_metrics = PartnershipAnalysisService.calculate_partnership_metrics(data)

        st.markdown("## 🤝 Partnership Potential Analysis Insights")

        # Top partnership opportunity
        top_city = partnership_metrics.index[0]
        top_score = partnership_metrics.iloc[0]['partnership_score']

        # Key metrics
        st.markdown("### 📊 Key Performance Indicators")
        cols = st.columns(3)
        metrics = ['partnership_score', 'weekend_ratio', 'new_customer_ratio', 'passenger_rating']
        labels = ['Partnership Score', 'Weekend Traffic Ratio', 'New Customer Ratio', 'Avg Passenger Rating']
        for i, (metric, label) in enumerate(zip(metrics, labels)):
            value = partnership_metrics.loc[top_city, metric]
            cols[i % 3].metric(label, f"{value:.2f}{'%' if 'ratio' in metric else ''}")

        # Insights
        st.markdown("### 🔍 Key Insights")
        insights = [
            f"**Top Partnership Candidate**: {top_city} with a partnership score of {top_score:.2f}",
            f"**Weekend Activity**: {partnership_metrics.loc[top_city, 'weekend_ratio']:.2f}% increase in weekend traffic",
            f"**Market Growth**: {partnership_metrics.loc[top_city, 'new_customer_ratio']:.2f}% new customer acquisition rate",
            f"**Customer Satisfaction**: Average passenger rating of {partnership_metrics.loc[top_city, 'passenger_rating']:.2f}"
        ]
        for insight in insights:
            st.markdown(f"- {insight}")

        # Story
        st.markdown("### 📖 Partnership Potential Story")
        story = f"""
        My analysis identifies {top_city} as the prime partnership candidate with a score of {top_score:.2f}. 
        Key factors contributing to this assessment include:
        
        1. A {partnership_metrics.loc[top_city, 'weekend_ratio']:.2f}% surge in weekend traffic, 
           indicating a thriving leisure and tourism sector.
        2. Strong market growth potential, with {partnership_metrics.loc[top_city, 'new_customer_ratio']:.2f}% 
           of the customer base being new acquisitions.
        3. High customer satisfaction levels, reflected in an average passenger rating of 
           {partnership_metrics.loc[top_city, 'passenger_rating']:.2f}.

        These insights suggest that {top_city} offers significant opportunities for targeted marketing, 
        customer base expansion, and maintaining high-quality service standards.
        """
        st.markdown(story)
