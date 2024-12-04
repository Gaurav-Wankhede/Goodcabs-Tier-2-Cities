import pandas as pd
import altair as alt
import streamlit as st
from config.__init__ import DataPaths

class DayTypeAnalysisService:
    @staticmethod
    @st.cache_data
    def analyze_day_types():
        """
        Analyze patterns between weekdays and weekends
        """
        try:
            # Load data
            fact_trips = pd.read_csv(DataPaths.FACT_TRIPS)
            dim_city = pd.read_csv(DataPaths.DIM_CITY)
            dim_date = pd.read_csv(DataPaths.DIM_DATE)

            # Merge data
            trips_analysis = fact_trips.merge(dim_city, on='city_id').merge(dim_date[['date', 'day_type']], on='date')

            # Calculate trips by city and day type
            day_type_analysis = trips_analysis.groupby(['city_name', 'day_type'])['trip_id'].count().reset_index()
            day_type_pivot = day_type_analysis.pivot(index='city_name', columns='day_type', values='trip_id')
            day_type_pivot['Total'] = day_type_pivot['Weekday'] + day_type_pivot['Weekend']
            day_type_pivot['Weekday_Ratio'] = (day_type_pivot['Weekday'] / day_type_pivot['Total'] * 100).round(2)
            day_type_pivot['Weekend_Ratio'] = (day_type_pivot['Weekend'] / day_type_pivot['Total'] * 100).round(2)

            return day_type_pivot
        except Exception as e:
            raise Exception(f"Error analyzing day types: {str(e)}")

    @staticmethod
    @st.cache_data
    def show_charts(day_type_pivot):
        # Create visualization using Altair
        day_type_ratios = day_type_pivot.reset_index().melt(id_vars='city_name', value_vars=['Weekday_Ratio', 'Weekend_Ratio'], var_name='Day Type', value_name='Ratio')
        chart = alt.Chart(day_type_ratios).mark_bar().encode(
            x=alt.X('city_name:N', title='Cities', sort=None),
            y=alt.Y('Ratio:Q', title='Percentage of Total Trips'),
            color=alt.Color('Day Type:N', scale=alt.Scale(scheme='goldorange'), title='Day Type'),
            tooltip=['city_name', 'Day Type', 'Ratio']
        ).properties(
            width=600,
            height=400,
            title='Weekday vs Weekend Trip Distribution by City'
        ).configure(background='black')
        st.altair_chart(chart)

    @staticmethod
    @st.cache_data
    def show_dataframes(day_type_pivot):
        # Format the numbers
        formatted_pivot = day_type_pivot.copy()
        formatted_pivot['Weekday'] = formatted_pivot['Weekday'].apply(lambda x: f"{x:,}")
        formatted_pivot['Weekend'] = formatted_pivot['Weekend'].apply(lambda x: f"{x:,}")
        formatted_pivot['Total'] = formatted_pivot['Total'].apply(lambda x: f"{x:,}")
        formatted_pivot['Weekday_Ratio'] = formatted_pivot['Weekday_Ratio'].apply(lambda x: f"{x}%")
        formatted_pivot['Weekend_Ratio'] = formatted_pivot['Weekend_Ratio'].apply(lambda x: f"{x}%")

        # Display results in Streamlit
        st.write("## Trip Distribution by Day Type for Each City")
        st.dataframe(formatted_pivot)

    @staticmethod
    @st.cache_data
    def show_insights(day_type_pivot):
        st.subheader("Day Type Analysis Insights")

        # Key Metrics
        total_cities = len(day_type_pivot)
        weekday_dominant = (day_type_pivot['Weekday_Ratio'] > 50).sum()
        weekend_dominant = total_cities - weekday_dominant

        # Display Key Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Cities Analyzed", total_cities)
        col2.metric("Weekday-Dominant Cities", weekday_dominant)
        col3.metric("Weekend-Dominant Cities", weekend_dominant)

        # Story Telling
        with col1:
            st.write("### 🏙️ City Trip Patterns Story")
            st.write(f"""
            My analysis reveals a diverse landscape of {total_cities} cities, each with its unique 
            weekday-to-weekend trip ratio. I've identified {weekday_dominant} cities that lean towards 
            weekday trips, while {weekend_dominant} cities show a stronger weekend travel trend.
            
            This split provides valuable insights into the varying dynamics of urban mobility across different locations.
            """)

        # Notable Cities
        with col2:
            st.write("### 🏆 Notable Cities")
            max_weekday_city = day_type_pivot['Weekday_Ratio'].idxmax()
            max_weekend_city = day_type_pivot['Weekend_Ratio'].idxmax()
            st.write(f"""
            - **{max_weekday_city}** stands out with the highest weekday trip ratio at {day_type_pivot.loc[max_weekday_city, 'Weekday_Ratio']:.2f}%
            - **{max_weekend_city}** leads in weekend trips with a ratio of {day_type_pivot.loc[max_weekend_city, 'Weekend_Ratio']:.2f}%
            
            These extremes highlight the importance of tailored strategies for different urban environments.
            """)

        # Distribution Analysis
        st.write("### 📊 Trip Distribution Highlights")
        for city, row in day_type_pivot.nlargest(3, 'Weekday_Ratio').iterrows():
            st.write(f"- **{city}**: {row['Weekday_Ratio']:.2f}% weekday, {row['Weekend_Ratio']:.2f}% weekend")
        st.write("...")
        for city, row in day_type_pivot.nlargest(3, 'Weekend_Ratio').iterrows():
            st.write(f"- **{city}**: {row['Weekday_Ratio']:.2f}% weekday, {row['Weekend_Ratio']:.2f}% weekend")

        # Key Takeaways and Recommendations
        st.write("### 💡 Key Takeaways and Recommendations")
        st.write("""
        1. **Tailored Marketing**: Develop city-specific campaigns aligned with dominant trip patterns
        2. **Resource Optimization**: Adjust resource allocation based on weekday vs weekend demand
        3. **Further Investigation**: Explore factors behind extreme day type ratios in certain cities
        4. **Targeted Services**: Design services catering to the specific needs of weekday and weekend travelers
        5. **Continuous Monitoring**: Regularly analyze these patterns to adapt to changing urban dynamics
        """)

    @staticmethod
    @st.cache_data
    def show_overview(view_mode="Charts"):
        """
        Show overview of day type analysis
        """
        try:
            day_type_pivot = DayTypeAnalysisService.analyze_day_types()
            
            if view_mode == "Charts":
                DayTypeAnalysisService.show_charts(day_type_pivot)
            elif view_mode == "Dataframes":
                DayTypeAnalysisService.show_dataframes(day_type_pivot)
            else:
                DayTypeAnalysisService.show_insights(day_type_pivot)
        except Exception as e:
            st.error(f"Error showing day type overview: {str(e)}")
            return None
