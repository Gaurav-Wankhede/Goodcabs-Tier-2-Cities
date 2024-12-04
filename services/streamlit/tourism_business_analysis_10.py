import pandas as pd
import streamlit as st
import altair as alt
from config.__init__ import DataPaths

class TourismBusinessAnalysisService:
    @staticmethod
    @st.cache_data
    def get_tourism_data():
        """Get tourism and business analysis data."""
        fact_trips = pd.read_csv(DataPaths.FACT_TRIPS)
        dim_date = pd.read_csv(DataPaths.DIM_DATE)
        dim_city = pd.read_csv(DataPaths.DIM_CITY)
        fact_passenger = pd.read_csv(DataPaths.FACT_PASSENGER_SUMMARY)

        trips_analysis = fact_trips.merge(dim_date[['date', 'month_name', 'day_type']], on='date')
        trips_analysis = trips_analysis.merge(dim_city[['city_id', 'city_name']], on='city_id')

        day_type_analysis = trips_analysis.groupby(['city_name', 'day_type']).agg({
            'trip_id': 'count',
            'passenger_type': lambda x: (x == 'new').mean() * 100
        }).round(2).reset_index()

        day_type_analysis.columns = ['city_name', 'day_type', 'total_trips', 'new_passenger_percent']

        weekend_weekday_ratio = day_type_analysis.pivot(index='city_name', 
                                                      columns='day_type', 
                                                      values='total_trips').reset_index()
        weekend_weekday_ratio = weekend_weekday_ratio.fillna(0)
        weekend_weekday_ratio['Weekend_Weekday_Ratio'] = weekend_weekday_ratio.apply(
            lambda row: (row['Weekend'] / row['Weekday']) if row['Weekday'] > 0 else 0,
            axis=1
        ).round(2)

        monthly_city = fact_passenger.merge(dim_city[['city_id', 'city_name']], on='city_id')
        monthly_city['new_passenger_ratio'] = (monthly_city['new_passengers'] / 
                                             monthly_city['total_passengers'] * 100).round(2)

        peak_months = monthly_city.sort_values('new_passenger_ratio', ascending=False).groupby('city_name').first()

        return day_type_analysis, weekend_weekday_ratio, monthly_city, peak_months

    @staticmethod
    @st.cache_data
    def show_charts():
        """Display tourism and business analysis charts."""
        st.subheader("Tourism vs Business Analysis")
        
        day_type_analysis, weekend_weekday_ratio, monthly_city, _ = TourismBusinessAnalysisService.get_tourism_data()
        
        if weekend_weekday_ratio.empty or 'Weekend_Weekday_Ratio' not in weekend_weekday_ratio.columns:
            st.error("Insufficient data for Weekend to Weekday Ratio analysis.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            ratio_data = weekend_weekday_ratio.sort_values('Weekend_Weekday_Ratio', ascending=False)
            
            base = alt.Chart(ratio_data).encode(
                x=alt.X('city_name:N', sort='-y', title='City', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Weekend_Weekday_Ratio:Q', title='Weekend/Weekday Ratio')
            ).properties(
                width=300,
                height=400,
                title='Tourism vs Business Pattern by City'
            )
            
            bars = base.mark_bar().encode(
                color=alt.condition(
                    alt.datum.Weekend_Weekday_Ratio > 1,
                    alt.value('#00FF00'),
                    alt.value('#FF4500')
                ),
                tooltip=['city_name', alt.Tooltip('Weekend_Weekday_Ratio:Q', format='.2f')]
            )
            
            rule = base.mark_rule(strokeDash=[2, 2], color='white').encode(
                y='a:Q'
            ).transform_calculate(a="1")
            
            text = base.mark_text(
                align='center',
                baseline='bottom',
                dy=-5,
                color='white'
            ).encode(
                text=alt.Text('Weekend_Weekday_Ratio:Q', format='.2f')
            )
            
            chart = (bars + rule + text).configure_view(
                strokeWidth=0
            ).configure_axis(
                labelColor='white',
                titleColor='white',
                gridColor='#444444'
            ).configure_title(
                color='white'
            )
            
            st.altair_chart(chart, use_container_width=True)
        
        with col2:
            if day_type_analysis.empty or 'new_passenger_percent' not in day_type_analysis.columns:
                st.error("Insufficient data for New Passenger Distribution analysis.")
                return
            
            heatmap = alt.Chart(day_type_analysis).mark_rect().encode(
                x=alt.X('day_type:N', title='Day Type'),
                y=alt.Y('city_name:N', title='City'),
                color=alt.Color('new_passenger_percent:Q', 
                              scale=alt.Scale(scheme='yelloworangered'),
                              title='New Passenger %'),
                tooltip=['city_name', 'day_type', 
                        alt.Tooltip('new_passenger_percent:Q', title='New Passenger %', format='.1f')]
            ).properties(
                width=300,
                height=400,
                title='New Passenger Distribution'
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
    @st.cache_data
    def show_dataframes():
        """Display tourism and business analysis data."""
        st.subheader("Tourism vs Business Analysis Data")
        
        day_type_analysis, weekend_weekday_ratio, _, peak_months = TourismBusinessAnalysisService.get_tourism_data()
        
        st.write("### Weekday vs Weekend Patterns by City")
        st.dataframe(
            day_type_analysis.style.format({
                'total_trips': '{:,.0f}',
                'new_passenger_percent': '{:.1f}%'
            }),
            use_container_width=True
        )
        
        st.write("### Weekend to Weekday Ratio by City")
        ratio_display = weekend_weekday_ratio.sort_values('Weekend_Weekday_Ratio', ascending=False)
        st.dataframe(
            ratio_display.style.format({
                'Weekend': '{:,.0f}',
                'Weekday': '{:,.0f}',
                'Weekend_Weekday_Ratio': '{:.2f}'
            }),
            use_container_width=True
        )
        
        st.write("### Peak Months for New Passengers by City")
        st.dataframe(
            peak_months[['month', 'new_passenger_ratio']].sort_values('new_passenger_ratio', ascending=False)
            .style.format({'new_passenger_ratio': '{:.1f}%'}),
            use_container_width=True
        )

    @staticmethod
    @st.cache_data
    def show_insights():
        """Display key insights from tourism and business analysis."""
        st.subheader("Tourism vs Business Analysis Insights")
        
        _, weekend_weekday_ratio, _, peak_months = TourismBusinessAnalysisService.get_tourism_data()
        
        tourism_cities = weekend_weekday_ratio[weekend_weekday_ratio['Weekend_Weekday_Ratio'] > 1]
        business_cities = weekend_weekday_ratio[weekend_weekday_ratio['Weekend_Weekday_Ratio'] <= 1]
        
        # Key Metrics
        avg_ratio = weekend_weekday_ratio['Weekend_Weekday_Ratio'].mean()
        max_tourism_ratio = tourism_cities['Weekend_Weekday_Ratio'].max()
        min_business_ratio = business_cities['Weekend_Weekday_Ratio'].min()
        
        st.write("### 📊 Key Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Tourism-Heavy Cities", len(tourism_cities))
        col2.metric("Business-Heavy Cities", len(business_cities))
        col3.metric("Avg Weekend/Weekday Ratio", f"{avg_ratio:.2f}")
        
        with col1:
            st.write("### 📈 Analysis Highlights")
            st.write(f"""
            - Total cities analyzed: {len(weekend_weekday_ratio)}
            - Tourism-leaning cities: {len(tourism_cities)}
            - Business-oriented cities: {len(business_cities)}
            - Average weekend-to-weekday ratio: {avg_ratio:.2f}
            - Highest tourism ratio: {max_tourism_ratio:.2f}
            - Lowest business ratio: {min_business_ratio:.2f}
            """)

        st.write("### 🏆 Notable Cities")
        top_tourism = tourism_cities.nlargest(3, 'Weekend_Weekday_Ratio')
        top_business = business_cities.nsmallest(3, 'Weekend_Weekday_Ratio')
        
        with col2:
            st.write("#### Top Tourism-Heavy Cities:")
            for _, city in top_tourism.iterrows():
                st.write(f"- {city['city_name']}: {city['Weekend_Weekday_Ratio']:.2f} ratio")
        with col3:
            st.write("#### Top Business-Heavy Cities:")
            for _, city in top_business.iterrows():
                st.write(f"- {city['city_name']}: {city['Weekend_Weekday_Ratio']:.2f} ratio")

        
        
        
        
        st.write("### 📅 Peak Month Insights")
        st.write("Peak months for new passenger acquisition by city:")
        for city_name, data in peak_months.iterrows():
            st.write(f"- {city_name}: Peaks in {data['month']} with {data['new_passenger_ratio']:.1f}% new passengers")
        
        st.write("### 🔍 Key Takeaways")
        st.write("""
        - Clear distinction between tourism-heavy and business-oriented cities
        - Weekend-to-weekday ratio serves as a key indicator for city classification
        - Significant variation in peak months for new passenger acquisition across cities
        - Insights suggest potential for tailored strategies in service provision and marketing
        """)
