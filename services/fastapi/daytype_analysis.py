import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from config.__init__ import DataPaths

class DayTypeAnalysisService:
    @staticmethod
    def analyze_weekday_weekend_patterns():
        """
        Analyze trip patterns between weekdays and weekends for each city.
        Returns visualization and detailed day type metrics.
        """
        try:
            # 1. Data Import using configured paths
            trips_df = pd.read_csv(DataPaths.FACT_TRIPS)
            cities_df = pd.read_csv(DataPaths.DIM_CITY)
            dates_df = pd.read_csv(DataPaths.DIM_DATE)

            # 2. Merge data
            trips_analysis = trips_df.merge(cities_df, on='city_id').merge(
                dates_df[['date', 'day_type']], 
                on='date'
            )

            # 3. Calculate trips by city and day type
            day_type_analysis = trips_analysis.groupby(
                ['city_name', 'day_type']
            )['trip_id'].count().reset_index()
            
            day_type_pivot = day_type_analysis.pivot(
                index='city_name', 
                columns='day_type', 
                values='trip_id'
            )
            
            # Calculate totals and ratios
            day_type_pivot['Total'] = day_type_pivot['Weekday'] + day_type_pivot['Weekend']
            day_type_pivot['Weekday_Ratio'] = (day_type_pivot['Weekday'] / day_type_pivot['Total'] * 100).round(2)
            day_type_pivot['Weekend_Ratio'] = (day_type_pivot['Weekend'] / day_type_pivot['Total'] * 100).round(2)

            # 4. Generate Bar Plot Visualization
            plt.style.use('dark_background')
            plt.figure(figsize=(12, 6), facecolor='#2e2e2e')
            
            day_type_ratios = pd.DataFrame({
                'City': day_type_pivot.index,
                'Weekday Ratio': day_type_pivot['Weekday_Ratio'],
                'Weekend Ratio': day_type_pivot['Weekend_Ratio']
            })

            x = range(len(day_type_ratios))
            width = 0.35

            plt.bar(x, day_type_ratios['Weekday Ratio'], width, 
                   label='Weekday', color='#00FF7F')
            plt.bar([i + width for i in x], day_type_ratios['Weekend Ratio'], 
                   width, label='Weekend', color='#FFD700')

            plt.xlabel('Cities', color='white', labelpad=10)
            plt.ylabel('Percentage of Total Trips', color='white', labelpad=10)
            plt.title('Weekday vs Weekend Trip Distribution by City', 
                     color='white', pad=20)
            
            # Customize ticks
            plt.xticks([i + width/2 for i in x], day_type_ratios['City'], 
                      rotation=45, color='white')
            plt.yticks(color='white')
            
            plt.legend(facecolor='#2e2e2e', labelcolor='white')
            plt.grid(True, alpha=0.2)
            plt.tight_layout()

            # Save plot to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf.seek(0)
            plot_base64 = base64.b64encode(buf.getvalue()).decode()
            plt.close()

            # 5. Calculate additional statistics
            overall_stats = {
                'weekday': {
                    'total_trips': int(day_type_pivot['Weekday'].sum()),
                    'average_trips_per_city': float(day_type_pivot['Weekday'].mean().round(2)),
                    'highest_trips': {
                        'city': day_type_pivot['Weekday'].idxmax(),
                        'trips': int(day_type_pivot['Weekday'].max())
                    }
                },
                'weekend': {
                    'total_trips': int(day_type_pivot['Weekend'].sum()),
                    'average_trips_per_city': float(day_type_pivot['Weekend'].mean().round(2)),
                    'highest_trips': {
                        'city': day_type_pivot['Weekend'].idxmax(),
                        'trips': int(day_type_pivot['Weekend'].max())
                    }
                }
            }

            # Calculate weekday/weekend ratio for each city
            weekday_weekend_ratios = (day_type_pivot['Weekday'] / day_type_pivot['Weekend']).round(2)
            highest_weekday_bias = weekday_weekend_ratios.idxmax()
            lowest_weekday_bias = weekday_weekend_ratios.idxmin()

            # 6. Prepare Analysis Results
            analysis_results = {
                "visualization": {
                    "plot": plot_base64,
                    "type": "image/png",
                    "encoding": "base64"
                },
                "city_distributions": {
                    city: {
                        "weekday_trips": int(day_type_pivot.loc[city, 'Weekday']),
                        "weekend_trips": int(day_type_pivot.loc[city, 'Weekend']),
                        "total_trips": int(day_type_pivot.loc[city, 'Total']),
                        "weekday_percentage": float(day_type_pivot.loc[city, 'Weekday_Ratio']),
                        "weekend_percentage": float(day_type_pivot.loc[city, 'Weekend_Ratio']),
                        "weekday_weekend_ratio": float(weekday_weekend_ratios[city])
                    }
                    for city in day_type_pivot.index
                },
                "overall_statistics": overall_stats,
                "pattern_insights": {
                    "most_weekday_biased": {
                        "city": highest_weekday_bias,
                        "weekday_weekend_ratio": float(weekday_weekend_ratios[highest_weekday_bias])
                    },
                    "most_weekend_biased": {
                        "city": lowest_weekday_bias,
                        "weekday_weekend_ratio": float(weekday_weekend_ratios[lowest_weekday_bias])
                    },
                    "average_weekday_weekend_ratio": float(weekday_weekend_ratios.mean().round(2))
                }
            }

            return analysis_results

        except Exception as e:
            raise Exception(f"Error analyzing day type patterns: {str(e)}")
