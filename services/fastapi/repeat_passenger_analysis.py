import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from config.__init__ import DataPaths

class RepeatPassengerAnalysisService:
    @staticmethod
    def analyze_passenger_frequency():
        """
        Analyze repeat passenger frequency patterns across cities.
        Returns visualizations and detailed frequency metrics.
        """
        try:
            # 1. Data Import using configured paths
            repeat_dist = pd.read_csv(DataPaths.DIM_REPEAT_TRIP_DISTRIBUTION)
            cities_df = pd.read_csv(DataPaths.DIM_CITY)

            # 2. Merge data and prepare
            trip_freq = repeat_dist.merge(cities_df, on='city_id')
            trip_freq['trip_number'] = trip_freq['trip_count'].str.extract(r'(\d+)').astype(int)
            trip_freq = trip_freq.sort_values('trip_number')

            # 3. Calculate total repeat passengers per city
            city_totals = trip_freq.groupby('city_name')['repeat_passenger_count'].sum().reset_index()

            # 4. Calculate percentage distribution
            trip_freq_pct = trip_freq.merge(city_totals, on='city_name', suffixes=('', '_total'))
            trip_freq_pct['percentage'] = (
                trip_freq_pct['repeat_passenger_count'] / 
                trip_freq_pct['repeat_passenger_count_total'] * 100
            ).round(2)

            # 5. Analyze high frequency patterns (5 or more trips)
            high_freq_analysis = trip_freq_pct[trip_freq_pct['trip_number'] >= 5].groupby('city_name').agg({
                'repeat_passenger_count': 'sum',
                'repeat_passenger_count_total': 'first'
            }).assign(
                high_freq_percentage=lambda x: (
                    x['repeat_passenger_count'] / x['repeat_passenger_count_total'] * 100
                ).round(2)
            ).sort_values('high_freq_percentage', ascending=False)

            # 6. Create frequency distribution table
            freq_dist = trip_freq_pct.pivot_table(
                index='city_name',
                columns='trip_number',
                values='percentage',
                aggfunc='mean'
            ).round(2)

            # 7. Generate Heatmap Visualization
            plt.style.use('dark_background')
            plt.figure(figsize=(15, 8), facecolor='#2e2e2e')
            
            sns.heatmap(
                freq_dist,
                annot=True,
                fmt='.1f',
                cmap='YlOrRd',
                cbar_kws={'label': 'Percentage of Repeat Passengers'}
            )
            
            plt.title('Trip Frequency Distribution Patterns by City', 
                     color='white', pad=20)
            plt.xlabel('Number of Trips per Month', color='white', labelpad=10)
            plt.ylabel('City', color='white', labelpad=10)
            
            # Customize ticks and colorbar
            plt.tick_params(colors='white')
            plt.gcf().axes[-1].tick_params(colors='white')
            plt.gcf().axes[-1].yaxis.label.set_color('white')
            
            plt.tight_layout()

            # Save heatmap to bytes
            buf1 = io.BytesIO()
            plt.savefig(buf1, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf1.seek(0)
            heatmap_base64 = base64.b64encode(buf1.getvalue()).decode()
            plt.close()

            # 8. Generate Bar Plot for High-Frequency Passengers
            plt.figure(figsize=(12, 6), facecolor='#2e2e2e')
            high_freq_analysis['high_freq_percentage'].plot(
                kind='bar',
                color='#00FF7F',
                width=0.8
            )
            
            plt.title('Percentage of High-Frequency Repeat Passengers (5+ trips) by City', 
                     color='white', pad=20)
            plt.xlabel('City', color='white', labelpad=10)
            plt.ylabel('Percentage of Total Repeat Passengers', color='white', labelpad=10)
            plt.grid(True, alpha=0.2)
            
            # Customize ticks
            plt.xticks(rotation=45, color='white')
            plt.yticks(color='white')
            
            plt.tight_layout()

            # Save bar plot to bytes
            buf2 = io.BytesIO()
            plt.savefig(buf2, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf2.seek(0)
            barplot_base64 = base64.b64encode(buf2.getvalue()).decode()
            plt.close()

            # 9. Calculate additional statistics
            total_stats = {
                'total_repeat_passengers': int(city_totals['repeat_passenger_count'].sum()),
                'high_freq_passengers': int(high_freq_analysis['repeat_passenger_count'].sum()),
                'high_freq_percentage': float(
                    (high_freq_analysis['repeat_passenger_count'].sum() / 
                     city_totals['repeat_passenger_count'].sum() * 100).round(2)
                )
            }

            # 10. Prepare Analysis Results
            analysis_results = {
                "visualizations": {
                    "frequency_heatmap": {
                        "plot": heatmap_base64,
                        "type": "image/png",
                        "encoding": "base64"
                    },
                    "high_frequency_barplot": {
                        "plot": barplot_base64,
                        "type": "image/png",
                        "encoding": "base64"
                    }
                },
                "frequency_distribution": {
                    city: freq_dist.loc[city].dropna().to_dict()
                    for city in freq_dist.index
                },
                "high_frequency_analysis": {
                    city: {
                        "total_repeat_passengers": int(high_freq_analysis.loc[city, 'repeat_passenger_count_total']),
                        "high_freq_passengers": int(high_freq_analysis.loc[city, 'repeat_passenger_count']),
                        "high_freq_percentage": float(high_freq_analysis.loc[city, 'high_freq_percentage'])
                    }
                    for city in high_freq_analysis.index
                },
                "overall_statistics": total_stats,
                "city_rankings": {
                    "highest_retention": {
                        "city": high_freq_analysis.index[0],
                        "percentage": float(high_freq_analysis['high_freq_percentage'].iloc[0])
                    },
                    "lowest_retention": {
                        "city": high_freq_analysis.index[-1],
                        "percentage": float(high_freq_analysis['high_freq_percentage'].iloc[-1])
                    }
                }
            }

            return analysis_results

        except Exception as e:
            raise Exception(f"Error analyzing repeat passenger patterns: {str(e)}")
