import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from config.__init__ import DataPaths

class DemandAnalysisService:
    @staticmethod
    def analyze_monthly_demand():
        """
        Analyze peak and low demand months for each city.
        Returns visualization and detailed demand metrics.
        """
        try:
            # 1. Data Import using configured paths
            trips_df = pd.read_csv(DataPaths.FACT_TRIPS)
            cities_df = pd.read_csv(DataPaths.DIM_CITY)
            dates_df = pd.read_csv(DataPaths.DIM_DATE)

            # 2. Merge trips with city and date information
            trips_analysis = trips_df.merge(cities_df, on='city_id').merge(
                dates_df[['date', 'month_name', 'start_of_month']], 
                on='date'
            )

            # 3. Calculate monthly trips for each city
            monthly_trips = trips_analysis.groupby(
                ['city_name', 'start_of_month', 'month_name']
            )['trip_id'].count().reset_index()
            monthly_trips.columns = ['city_name', 'start_of_month', 'month_name', 'total_trips']

            # 4. Find peak and low demand months for each city
            results = []
            for city in monthly_trips['city_name'].unique():
                city_data = monthly_trips[monthly_trips['city_name'] == city]
                peak_idx = city_data['total_trips'].idxmax()
                low_idx = city_data['total_trips'].idxmin()
                
                results.append({
                    'city': city,
                    'peak_month': city_data.loc[peak_idx, 'month_name'],
                    'peak_trips': int(city_data.loc[peak_idx, 'total_trips']),
                    'low_month': city_data.loc[low_idx, 'month_name'],
                    'low_trips': int(city_data.loc[low_idx, 'total_trips'])
                })

            # 5. Generate Heatmap Visualization
            plt.style.use('dark_background')
            plt.figure(figsize=(15, 8), facecolor='#2e2e2e')
            
            pivot_data = monthly_trips.pivot(
                index='city_name', 
                columns='month_name', 
                values='total_trips'
            )
            
            sns.heatmap(
                pivot_data, 
                annot=True, 
                fmt=',', 
                cmap='YlOrRd',
                cbar_kws={'label': 'Number of Trips'},
                annot_kws={'size': 8}
            )
            
            plt.title('Monthly Trip Distribution by City', color='white', pad=20)
            plt.xlabel('Month', color='white', labelpad=10)
            plt.ylabel('City', color='white', labelpad=10)
            plt.xticks(rotation=45, color='white')
            plt.yticks(color='white')
            
            # Customize colorbar
            plt.gcf().axes[-1].tick_params(colors='white')
            plt.gcf().axes[-1].yaxis.label.set_color('white')
            
            plt.tight_layout()

            # Save plot to bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf.seek(0)
            plot_base64 = base64.b64encode(buf.getvalue()).decode()
            plt.close()

            # 6. Calculate additional statistics
            total_monthly_trips = monthly_trips.groupby('month_name')['total_trips'].sum()
            busiest_month = total_monthly_trips.idxmax()
            quietest_month = total_monthly_trips.idxmin()

            # 7. Prepare Analysis Results
            analysis_results = {
                "visualization": {
                    "plot": plot_base64,
                    "type": "image/png",
                    "encoding": "base64"
                },
                "city_demand_patterns": results,
                "monthly_distribution": {
                    city: monthly_trips[monthly_trips['city_name'] == city][
                        ['month_name', 'total_trips']
                    ].set_index('month_name')['total_trips'].to_dict()
                    for city in monthly_trips['city_name'].unique()
                },
                "summary_statistics": {
                    "overall_busiest_month": {
                        "month": busiest_month,
                        "total_trips": int(total_monthly_trips[busiest_month])
                    },
                    "overall_quietest_month": {
                        "month": quietest_month,
                        "total_trips": int(total_monthly_trips[quietest_month])
                    },
                    "monthly_totals": total_monthly_trips.to_dict(),
                    "demand_variability": {
                        city: {
                            "max_min_ratio": float(round(
                                monthly_trips[monthly_trips['city_name'] == city]['total_trips'].max() /
                                monthly_trips[monthly_trips['city_name'] == city]['total_trips'].min(), 
                                2
                            )),
                            "coefficient_of_variation": float(round(
                                monthly_trips[monthly_trips['city_name'] == city]['total_trips'].std() /
                                monthly_trips[monthly_trips['city_name'] == city]['total_trips'].mean() * 100,
                                2
                            ))
                        }
                        for city in monthly_trips['city_name'].unique()
                    }
                }
            }

            return analysis_results

        except Exception as e:
            raise Exception(f"Error analyzing monthly demand: {str(e)}")
