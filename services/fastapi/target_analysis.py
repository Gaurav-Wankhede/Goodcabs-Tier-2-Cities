import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
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
    def analyze_target_achievement():
        """
        Analyze monthly target achievement for key metrics across cities.
        Returns visualization and detailed performance metrics.
        """
        try:
            # 1. Data Import using configured paths
            fact_trips = pd.read_csv(DataPaths.FACT_TRIPS)
            fact_passenger = pd.read_csv(DataPaths.FACT_PASSENGER_SUMMARY)
            cities_df = pd.read_csv(DataPaths.DIM_CITY)
            dates_df = pd.read_csv(DataPaths.DIM_DATE)
            target_trips = pd.read_csv(DataPaths.MONTHLY_TARGET_TRIPS)
            target_passengers = pd.read_csv(DataPaths.MONTHLY_TARGET_NEW_PASSENGERS)
            target_ratings = pd.read_csv(DataPaths.CITY_TARGET_PASSENGER_RATING)

            # 2. Calculate actual metrics
            # Monthly trips by city
            actual_trips = fact_trips.groupby(['city_id', 'date'])['trip_id'].count().reset_index()
            actual_trips = actual_trips.merge(dates_df[['date', 'start_of_month']], on='date')
            monthly_trips = actual_trips.groupby(['city_id', 'start_of_month'])['trip_id'].sum().reset_index()

            # Monthly ratings by city
            monthly_ratings = fact_trips.groupby(['city_id', 'date'])['passenger_rating'].mean().reset_index()
            monthly_ratings = monthly_ratings.merge(dates_df[['date', 'start_of_month']], on='date')
            monthly_ratings = monthly_ratings.groupby(['city_id', 'start_of_month'])['passenger_rating'].mean().round(2).reset_index()

            # 3. Compare with targets
            performance_data = []
            for city_id in cities_df['city_id'].unique():
                city_name = cities_df[cities_df['city_id'] == city_id]['city_name'].iloc[0]
                
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
                    'city': city_name,
                    'trips': {
                        'target': int(city_trip_target),
                        'actual': int(avg_trips),
                        'difference_percentage': float(trip_diff),
                        'status': trip_status
                    },
                    'new_passengers': {
                        'target': int(city_passenger_target),
                        'actual': int(avg_new_passengers),
                        'difference_percentage': float(passenger_diff),
                        'status': passenger_status
                    },
                    'rating': {
                        'target': float(round(city_rating_target, 2)),
                        'actual': float(round(avg_rating, 2)),
                        'difference_percentage': float(rating_diff),
                        'status': rating_status
                    }
                })

            # 4. Create performance DataFrame for visualization
            performance_df = pd.DataFrame(performance_data)
            achievement_data = pd.DataFrame({
                'City': [item['city'] for item in performance_data],
                'Trips': [item['trips']['difference_percentage'] for item in performance_data],
                'NewPass': [item['new_passengers']['difference_percentage'] for item in performance_data],
                'Rating': [item['rating']['difference_percentage'] for item in performance_data]
            })

            # 5. Generate Heatmap Visualization
            plt.style.use('dark_background')
            plt.figure(figsize=(15, 8), facecolor='#2e2e2e')
            
            sns.heatmap(
                achievement_data.set_index('City')[['Trips', 'NewPass', 'Rating']],
                cmap='RdYlGn',
                center=0,
                annot=True,
                fmt='.1f',
                cbar_kws={'label': 'Percentage Difference from Target'}
            )
            
            plt.title('Target Achievement by City and Metric (%)', 
                     color='white', pad=20)
            
            # Customize ticks and colorbar
            plt.tick_params(colors='white')
            plt.gcf().axes[-1].tick_params(colors='white')
            plt.gcf().axes[-1].yaxis.label.set_color('white')
            
            plt.tight_layout()

            # Save plot to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf.seek(0)
            plot_base64 = base64.b64encode(buf.getvalue()).decode()
            plt.close()

            # 6. Calculate overall statistics
            overall_stats = {
                'trips': {
                    'cities_exceeded': sum(1 for item in performance_data if item['trips']['status'] == 'Exceeded'),
                    'cities_met': sum(1 for item in performance_data if item['trips']['status'] == 'Met'),
                    'cities_missed': sum(1 for item in performance_data if item['trips']['status'] == 'Missed')
                },
                'new_passengers': {
                    'cities_exceeded': sum(1 for item in performance_data if item['new_passengers']['status'] == 'Exceeded'),
                    'cities_met': sum(1 for item in performance_data if item['new_passengers']['status'] == 'Met'),
                    'cities_missed': sum(1 for item in performance_data if item['new_passengers']['status'] == 'Missed')
                },
                'rating': {
                    'cities_exceeded': sum(1 for item in performance_data if item['rating']['status'] == 'Exceeded'),
                    'cities_met': sum(1 for item in performance_data if item['rating']['status'] == 'Met'),
                    'cities_missed': sum(1 for item in performance_data if item['rating']['status'] == 'Missed')
                }
            }

            # 7. Prepare Analysis Results
            analysis_results = {
                "visualization": {
                    "plot": plot_base64,
                    "type": "image/png",
                    "encoding": "base64"
                },
                "city_performance": performance_data,
                "overall_statistics": overall_stats,
                "top_performers": {
                    "trips": max(performance_data, key=lambda x: x['trips']['difference_percentage']),
                    "new_passengers": max(performance_data, key=lambda x: x['new_passengers']['difference_percentage']),
                    "rating": max(performance_data, key=lambda x: x['rating']['difference_percentage'])
                },
                "improvement_needed": {
                    "trips": min(performance_data, key=lambda x: x['trips']['difference_percentage']),
                    "new_passengers": min(performance_data, key=lambda x: x['new_passengers']['difference_percentage']),
                    "rating": min(performance_data, key=lambda x: x['rating']['difference_percentage'])
                }
            }

            return analysis_results

        except Exception as e:
            raise Exception(f"Error analyzing target achievement: {str(e)}")
