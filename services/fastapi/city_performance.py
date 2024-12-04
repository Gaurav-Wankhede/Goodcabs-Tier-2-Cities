import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from config.__init__ import DataPaths

class CityPerformanceService:
    @staticmethod
    def analyze_top_bottom_cities():
        """
        Analyze top and bottom performing cities based on total trips.
        Returns visualization and detailed statistics.
        """
        try:
            # 1. Data Import using configured paths
            fact_trips = pd.read_csv(DataPaths.FACT_TRIPS)
            dim_city = pd.read_csv(DataPaths.DIM_CITY)

            # 2. Data Preparation
            city_trip_summary = fact_trips.groupby('city_id').size().reset_index(name='total_trips')
            city_trip_summary = city_trip_summary.merge(dim_city[['city_id', 'city_name']], on='city_id')

            # 3. Top and Bottom Cities Analysis
            city_trip_summary_sorted = city_trip_summary.sort_values('total_trips', ascending=False)
            total_trips = city_trip_summary_sorted['total_trips'].sum()

            top_3_cities = city_trip_summary_sorted.head(3).copy()
            bottom_3_cities = city_trip_summary_sorted.tail(3).copy()

            top_3_cities['trip_percentage'] = (top_3_cities['total_trips'] / total_trips * 100).round(2)
            bottom_3_cities['trip_percentage'] = (bottom_3_cities['total_trips'] / total_trips * 100).round(2)

            # 4. Generate Visualization
            plt.style.use('dark_background')
            sns.set_style("darkgrid")
            
            plt.figure(figsize=(15, 6), facecolor='#2e2e2e')

            # Bar plot for Top Cities
            plt.subplot(1, 2, 1)
            bars1 = sns.barplot(x='city_name', y='total_trips', data=top_3_cities, palette='magma', hue='city_name')
            plt.title('Top 3 Cities by Total Trips', fontsize=12, color='white', pad=15)
            plt.xticks(rotation=45, color='white')
            plt.yticks(color='white')
            plt.xlabel('City Name', color='white', labelpad=10)
            plt.ylabel('Total Trips', color='white', labelpad=10)

            # Add value labels on bars
            for i, bar in enumerate(bars1.patches):
                bars1.text(bar.get_x() + bar.get_width()/2., 
                        bar.get_height(), 
                        f'{int(bar.get_height()):,}', 
                        ha='center', va='bottom', color='white')

            # Bar plot for Bottom Cities
            plt.subplot(1, 2, 2)
            bars2 = sns.barplot(x='city_name', y='total_trips', data=bottom_3_cities, palette='magma', hue='city_name')
            plt.title('Bottom 3 Cities by Total Trips', fontsize=12, color='white', pad=15)
            plt.xticks(rotation=45, color='white')
            plt.yticks(color='white')
            plt.xlabel('City Name', color='white', labelpad=10)
            plt.ylabel('Total Trips', color='white', labelpad=10)

            # Add value labels on bars
            for i, bar in enumerate(bars2.patches):
                bars2.text(bar.get_x() + bar.get_width()/2., 
                        bar.get_height(), 
                        f'{int(bar.get_height()):,}', 
                        ha='center', va='bottom', color='white')

            plt.tight_layout()
            
            # Save plot to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf.seek(0)
            plot_base64 = base64.b64encode(buf.getvalue()).decode()
            plt.close()

            # 5. Prepare Analysis Results
            analysis_results = {
                "visualization": {
                    "plot": plot_base64,
                    "type": "image/png",
                    "encoding": "base64"
                },
                "top_cities": {
                    "data": top_3_cities[['city_name', 'total_trips', 'trip_percentage']].to_dict('records'),
                    "total_trips": int(top_3_cities['total_trips'].sum()),
                    "total_percentage": float(top_3_cities['trip_percentage'].sum())
                },
                "bottom_cities": {
                    "data": bottom_3_cities[['city_name', 'total_trips', 'trip_percentage']].to_dict('records'),
                    "total_trips": int(bottom_3_cities['total_trips'].sum()),
                    "total_percentage": float(bottom_3_cities['trip_percentage'].sum())
                },
                "overall_statistics": {
                    "total_trips_all_cities": int(total_trips),
                    "average_trips_per_city": float(total_trips / len(city_trip_summary)),
                    "total_cities_analyzed": len(city_trip_summary)
                }
            }
            
            return analysis_results

        except Exception as e:
            raise Exception(f"Error analyzing city performance: {str(e)}")
