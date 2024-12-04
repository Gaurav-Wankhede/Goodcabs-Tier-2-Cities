import pandas as pd
from config.__init__ import DataPaths
import streamlit as st
import altair as alt
from typing import Dict, List
import numpy as np

class RPRAnalysisService:
    @staticmethod
    def analyze_rpr():
        """
        Analyze Repeat Passenger Rate (RPR%) by city and month.
        Returns detailed metrics for both city and monthly analysis.
        """
        try:
            fact_passenger = pd.read_csv(DataPaths.FACT_PASSENGER_SUMMARY)
            dim_city = pd.read_csv(DataPaths.DIM_CITY)
            dim_date = pd.read_csv(DataPaths.DIM_DATE)

            fact_passenger['RPR%'] = (fact_passenger['repeat_passengers'] / 
                                    fact_passenger['total_passengers'] * 100).round(2)

            city_rpr = fact_passenger.groupby('city_id')['RPR%'].mean().round(2).reset_index()
            city_rpr = city_rpr.merge(dim_city[['city_id', 'city_name']], on='city_id')
            city_rpr_sorted = city_rpr.sort_values('RPR%', ascending=False).reset_index(drop=True)

            city_metrics = fact_passenger.groupby('city_id').agg({
                'RPR%': 'mean',
                'total_passengers': 'sum',
                'repeat_passengers': 'sum'
            }).round(2).reset_index()
            city_metrics = city_metrics.merge(dim_city[['city_id', 'city_name']], on='city_id')
            city_metrics_sorted = city_metrics.sort_values('RPR%', ascending=False).reset_index(drop=True)

            month_mapping = dim_date[['start_of_month', 'month_name']].drop_duplicates()
            fact_passenger = fact_passenger.merge(month_mapping, 
                                                left_on='month', 
                                                right_on='start_of_month')
            
            monthly_rpr = fact_passenger.groupby(['month', 'month_name']).agg({
                'RPR%': 'mean',
                'total_passengers': 'sum',
                'repeat_passengers': 'sum'
            }).round(2).reset_index()
            monthly_rpr_sorted = monthly_rpr.sort_values('RPR%', ascending=False).reset_index(drop=True)

            analysis_results = {
                "city_analysis": {
                    "top_performers": [
                        {
                            "city": row['city_name'],
                            "rpr_percentage": float(row['RPR%']),
                            "total_passengers": int(row['total_passengers']),
                            "repeat_passengers": int(row['repeat_passengers'])
                        }
                        for _, row in city_metrics_sorted.head(2).iterrows()
                    ],
                    "bottom_performers": [
                        {
                            "city": row['city_name'],
                            "rpr_percentage": float(row['RPR%']),
                            "total_passengers": int(row['total_passengers']),
                            "repeat_passengers": int(row['repeat_passengers'])
                        }
                        for _, row in city_metrics_sorted.tail(2).iterrows()
                    ],
                    "all_cities": [
                        {
                            "city": row['city_name'],
                            "rpr_percentage": float(row['RPR%']),
                            "total_passengers": int(row['total_passengers']),
                            "repeat_passengers": int(row['repeat_passengers'])
                        }
                        for _, row in city_metrics_sorted.iterrows()
                    ]
                },
                "monthly_analysis": {
                    "highest_month": {
                        "month": monthly_rpr_sorted.iloc[0]['month_name'],
                        "rpr_percentage": float(monthly_rpr_sorted.iloc[0]['RPR%']),
                        "total_passengers": int(monthly_rpr_sorted.iloc[0]['total_passengers']),
                        "repeat_passengers": int(monthly_rpr_sorted.iloc[0]['repeat_passengers'])
                    },
                    "lowest_month": {
                        "month": monthly_rpr_sorted.iloc[-1]['month_name'],
                        "rpr_percentage": float(monthly_rpr_sorted.iloc[-1]['RPR%']),
                        "total_passengers": int(monthly_rpr_sorted.iloc[-1]['total_passengers']),
                        "repeat_passengers": int(monthly_rpr_sorted.iloc[-1]['repeat_passengers'])
                    },
                    "all_months": [
                        {
                            "month": row['month_name'],
                            "rpr_percentage": float(row['RPR%']),
                            "total_passengers": int(row['total_passengers']),
                            "repeat_passengers": int(row['repeat_passengers'])
                        }
                        for _, row in monthly_rpr_sorted.iterrows()
                    ]
                },
                "overall_statistics": {
                    "system_average_rpr": float(fact_passenger['RPR%'].mean().round(2)),
                    "total_repeat_passengers": int(fact_passenger['repeat_passengers'].sum()),
                    "total_passengers": int(fact_passenger['total_passengers'].sum()),
                    "overall_rpr": float((fact_passenger['repeat_passengers'].sum() / 
                                       fact_passenger['total_passengers'].sum() * 100).round(2))
                }
            }

            return analysis_results

        except Exception as e:
            raise Exception(f"Error analyzing RPR metrics: {str(e)}")

    @staticmethod
    def get_rpr_data():
        """Get RPR (Repeat Passenger Rate) data for all cities."""
        fact_passenger = pd.read_csv(DataPaths.FACT_PASSENGER_SUMMARY)
        dim_city = pd.read_csv(DataPaths.DIM_CITY)

        fact_passenger['RPR%'] = (fact_passenger['repeat_passengers'] / fact_passenger['total_passengers'] * 100).round(2)

        city_rpr = fact_passenger.groupby('city_id')['RPR%'].mean().round(2).reset_index()

        city_rpr = city_rpr.merge(dim_city[['city_id', 'city_name']], on='city_id')

        return city_rpr.sort_values('RPR%', ascending=False).reset_index(drop=True)

    @staticmethod
    def show_charts():
        """Display RPR analysis charts using Altair."""
        st.subheader("Repeat Passenger Rate (RPR%) Analysis")
        
        city_rpr_sorted = RPRAnalysisService.get_rpr_data()
        
        def create_chart(data, title):
            base = alt.Chart(data).encode(
                x=alt.X('city_name:N', title='City', sort=None),
                y=alt.Y('RPR%:Q', title='RPR%', scale=alt.Scale(domain=[0, max(data['RPR%']) + 5]))
            ).properties(width=400, height=300)
            
            bars = base.mark_bar().encode(
                color=alt.Color('RPR%:Q', scale=alt.Scale(scheme='redyellowgreen'), legend=None),
                tooltip=[alt.Tooltip('city_name:N', title='City'), alt.Tooltip('RPR%:Q', title='RPR%', format='.2f')]
            )
            
            text = base.mark_text(align='center', baseline='bottom', dy=-5, color='white').encode(
                text=alt.Text('RPR%:Q', format='.1f')
            )
            
            return alt.layer(bars, text).properties(title=title).configure_view(
                strokeWidth=0
            ).configure_axis(
                labelColor='white', titleColor='white', gridColor='#444444', labelAngle=45
            ).configure_title(color='white')
        
        col1, col2 = st.columns(2)
        
        with col1:
            top_5_chart = create_chart(city_rpr_sorted.head(), 'Top 5 Cities by RPR%')
            st.altair_chart(top_5_chart, use_container_width=True)
        
        with col2:
            bottom_5_chart = create_chart(city_rpr_sorted.tail(), 'Bottom 5 Cities by RPR%')
            st.altair_chart(bottom_5_chart, use_container_width=True)

    @staticmethod
    def show_dataframes():
        """Display RPR analysis data in tabular format."""
        st.subheader("RPR Performance Data")
        
        city_rpr_sorted = RPRAnalysisService.get_rpr_data()
        
        st.write("### Repeat Passenger Rate (RPR%) by City")
        st.dataframe(
            city_rpr_sorted[['city_name', 'RPR%']].rename(columns={'city_name': 'City'}),
            use_container_width=True
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Top 2 Cities by RPR%")
            st.dataframe(
                city_rpr_sorted.head(2)[['city_name', 'RPR%']].rename(columns={'city_name': 'City'}),
                use_container_width=True
            )
        
        with col2:
            st.write("### Bottom 2 Cities by RPR%")
            st.dataframe(
                city_rpr_sorted.tail(2)[['city_name', 'RPR%']].rename(columns={'city_name': 'City'}),
                use_container_width=True
            )

    @staticmethod
    def show_insights():
        """Display key insights from RPR analysis."""
        st.subheader("RPR Analysis Insights")
        
        city_rpr_sorted = RPRAnalysisService.get_rpr_data()
        
        avg_rpr = city_rpr_sorted['RPR%'].mean()
        max_rpr = city_rpr_sorted['RPR%'].max()
        min_rpr = city_rpr_sorted['RPR%'].min()
        rpr_range = max_rpr - min_rpr
        
        st.write("### Key Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Average RPR%", f"{avg_rpr:.2f}%")
        col2.metric("Highest RPR%", f"{max_rpr:.2f}%")
        col3.metric("Lowest RPR%", f"{min_rpr:.2f}%")
        
        st.write("### Key Insights")
        top_city = city_rpr_sorted.iloc[0]
        bottom_city = city_rpr_sorted.iloc[-1]
        above_avg = city_rpr_sorted[city_rpr_sorted['RPR%'] > avg_rpr]
        below_avg = city_rpr_sorted[city_rpr_sorted['RPR%'] < avg_rpr]
        
        st.markdown(f"""
        - 🏆 **Top Performer**: {top_city['city_name']} leads with {top_city['RPR%']:.2f}% RPR
        - 🚀 **Growth Opportunity**: {bottom_city['city_name']} at {bottom_city['RPR%']:.2f}% RPR
        - 📊 **Performance Range**: {rpr_range:.2f}% difference between highest and lowest
        - 📈 **Above Average**: {len(above_avg)} cities exceed the {avg_rpr:.2f}% average
        - 📉 **Below Average**: {len(below_avg)} cities fall below the average
        """)
        
        st.write("### RPR Analysis Summary")
        st.markdown(f"""
        The analysis of Repeat Passenger Rate (RPR) reveals:

        1. **Performance Spectrum**: 
           - Highest: {top_city['city_name']} ({top_city['RPR%']:.2f}%)
           - Lowest: {bottom_city['city_name']} ({bottom_city['RPR%']:.2f}%)
           - Range: {rpr_range:.2f}%

        2. **Average Performance**:
           - Mean RPR: {avg_rpr:.2f}%
           - {len(above_avg)} cities above average
           - {len(below_avg)} cities below average

        3. **Key Observations**:
           - Significant variation in customer retention across cities
           - Opportunities for improvement in lower-performing areas
           - Best practices from top performers could be leveraged

        4. **Strategic Implications**:
           - Targeted approaches needed for below-average cities
           - Potential for knowledge sharing from high-performing cities
           - Focus on enhancing customer experience to boost RPR
        """)