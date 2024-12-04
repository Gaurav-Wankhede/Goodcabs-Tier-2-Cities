import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from config.__init__ import DataPaths

class RatingAnalysisService:
    @staticmethod
    def analyze_city_ratings():
        """
        Analyze ratings by city and passenger type.
        Returns visualizations and detailed rating metrics.
        """
        try:
            # 1. Data Import using configured paths
            trips_df = pd.read_csv(DataPaths.FACT_TRIPS)
            cities_df = pd.read_csv(DataPaths.DIM_CITY)

            # 2. Merge trips with city information
            trips_analysis = trips_df.merge(cities_df, on='city_id')

            # 3. Calculate average ratings by city and passenger type
            rating_metrics = trips_analysis.groupby(['city_name', 'passenger_type']).agg({
                'passenger_rating': 'mean',
                'driver_rating': 'mean'
            }).round(2)

            # Reset index for easier manipulation
            rating_metrics = rating_metrics.reset_index()

            # 4. Calculate overall city ratings
            city_overall = rating_metrics.groupby('city_name').agg({
                'passenger_rating': 'mean',
                'driver_rating': 'mean'
            }).round(2)

            # 5. Generate Heatmap Visualization
            plt.style.use('dark_background')
            plt.figure(figsize=(12, 6), facecolor='#2e2e2e')
            
            rating_comparison = rating_metrics.pivot(
                index='city_name',
                columns='passenger_type',
                values='passenger_rating'
            )
            
            sns.heatmap(
                rating_comparison, 
                annot=True, 
                cmap='RdYlGn', 
                center=7, 
                vmin=0, 
                vmax=10,
                fmt='.2f'
            )
            
            plt.title('Passenger Ratings by City and Passenger Type', color='white', pad=20)
            plt.xlabel('Passenger Type', color='white', labelpad=10)
            plt.ylabel('City', color='white', labelpad=10)
            
            # Customize tick colors
            plt.tick_params(colors='white')
            
            plt.tight_layout()

            # Save plot to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf.seek(0)
            plot_base64 = base64.b64encode(buf.getvalue()).decode()
            plt.close()

            # 6. Create detailed ratings table with pivot
            detailed_ratings = rating_metrics.pivot(
                index='city_name',
                columns='passenger_type',
                values=['passenger_rating', 'driver_rating']
            )
            detailed_ratings.columns = [f'{col[1]}_{col[0]}' for col in detailed_ratings.columns]

            # 7. Prepare Analysis Results
            analysis_results = {
                "visualization": {
                    "plot": plot_base64,
                    "type": "image/png",
                    "encoding": "base64"
                },
                "detailed_ratings": detailed_ratings.round(2).to_dict('index'),
                "city_rankings": {
                    "top_rated_cities": {
                        "by_passenger_rating": city_overall.nlargest(3, 'passenger_rating')[
                            ['passenger_rating']
                        ].round(2).to_dict('index'),
                        "by_driver_rating": city_overall.nlargest(3, 'driver_rating')[
                            ['driver_rating']
                        ].round(2).to_dict('index')
                    },
                    "bottom_rated_cities": {
                        "by_passenger_rating": city_overall.nsmallest(3, 'passenger_rating')[
                            ['passenger_rating']
                        ].round(2).to_dict('index'),
                        "by_driver_rating": city_overall.nsmallest(3, 'driver_rating')[
                            ['driver_rating']
                        ].round(2).to_dict('index')
                    }
                },
                "summary_statistics": {
                    "overall_average_ratings": {
                        "passenger_rating": float(trips_analysis['passenger_rating'].mean().round(2)),
                        "driver_rating": float(trips_analysis['driver_rating'].mean().round(2))
                    },
                    "rating_by_passenger_type": rating_metrics.groupby('passenger_type').agg({
                        'passenger_rating': 'mean',
                        'driver_rating': 'mean'
                    }).round(2).to_dict('index'),
                    "rating_ranges": {
                        "passenger_rating": {
                            "min": float(trips_analysis['passenger_rating'].min()),
                            "max": float(trips_analysis['passenger_rating'].max())
                        },
                        "driver_rating": {
                            "min": float(trips_analysis['driver_rating'].min()),
                            "max": float(trips_analysis['driver_rating'].max())
                        }
                    }
                }
            }

            return analysis_results

        except Exception as e:
            raise Exception(f"Error analyzing city ratings: {str(e)}")
