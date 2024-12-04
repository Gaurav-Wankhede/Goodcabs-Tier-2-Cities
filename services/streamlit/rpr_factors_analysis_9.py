import pandas as pd
import streamlit as st
import altair as alt
from config.__init__ import DataPaths

class RPRFactorsAnalysisService:
    @staticmethod
    @st.cache_data
    def get_factors_data():
        """Get RPR factors analysis data."""
        # Read the required data
        fact_trips = pd.read_csv(DataPaths.FACT_TRIPS)
        fact_passenger = pd.read_csv(DataPaths.FACT_PASSENGER_SUMMARY)
        dim_city = pd.read_csv(DataPaths.DIM_CITY)

        # Calculate RPR% for each city
        fact_passenger['RPR%'] = (fact_passenger['repeat_passengers'] / fact_passenger['total_passengers'] * 100).round(2)
        city_rpr = fact_passenger.groupby('city_id')['RPR%'].mean().round(2)

        # Calculate average metrics by city
        city_metrics = fact_trips.groupby('city_id').agg({
            'passenger_rating': 'mean',
            'fare_amount': 'mean',
            'distance_travelled(km)': 'mean'
        }).round(2)

        # Combine metrics
        city_analysis = pd.DataFrame({
            'RPR%': city_rpr,
            'Avg_Rating': city_metrics['passenger_rating'],
            'Avg_Fare': city_metrics['fare_amount'],
            'Avg_Distance': city_metrics['distance_travelled(km)']
        }).reset_index()

        # Add city names
        city_analysis = city_analysis.merge(dim_city[['city_id', 'city_name']], on='city_id')
        
        # Calculate correlations
        correlation_matrix = city_analysis[['RPR%', 'Avg_Rating', 'Avg_Fare', 'Avg_Distance']].corr()
        
        return city_analysis, correlation_matrix

    @staticmethod
    @st.cache_data
    def show_charts():
        """Display RPR factors analysis charts."""
        st.subheader("RPR Factors Analysis Charts")
        
        # Get data
        city_analysis, correlation_matrix = RPRFactorsAnalysisService.get_factors_data()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Correlation Heatmap
            corr_data = correlation_matrix.reset_index().melt(id_vars='index')
            heatmap = alt.Chart(corr_data).mark_rect().encode(
                x=alt.X('index:N', title=None),
                y=alt.Y('variable:N', title=None),
                color=alt.Color('value:Q', scale=alt.Scale(scheme='redyellowgreen', domain=[-1, 1])),
                tooltip=['index', 'variable', alt.Tooltip('value:Q', format='.2f')]
            ).properties(
                width=300,
                height=300,
                title='Correlation Matrix'
            ).configure_view(
                strokeWidth=0
            ).configure_axis(
                labelColor='white',
                titleColor='white'
            ).configure_title(
                color='white'
            )
            
            st.altair_chart(heatmap, use_container_width=True)
        
        with col2:
            # Scatter plot with highest correlation factor
            scatter = alt.Chart(city_analysis).mark_circle(color='goldenrod').encode(
                x=alt.X('Avg_Rating:Q', title='Average Rating'),
                y=alt.Y('RPR%:Q', title='RPR%'),
                tooltip=['city_name', 'RPR%', 'Avg_Rating']
            ).properties(
                width=300,
                height=300,
                title='RPR% vs Average Rating'
            ).configure_view(
                strokeWidth=0
            ).configure_axis(
                labelColor='white',
                titleColor='white',
                gridColor='#444444'
            ).configure_title(
                color='white'
            )
            
            st.altair_chart(scatter, use_container_width=True)

    @staticmethod
    @st.cache_data
    def show_dataframes():
        """Display RPR factors analysis data."""
        st.subheader("RPR Factors Analysis Data")
        
        # Get data
        city_analysis, correlation_matrix = RPRFactorsAnalysisService.get_factors_data()
        
        # Display city analysis
        st.write("### City-wise Analysis")
        st.dataframe(
            city_analysis.sort_values('RPR%', ascending=False).style.format({
                'RPR%': '{:.2f}%',
                'Avg_Rating': '{:.2f}',
                'Avg_Fare': '{:.2f}',
                'Avg_Distance': '{:.2f}'
            }),
            use_container_width=True
        )
        
        # Display correlations
        st.write("### Correlation with RPR%")
        correlations = correlation_matrix['RPR%'].sort_values(ascending=False)
        st.dataframe(
            pd.DataFrame(correlations).style.format('{:.2f}'),
            use_container_width=True
        )

    @staticmethod
    @st.cache_data
    def show_insights():
        """Display key insights from RPR factors analysis."""
        st.subheader("RPR Factors Analysis Insights")
        
        # Get data
        city_analysis, correlation_matrix = RPRFactorsAnalysisService.get_factors_data()
        
        # Calculate key statistics
        correlations = correlation_matrix['RPR%'].sort_values(ascending=False)
        top_city = city_analysis.sort_values('RPR%', ascending=False).iloc[0]
        bottom_city = city_analysis.sort_values('RPR%', ascending=False).iloc[-1]
        
        # Key Metrics
        st.write("### 📊 Key Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Highest RPR%", f"{top_city['RPR%']:.2f}%", top_city['city_name'])
        col2.metric("Lowest RPR%", f"{bottom_city['RPR%']:.2f}%", bottom_city['city_name'])
        col3.metric("Strongest Correlation", f"{correlations.iloc[1]:.2f}", correlations.index[1])

        # Key Insights
        st.write("### 🔍 Key Insights")
        st.markdown(f"""
        - **Correlation Analysis:**
          - Highest positive correlation: {max(correlations.iloc[1:]):.2f} with {correlations.index[1]}
          - Highest negative correlation: {min(correlations.iloc[1:]):.2f} with {correlations.index[-1]}
        - **City Performance Comparison:**
          - Top performer: {top_city['city_name']} with {top_city['RPR%']:.2f}% RPR
          - Lowest performer: {bottom_city['city_name']} with {bottom_city['RPR%']:.2f}% RPR
          - Rating comparison: Top city {top_city['Avg_Rating']:.2f}, Bottom city {bottom_city['Avg_Rating']:.2f}
        - **Fare and Distance Analysis:**
          - Fare comparison: Top city ₹{top_city['Avg_Fare']:.2f}, Bottom city ₹{bottom_city['Avg_Fare']:.2f}
          - Distance comparison: Top city {top_city['Avg_Distance']:.2f} km, Bottom city {bottom_city['Avg_Distance']:.2f} km
        """)

        # Story Telling
        st.write("### 📖 RPR Analysis Narrative")
        st.markdown(f"""
        The analysis of Repeat Passenger Rate (RPR) reveals significant insights:

        1. **Performance Spectrum:**
           - {top_city['city_name']} leads with {top_city['RPR%']:.2f}% RPR
           - {bottom_city['city_name']} shows potential for improvement at {bottom_city['RPR%']:.2f}% RPR

        2. **Key Correlations:**
           - {correlations.index[1]} demonstrates the strongest positive correlation ({correlations.iloc[1]:.2f}) with RPR
           - This factor could be crucial for improving repeat rates across cities

        3. **City-Specific Insights:**
           - Top performer ({top_city['city_name']}) characteristics:
             * Average rating: {top_city['Avg_Rating']:.2f}
             * Average fare: ₹{top_city['Avg_Fare']:.2f}
             * Average trip distance: {top_city['Avg_Distance']:.2f} km
           - Area for improvement ({bottom_city['city_name']}) characteristics:
             * Average rating: {bottom_city['Avg_Rating']:.2f}
             * Average fare: ₹{bottom_city['Avg_Fare']:.2f}
             * Average trip distance: {bottom_city['Avg_Distance']:.2f} km

        4. **Strategic Focus:**
           - Replicate successful practices from {top_city['city_name']}
           - Address challenges in {bottom_city['city_name']}
           - Leverage the impact of {correlations.index[1]} to enhance overall service quality and customer retention
        """)
