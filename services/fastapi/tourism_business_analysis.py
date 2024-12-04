import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import numpy as np
from datetime import datetime
from config.__init__ import DataPaths

class TourismBusinessAnalysisService:
    @staticmethod
    def analyze_tourism_business_patterns():
        """
        Analyze tourism vs. business demand patterns across cities,
        including weekend/weekday ratios and seasonal patterns.
        """
        try:
            # 1. Data Import
            fact_trips = pd.read_csv(DataPaths.FACT_TRIPS)
            dim_date = pd.read_csv(DataPaths.DIM_DATE)
            dim_city = pd.read_csv(DataPaths.DIM_CITY)
            fact_passenger = pd.read_csv(DataPaths.FACT_PASSENGER_SUMMARY)

            # Add month number to dim_date
            dim_date['month_number'] = pd.to_datetime(dim_date['date']).dt.month

            # 2. Merge data for analysis
            trips_analysis = fact_trips.merge(
                dim_date[['date', 'month_name', 'day_type', 'month_number']], 
                on='date'
            )
            trips_analysis = trips_analysis.merge(
                dim_city[['city_id', 'city_name']], 
                on='city_id'
            )

            # 3. Day Type Analysis
            day_type_analysis = trips_analysis.groupby(
                ['city_name', 'day_type']
            ).agg({
                'trip_id': 'count',
                'passenger_type': lambda x: (x == 'new').mean() * 100,
                'fare_amount': 'mean',
                'distance_travelled(km)': 'mean'
            }).round(2).reset_index()

            # Calculate weekend to weekday ratios
            weekend_weekday = day_type_analysis.pivot(
                index='city_name',
                columns='day_type',
                values=['trip_id', 'passenger_type', 'fare_amount', 'distance_travelled(km)']
            ).reset_index()

            # Flatten column names
            weekend_weekday.columns = ['city_name'] + [
                f'{col[0]}_{col[1]}'.lower() 
                for col in weekend_weekday.columns[1:]
            ]

            # Calculate ratios
            weekend_weekday['trip_ratio'] = (
                weekend_weekday['trip_id_weekend'] / 
                weekend_weekday['trip_id_weekday']
            ).round(2)
            weekend_weekday['new_passenger_ratio'] = (
                weekend_weekday['passenger_type_weekend'] / 
                weekend_weekday['passenger_type_weekday']
            ).round(2)
            weekend_weekday['fare_ratio'] = (
                weekend_weekday['fare_amount_weekend'] / 
                weekend_weekday['fare_amount_weekday']
            ).round(2)
            weekend_weekday['distance_ratio'] = (
                weekend_weekday['distance_travelled(km)_weekend'] / 
                weekend_weekday['distance_travelled(km)_weekday']
            ).round(2)

            # 4. Monthly Pattern Analysis
            monthly_analysis = fact_passenger.merge(
                dim_city[['city_id', 'city_name']], 
                on='city_id'
            )
            
            # Extract month number from the month column
            monthly_analysis['month_number'] = pd.to_datetime(monthly_analysis['month']).dt.month
            
            monthly_analysis['new_passenger_ratio'] = (
                monthly_analysis['new_passengers'] / 
                monthly_analysis['total_passengers'] * 100
            ).round(2)

            # Get peak months and seasonal patterns
            peak_months = monthly_analysis.sort_values(
                'new_passenger_ratio', 
                ascending=False
            ).groupby('city_name').first()

            # Calculate seasonal indices using month number
            monthly_patterns = monthly_analysis.pivot_table(
                index='city_name',
                columns='month_number',
                values='new_passenger_ratio',
                aggfunc='mean'
            ).round(2)

            # Fill any missing months with 0
            for month in range(1, 13):
                if month not in monthly_patterns.columns:
                    monthly_patterns[month] = 0
            monthly_patterns = monthly_patterns.reindex(sorted(monthly_patterns.columns), axis=1)

            # 5. Generate Visualizations
            plt.style.use('dark_background')

            # Weekend/Weekday Ratio Plot
            fig1, ax1 = plt.subplots(figsize=(12, 6), facecolor='#2e2e2e')
            ratio_data = weekend_weekday.sort_values('trip_ratio', ascending=False)
            
            bars = ax1.bar(ratio_data['city_name'], ratio_data['trip_ratio'])
            ax1.axhline(y=1, color='r', linestyle='--', alpha=0.5)

            # Color bars based on tourism indication
            for bar in bars:
                if bar.get_height() > 1:
                    bar.set_color('green')
                else:
                    bar.set_color('red')

            ax1.set_title('Weekend to Weekday Trip Ratio by City\n' +
                         '(Green: Tourism-Heavy, Red: Business-Heavy)', 
                         pad=20)
            ax1.set_xlabel('City')
            ax1.set_ylabel('Weekend/Weekday Ratio')
            plt.xticks(rotation=45, ha='right')

            # Add value labels
            for i, v in enumerate(ratio_data['trip_ratio']):
                ax1.text(i, v, f'{v:.2f}', ha='center', va='bottom')

            plt.tight_layout()

            # Save ratio plot
            buf1 = io.BytesIO()
            fig1.savefig(buf1, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf1.seek(0)
            ratio_plot = base64.b64encode(buf1.getvalue()).decode()
            plt.close(fig1)

            # Monthly Pattern Heatmap
            fig2, ax2 = plt.subplots(figsize=(15, 8), facecolor='#2e2e2e')
            
            sns.heatmap(monthly_patterns,
                       cmap='RdYlGn',
                       center=monthly_patterns.mean().mean(),
                       annot=True,
                       fmt='.1f',
                       ax=ax2)
            
            ax2.set_title('Monthly New Passenger Patterns by City\n' +
                         '(Higher values indicate potential tourist seasons)',
                         pad=20)
            # Set month names for x-axis
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            ax2.set_xticklabels(month_names, rotation=45)
            
            plt.tight_layout()

            # Save heatmap
            buf2 = io.BytesIO()
            fig2.savefig(buf2, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf2.seek(0)
            heatmap_plot = base64.b64encode(buf2.getvalue()).decode()
            plt.close(fig2)

            # 6. Classify Cities
            tourism_threshold = 1.1  # 10% higher weekend activity
            city_classifications = []
            
            for _, city in weekend_weekday.iterrows():
                peak_month = peak_months.loc[city['city_name']]['month_number']
                classification = {
                    "city": city['city_name'],
                    "classification": "Tourism-Heavy" if city['trip_ratio'] > tourism_threshold else "Business-Heavy",
                    "metrics": {
                        "weekend_weekday_ratio": float(city['trip_ratio']),
                        "new_passenger_ratio": float(city['new_passenger_ratio']),
                        "fare_ratio": float(city['fare_ratio']),
                        "distance_ratio": float(city['distance_ratio'])
                    },
                    "peak_month": int(peak_month),
                    "peak_new_passenger_ratio": float(peak_months.loc[city['city_name']]['new_passenger_ratio'])
                }
                city_classifications.append(classification)

            # 7. Prepare Analysis Results
            analysis_results = {
                "visualizations": {
                    "weekend_weekday_ratio": {
                        "plot": ratio_plot,
                        "type": "image/png",
                        "encoding": "base64"
                    },
                    "monthly_patterns": {
                        "plot": heatmap_plot,
                        "type": "image/png",
                        "encoding": "base64"
                    }
                },
                "city_classifications": city_classifications,
                "tourism_metrics": {
                    "tourism_heavy_cities": len([
                        c for c in city_classifications 
                        if c['classification'] == "Tourism-Heavy"
                    ]),
                    "business_heavy_cities": len([
                        c for c in city_classifications 
                        if c['classification'] == "Business-Heavy"
                    ]),
                    "highest_weekend_ratio": {
                        "city": weekend_weekday.iloc[
                            weekend_weekday['trip_ratio'].argmax()
                        ]['city_name'],
                        "ratio": float(weekend_weekday['trip_ratio'].max())
                    },
                    "lowest_weekend_ratio": {
                        "city": weekend_weekday.iloc[
                            weekend_weekday['trip_ratio'].argmin()
                        ]['city_name'],
                        "ratio": float(weekend_weekday['trip_ratio'].min())
                    }
                },
                "seasonal_insights": {
                    "peak_months": [
                        {
                            "city": city,
                            "peak_month": int(data['month_number']),
                            "new_passenger_ratio": float(data['new_passenger_ratio'])
                        }
                        for city, data in peak_months.iterrows()
                    ],
                    "monthly_patterns": {
                        str(i): values.to_dict() 
                        for i, values in monthly_patterns.items()
                    }
                },
                "marketing_recommendations": {
                    "tourism_focused": [
                        city['city'] for city in city_classifications
                        if city['classification'] == "Tourism-Heavy"
                    ],
                    "business_focused": [
                        city['city'] for city in city_classifications
                        if city['classification'] == "Business-Heavy"
                    ]
                }
            }

            return analysis_results

        except Exception as e:
            raise Exception(f"Error analyzing tourism vs business patterns: {str(e)}")
