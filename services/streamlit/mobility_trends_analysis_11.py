import pandas as pd
import streamlit as st
import altair as alt
from config.__init__ import DataPaths

class MobilityTrendsAnalysisService:
    @staticmethod
    def get_mobility_data():
        """Get mobility trends analysis data."""
        # Read the required data
        fact_trips = pd.read_csv(DataPaths.FACT_TRIPS)
        dim_city = pd.read_csv(DataPaths.DIM_CITY)

        # Analyze trip distances and fares by city
        city_metrics = fact_trips.merge(dim_city[['city_id', 'city_name']], on='city_id')
        city_analysis = city_metrics.groupby('city_name').agg({
            'distance_travelled(km)': ['mean', 'sum'],
            'fare_amount': ['mean', 'sum'],
            'trip_id': 'count'
        }).round(2)

        city_analysis.columns = ['avg_distance', 'total_distance', 'avg_fare', 'total_fare', 'total_trips']

        # Calculate per km fare and carbon metrics
        city_analysis['fare_per_km'] = (city_analysis['avg_fare'] / city_analysis['avg_distance']).round(2)
        city_analysis['total_carbon_kg'] = (city_analysis['total_distance'] * 0.14).round(2)  # Assuming 0.14 kg CO2/km

        # Sort by total carbon footprint
        city_analysis = city_analysis.sort_values('total_carbon_kg', ascending=False)

        # Calculate potential EV impact
        ev_carbon_per_km = 0.053  # kg CO2/km for EVs
        city_analysis['ev_carbon_savings'] = (city_analysis['total_carbon_kg'] - 
                                            (city_analysis['total_distance'] * ev_carbon_per_km)).round(2)

        return city_analysis

    @staticmethod
    def show_charts():
        """Display mobility trends analysis charts."""
        st.subheader("Mobility Trends Analysis")
        
        # Get data
        city_analysis = MobilityTrendsAnalysisService.get_mobility_data()

        # Ensure data integrity
        if city_analysis.empty:
            st.error("Insufficient data for Mobility Trends analysis.")
            return

        # Split into two charts
        total_carbon_chart = alt.Chart(city_analysis.reset_index()).mark_bar().encode(
            x=alt.X('city_name:N', title='City'),
            y=alt.Y('total_carbon_kg:Q', title='Total Carbon Emissions (kg CO2)'),
            color=alt.Color('city_name:N', scale=alt.Scale(scheme='dark2'), title='City'),
            tooltip=['city_name:N', 'total_carbon_kg:Q']
        ).properties(
            width=300,
            height=400,
            title='Total Carbon Emissions by City'
        ).configure_axis(
            labelColor='white',
            titleColor='white'
        ).configure_title(
            color='white'
        )

        ev_savings_chart = alt.Chart(city_analysis.reset_index()).mark_bar().encode(
            x=alt.X('city_name:N', title='City'),
            y=alt.Y('ev_carbon_savings:Q', title='EV Carbon Savings (kg CO2)'),
            color=alt.Color('city_name:N', scale=alt.Scale(scheme='dark2'), title='City'),
            tooltip=['city_name:N', 'ev_carbon_savings:Q']
        ).properties(
            width=300,
            height=400,
            title='EV Carbon Savings by City'
        ).configure_axis(
            labelColor='white',
            titleColor='white'
        ).configure_title(
            color='white'
        )

        # Display in two columns
        col1, col2 = st.columns(2)
        with col1:
            st.altair_chart(total_carbon_chart, use_container_width=True)
        with col2:
            st.altair_chart(ev_savings_chart, use_container_width=True)

    @staticmethod
    def show_dataframes():
        """Display mobility trends analysis data."""
        st.subheader("Mobility Trends Analysis Data")
        
        # Get data
        city_analysis = MobilityTrendsAnalysisService.get_mobility_data()
        
        # Display city-wise analysis
        st.write("### City-wise Environmental Impact Analysis")
        st.dataframe(
            city_analysis.style.format({
                'avg_distance': '{:,.2f}',
                'total_distance': '{:,.2f}',
                'avg_fare': '{:,.2f}',
                'total_fare': '{:,.2f}',
                'total_trips': '{:,.0f}',
                'fare_per_km': '{:,.2f}',
                'total_carbon_kg': '{:,.2f}',
                'ev_carbon_savings': '{:,.2f}'
            }),
            use_container_width=True
        )

    @staticmethod
    def show_insights():
        """Display key insights from mobility trends analysis."""
        st.subheader("Mobility Trends Analysis Insights")
        
        city_analysis = MobilityTrendsAnalysisService.get_mobility_data()
        
        total_current_emissions = city_analysis['total_carbon_kg'].sum()
        total_ev_emissions = (city_analysis['total_distance'] * 0.053).sum()
        total_savings = total_current_emissions - total_ev_emissions
        percentage_reduction = (total_savings / total_current_emissions * 100).round(2)

        st.write("### Key Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Current CO2 Emissions", f"{total_current_emissions:,.2f} kg")
        col2.metric("Potential EV CO2 Emissions", f"{total_ev_emissions:,.2f} kg")
        col3.metric("Carbon Footprint Reduction Potential", f"{percentage_reduction:.2f}%")

        st.write("### Environmental Impact Analysis")
        st.markdown(f"""
        - **Current Situation**: The analysis reveals a total carbon emission of {total_current_emissions:,.2f} kg CO2.
        - **EV Transition Potential**: By switching to electric vehicles, emissions could be reduced to {total_ev_emissions:,.2f} kg CO2.
        - **Potential Impact**: This transition could lead to a carbon footprint reduction of {percentage_reduction:.2f}%, saving {total_savings:,.2f} kg of CO2.
        """)

        st.write("### City-Specific Insights")
        for city, data in city_analysis.iterrows():
            with st.expander(f"{city} Analysis"):
                current_emissions = data['total_carbon_kg']
                potential_ev_emissions = data['total_distance'] * 0.053
                city_savings = current_emissions - potential_ev_emissions
                city_percentage = (city_savings / current_emissions * 100).round(2)
                
                st.metric("Emission Reduction Potential", f"{city_percentage:.2f}%")
                st.markdown(f"""
                - Current Emissions: {current_emissions:,.2f} kg
                - Potential EV Emissions: {potential_ev_emissions:,.2f} kg
                - Potential Savings: {city_savings:,.2f} kg
                - Average Trip Distance: {data['avg_distance']:.2f} km
                - Fare per km: ₹{data['fare_per_km']:.2f}
                """)

        st.write("### Data-Driven Recommendations")
        highest_emission_city = city_analysis['total_carbon_kg'].idxmax()
        highest_distance_city = city_analysis['avg_distance'].idxmax()
        
        st.markdown(f"""
        1. **EV Adoption Strategy**: Prioritize {highest_emission_city} for EV implementation due to its high emission levels.
        2. **Infrastructure Planning**: Focus on developing EV charging infrastructure in {highest_distance_city}, which has the longest average trip distances.
        3. **Environmental Campaign**: Highlight the potential {percentage_reduction:.2f}% emission reduction in marketing efforts.
        4. **Pricing Review**: Evaluate the current fare structure to promote eco-friendly transportation options.
        5. **Ongoing Assessment**: Implement regular analysis updates to track progress and identify emerging trends or opportunities.
        """)
