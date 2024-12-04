import pandas as pd
import streamlit as st
import altair as alt
from config.__init__ import DataPaths

class TargetAnalysisService:
    @staticmethod
    def calculate_performance(actual, target):
        """Calculate performance metrics and status."""
        diff = ((actual - target) / target * 100).round(2)
        if diff < -5:
            status = 'Missed'
        elif diff > 5:
            status = 'Exceeded'
        else:
            status = 'Met'
        return diff, status

    @staticmethod
    def get_performance_data():
        """Get performance data for all cities."""
        # Data Import using DataPaths
        fact_trips = pd.read_csv(DataPaths.FACT_TRIPS)
        fact_passenger = pd.read_csv(DataPaths.FACT_PASSENGER_SUMMARY)
        dim_city = pd.read_csv(DataPaths.DIM_CITY)
        dim_date = pd.read_csv(DataPaths.DIM_DATE)
        target_trips = pd.read_csv(DataPaths.MONTHLY_TARGET_TRIPS)
        target_passengers = pd.read_csv(DataPaths.MONTHLY_TARGET_NEW_PASSENGERS)
        target_ratings = pd.read_csv(DataPaths.CITY_TARGET_PASSENGER_RATING)

        # Calculate actual metrics
        # 1. Monthly trips by city
        actual_trips = fact_trips.groupby(['city_id', 'date'])['trip_id'].count().reset_index()
        actual_trips = actual_trips.merge(dim_date[['date', 'start_of_month']], on='date')
        monthly_trips = actual_trips.groupby(['city_id', 'start_of_month'])['trip_id'].sum().reset_index()

        # 2. Monthly ratings by city
        monthly_ratings = fact_trips.groupby(['city_id', 'date'])['passenger_rating'].mean().reset_index()
        monthly_ratings = monthly_ratings.merge(dim_date[['date', 'start_of_month']], on='date')
        monthly_ratings = monthly_ratings.groupby(['city_id', 'start_of_month'])['passenger_rating'].mean().round(2).reset_index()

        # Combine actual vs target
        performance_data = []
        for city_id in dim_city['city_id'].unique():
            city_name = dim_city[dim_city['city_id'] == city_id]['city_name'].iloc[0]
            
            # Get city's data
            city_trips = monthly_trips[monthly_trips['city_id'] == city_id]
            city_ratings = monthly_ratings[monthly_ratings['city_id'] == city_id]
            city_passengers = fact_passenger[fact_passenger['city_id'] == city_id]
            
            # Get targets
            city_trip_target = target_trips[target_trips['city_id'] == city_id]['total_target_trips'].mean()
            city_passenger_target = target_passengers[target_passengers['city_id'] == city_id]['target_new_passengers'].mean()
            city_rating_target = target_ratings[target_ratings['city_id'] == city_id]['target_avg_passenger_rating'].iloc[0]
            
            # Calculate performance
            avg_trips = city_trips['trip_id'].mean() if not city_trips.empty else 0
            avg_rating = city_ratings['passenger_rating'].mean() if not city_ratings.empty else 0
            avg_new_passengers = city_passengers['new_passengers'].mean() if not city_passengers.empty else 0
            
            trip_diff, trip_status = TargetAnalysisService.calculate_performance(avg_trips, city_trip_target)
            passenger_diff, passenger_status = TargetAnalysisService.calculate_performance(avg_new_passengers, city_passenger_target)
            rating_diff, rating_status = TargetAnalysisService.calculate_performance(avg_rating, city_rating_target)
            
            performance_data.append({
                'City': city_name,
                'Trips_Target': int(city_trip_target),
                'Trips_Actual': int(avg_trips),
                'Trips_Diff%': trip_diff,
                'Trips_Status': trip_status,
                'NewPass_Target': int(city_passenger_target),
                'NewPass_Actual': int(avg_new_passengers),
                'NewPass_Diff%': passenger_diff,
                'NewPass_Status': passenger_status,
                'Rating_Target': round(city_rating_target, 2),
                'Rating_Actual': round(avg_rating, 2),
                'Rating_Diff%': rating_diff,
                'Rating_Status': rating_status
            })

        return pd.DataFrame(performance_data).sort_values('City')

    @staticmethod
    def show_charts():
        """Display performance charts using Altair."""
        st.subheader("Target Achievement Analysis")
        
        # Get performance data
        performance_df = TargetAnalysisService.get_performance_data()
        
        # Prepare data for visualization
        metrics_data = []
        for _, row in performance_df.iterrows():
            metrics_data.append({
                'City': row['City'],
                'Trips': row['Trips_Diff%'],
                'NewPass': row['NewPass_Diff%'],
                'Rating': row['Rating_Diff%'],
                'Trips_Status': row['Trips_Status'],
                'NewPass_Status': row['NewPass_Status'],
                'Rating_Status': row['Rating_Status']
            })
        
        metrics_df = pd.DataFrame(metrics_data)
        
        # Melt the dataframe to get it into the right format for Altair
        melted_df = pd.melt(metrics_df, id_vars=['City'], 
                            value_vars=['Trips', 'NewPass', 'Rating'],
                            var_name='Metric', value_name='Difference')
        
        # Add status to melted dataframe
        melted_df['Status'] = melted_df.apply(lambda row: metrics_df.loc[metrics_df['City'] == row['City'], f"{row['Metric']}_Status"].values[0], axis=1)
        
        # Create heatmap using Altair
        heatmap = alt.Chart(melted_df).mark_rect().encode(
            x=alt.X('Metric:N', title='Metric'),
            y=alt.Y('City:N', title='City'),
            color=alt.Color('Difference:Q',
                          scale=alt.Scale(scheme='redyellowgreen', domain=[-20, 20]),
                          title='% Difference from Target'),
            tooltip=[
                alt.Tooltip('City:N'),
                alt.Tooltip('Metric:N'),
                alt.Tooltip('Difference:Q', format='.1f'),
                alt.Tooltip('Status:N')
            ]
        ).properties(
            title='Target Achievement by City and Metric',
            width=400,
            height=600
        ).configure_view(
            strokeWidth=0
        ).configure_axis(
            labelColor='white',
            titleColor='white'
        ).configure_title(
            color='white'
        )
        
        st.altair_chart(heatmap, use_container_width=True)

    @staticmethod
    def show_dataframes():
        """Display performance data in tabular format."""
        st.subheader("Performance Metrics by City")
        
        # Get performance data
        performance_df = TargetAnalysisService.get_performance_data()
        
        # Create three separate dataframes for better visualization
        trips_df = performance_df[['City', 'Trips_Target', 'Trips_Actual', 'Trips_Diff%', 'Trips_Status']]
        passengers_df = performance_df[['City', 'NewPass_Target', 'NewPass_Actual', 'NewPass_Diff%', 'NewPass_Status']]
        ratings_df = performance_df[['City', 'Rating_Target', 'Rating_Actual', 'Rating_Diff%', 'Rating_Status']]
        
        # Display dataframes in tabs
        tab1, tab2, tab3 = st.tabs(['Trips', 'New Passengers', 'Ratings'])
        
        with tab1:
            st.write("### Trips Performance")
            st.dataframe(trips_df, use_container_width=True)
            
        with tab2:
            st.write("### New Passengers Performance")
            st.dataframe(passengers_df, use_container_width=True)
            
        with tab3:
            st.write("### Ratings Performance")
            st.dataframe(ratings_df, use_container_width=True)

    @staticmethod
    def show_insights():
        """Display key insights from the performance data."""
        st.subheader("Key Performance Insights")
        
        # Get performance data
        performance_df = TargetAnalysisService.get_performance_data()
        
        # Calculate overall performance
        total_metrics = len(performance_df) * 3  # 3 metrics per city
        status_counts = {
            'Exceeded': sum((performance_df[col] == 'Exceeded').sum() for col in ['Trips_Status', 'NewPass_Status', 'Rating_Status']),
            'Met': sum((performance_df[col] == 'Met').sum() for col in ['Trips_Status', 'NewPass_Status', 'Rating_Status']),
            'Missed': sum((performance_df[col] == 'Missed').sum() for col in ['Trips_Status', 'NewPass_Status', 'Rating_Status'])
        }
        
        # Display overall performance
        st.markdown("### 📊 Overall Performance")
        cols = st.columns(3)
        for i, (status, count) in enumerate(status_counts.items()):
            cols[i].metric(f"{status} Targets", f"{count}/{total_metrics}")
        
        # Calculate and display key metrics
        st.markdown("### 🔑 Key Metrics")
        metrics = ['Trips', 'NewPass', 'Rating']
        for metric in metrics:
            best = performance_df.loc[performance_df[f'{metric}_Diff%'].idxmax()]
            worst = performance_df.loc[performance_df[f'{metric}_Diff%'].idxmin()]
            st.markdown(f"**{metric}:**")
            cols = st.columns(2)
            cols[0].metric("Top Performer", f"{best['City']}", f"{best[f'{metric}_Diff%']:.1f}% above target")
            cols[1].metric("Needs Improvement", f"{worst['City']}", f"{worst[f'{metric}_Diff%']:.1f}% below target")
        
        # Generate insights
        st.markdown("### 🔍 Key Insights")
        best_overall = performance_df.loc[performance_df[['Trips_Diff%', 'NewPass_Diff%', 'Rating_Diff%']].mean(axis=1).idxmax()]
        worst_overall = performance_df.loc[performance_df[['Trips_Diff%', 'NewPass_Diff%', 'Rating_Diff%']].mean(axis=1).idxmin()]
        best_metric = max(metrics, key=lambda m: best_overall[f'{m}_Diff%'])
        worst_metric = min(metrics, key=lambda m: worst_overall[f'{m}_Diff%'])
        
        st.markdown(f"""
        - Top performing city: {best_overall['City']}
        - Strongest metric in top city: {best_metric} ({best_overall[f'{best_metric}_Diff%']:.1f}% above target)
        - City needing most improvement: {worst_overall['City']}
        - Weakest metric in bottom city: {worst_metric} ({worst_overall[f'{worst_metric}_Diff%']:.1f}% below target)
        - City with highest new passenger growth: {performance_df.loc[performance_df['NewPass_Diff%'].idxmax(), 'City']} ({performance_df['NewPass_Diff%'].max():.1f}% above target)
        - City with best customer satisfaction: {performance_df.loc[performance_df['Rating_Diff%'].idxmax(), 'City']} ({performance_df['Rating_Diff%'].max():.1f}% above target)
        """)
        
        # Story telling
        st.markdown("### 📖 Performance Analysis")
        st.markdown(f"""
        My analysis of the performance data reveals:

        1. **Performance Overview**: Out of {total_metrics} total metrics across all cities, {status_counts['Exceeded']} were exceeded, {status_counts['Met']} were met, and {status_counts['Missed']} were missed.
        
        2. **Top Performer**: {best_overall['City']} stands out as the best overall performer, particularly excelling in {best_metric} with a {best_overall[f'{best_metric}_Diff%']:.1f}% improvement above the target.
        
        3. **Growth Leader**: {performance_df.loc[performance_df['NewPass_Diff%'].idxmax(), 'City']} is leading in new passenger acquisition, achieving {performance_df['NewPass_Diff%'].max():.1f}% above the target, indicating strong market expansion.
        
        4. **Customer Satisfaction Champion**: {performance_df.loc[performance_df['Rating_Diff%'].idxmax(), 'City']} is excelling in customer satisfaction, with ratings {performance_df['Rating_Diff%'].max():.1f}% above the target.
        
        5. **Improvement Opportunity**: {worst_overall['City']} shows the most room for improvement, particularly in {worst_metric}, where it's {abs(worst_overall[f'{worst_metric}_Diff%']):.1f}% below the target.

        These insights suggest a need for tailored strategies to capitalize on strengths and address challenges in each city.
        """)
