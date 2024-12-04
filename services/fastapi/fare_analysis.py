import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from config.__init__ import DataPaths

class FareAnalysisService:
    @staticmethod
    def analyze_city_fares():
        """
        Analyze average fares and distances per city.
        Returns visualization and detailed fare metrics.
        """
        try:
            # 1. Data Import using configured paths
            trips_df = pd.read_csv(DataPaths.FACT_TRIPS)
            cities_df = pd.read_csv(DataPaths.DIM_CITY)

            # 2. Calculate average fare and distance per city
            city_metrics = trips_df.groupby('city_id').agg({
                'fare_amount': 'mean',
                'distance_travelled(km)': 'mean'
            }).reset_index()

            # 3. Merge with city names
            city_metrics = city_metrics.merge(cities_df, on='city_id', how='left')
            city_metrics = city_metrics.sort_values('fare_amount', ascending=False)

            # 4. Calculate fare per kilometer
            city_metrics['fare_per_km'] = (
                city_metrics['fare_amount'] / city_metrics['distance_travelled(km)']
            ).round(2)

            # 5. Generate Visualization
            plt.style.use('dark_background')
            plt.figure(figsize=(12, 8), facecolor='#2e2e2e')
            
            plt.scatter(
                city_metrics['distance_travelled(km)'], 
                city_metrics['fare_amount'],
                color='goldenrod', 
                s=100, 
                alpha=0.6
            )

            # Customize the plot
            plt.xlabel('Average Distance Travelled (km)', color='white', fontsize=12)
            plt.ylabel('Average Fare Amount', color='white', fontsize=12)
            plt.title('Average Fare vs Distance Travelled per City', 
                     color='white', fontsize=14, pad=20)

            # Add city labels
            for i, city in enumerate(city_metrics['city_name']):
                plt.annotate(
                    city,
                    (city_metrics['distance_travelled(km)'].iloc[i], 
                     city_metrics['fare_amount'].iloc[i]),
                    color='white',
                    xytext=(5, 5),
                    textcoords='offset points',
                    fontsize=10
                )

            # Customize grid and spines
            plt.grid(True, linestyle='--', alpha=0.3)
            plt.tick_params(colors='white')
            plt.tight_layout()

            # Save plot to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf.seek(0)
            plot_base64 = base64.b64encode(buf.getvalue()).decode()
            plt.close()

            # 6. Prepare Analysis Results
            analysis_results = {
                "visualization": {
                    "plot": plot_base64,
                    "type": "image/png",
                    "encoding": "base64"
                },
                "city_metrics": city_metrics[[
                    'city_name', 'fare_amount', 'distance_travelled(km)', 'fare_per_km'
                ]].round(2).to_dict('records'),
                "summary_statistics": {
                    "highest_fare": {
                        "city": city_metrics.iloc[0]['city_name'],
                        "amount": float(city_metrics.iloc[0]['fare_amount'].round(2))
                    },
                    "lowest_fare": {
                        "city": city_metrics.iloc[-1]['city_name'],
                        "amount": float(city_metrics.iloc[-1]['fare_amount'].round(2))
                    },
                    "average_fare_all_cities": float(city_metrics['fare_amount'].mean().round(2)),
                    "average_distance_all_cities": float(city_metrics['distance_travelled(km)'].mean().round(2)),
                    "average_fare_per_km_all_cities": float(city_metrics['fare_per_km'].mean().round(2))
                },
                "fare_efficiency_ranking": city_metrics[[
                    'city_name', 'fare_per_km'
                ]].sort_values('fare_per_km', ascending=False).to_dict('records')
            }

            return analysis_results

        except Exception as e:
            raise Exception(f"Error analyzing city fares: {str(e)}")
