import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import numpy as np
from config.__init__ import DataPaths

class RPRFactorsAnalysisService:
    @staticmethod
    def analyze_rpr_factors():
        """
        Analyze factors influencing Repeat Passenger Rate (RPR%) including
        service quality, pricing, and distance metrics.
        """
        try:
            # 1. Data Import
            fact_trips = pd.read_csv(DataPaths.FACT_TRIPS)
            fact_passenger = pd.read_csv(DataPaths.FACT_PASSENGER_SUMMARY)
            dim_city = pd.read_csv(DataPaths.DIM_CITY)

            # 2. Calculate RPR% for each city
            fact_passenger['RPR%'] = (fact_passenger['repeat_passengers'] / 
                                    fact_passenger['total_passengers'] * 100).round(2)
            city_rpr = fact_passenger.groupby('city_id')['RPR%'].mean().round(2)

            # 3. Calculate city-wise metrics
            city_metrics = fact_trips.groupby('city_id').agg({
                'passenger_rating': 'mean',
                'fare_amount': 'mean',
                'distance_travelled(km)': 'mean',
                'trip_id': 'count'  # Added total trips as a factor
            }).round(2)

            # Calculate fare per km
            city_metrics['fare_per_km'] = (city_metrics['fare_amount'] / 
                                         city_metrics['distance_travelled(km)']).round(2)

            # 4. Combine all metrics
            city_analysis = pd.DataFrame({
                'RPR%': city_rpr,
                'Avg_Rating': city_metrics['passenger_rating'],
                'Avg_Fare': city_metrics['fare_amount'],
                'Avg_Distance': city_metrics['distance_travelled(km)'],
                'Fare_per_km': city_metrics['fare_per_km'],
                'Total_Trips': city_metrics['trip_id']
            }).reset_index()

            # Add city names
            city_analysis = city_analysis.merge(dim_city[['city_id', 'city_name']], 
                                              on='city_id')

            # 5. Calculate correlations
            correlation_matrix = city_analysis[[
                'RPR%', 'Avg_Rating', 'Avg_Fare', 'Avg_Distance', 
                'Fare_per_km', 'Total_Trips'
            ]].corr()

            # 6. Generate Visualizations
            plt.style.use('dark_background')

            # Correlation Heatmap
            fig1, ax1 = plt.subplots(figsize=(10, 8), facecolor='#2e2e2e')
            sns.heatmap(correlation_matrix,
                       annot=True,
                       cmap='RdYlGn',
                       center=0,
                       fmt='.2f',
                       square=True,
                       ax=ax1)
            ax1.set_title('Correlation Matrix of Factors Affecting RPR%', pad=20)
            plt.tight_layout()

            # Save correlation plot
            buf1 = io.BytesIO()
            fig1.savefig(buf1, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf1.seek(0)
            correlation_plot = base64.b64encode(buf1.getvalue()).decode()
            plt.close(fig1)

            # Scatter plots
            fig2, axes = plt.subplots(2, 3, figsize=(18, 12), facecolor='#2e2e2e')
            axes = axes.ravel()
            factors = ['Avg_Rating', 'Avg_Fare', 'Avg_Distance', 
                      'Fare_per_km', 'Total_Trips']

            for i, factor in enumerate(factors):
                sns.scatterplot(data=city_analysis, 
                              x=factor, 
                              y='RPR%', 
                              ax=axes[i], 
                              color='goldenrod')
                axes[i].set_title(f'RPR% vs {factor}')
                
                # Add trend line
                z = np.polyfit(city_analysis[factor], city_analysis['RPR%'], 1)
                p = np.poly1d(z)
                axes[i].plot(city_analysis[factor], 
                           p(city_analysis[factor]), 
                           "r--", 
                           alpha=0.8)
                
                # Add correlation coefficient
                corr = correlation_matrix.loc['RPR%', factor]
                axes[i].text(0.05, 0.95, f'Correlation: {corr:.2f}',
                           transform=axes[i].transAxes,
                           verticalalignment='top')

            axes[-1].remove()  # Remove the last empty subplot
            plt.tight_layout()

            # Save scatter plots
            buf2 = io.BytesIO()
            fig2.savefig(buf2, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf2.seek(0)
            scatter_plots = base64.b64encode(buf2.getvalue()).decode()
            plt.close(fig2)

            # 7. Identify key insights
            correlations = correlation_matrix['RPR%'].sort_values(ascending=False)
            strong_positive = correlations[
                (correlations > 0.5) & (correlations.index != 'RPR%')
            ]
            strong_negative = correlations[correlations < -0.5]
            
            # Calculate impact scores
            city_analysis['Rating_Impact'] = (
                city_analysis['Avg_Rating'] * correlation_matrix.loc['RPR%', 'Avg_Rating']
            )
            city_analysis['Fare_Impact'] = (
                city_analysis['Fare_per_km'] * correlation_matrix.loc['RPR%', 'Fare_per_km']
            )

            # 8. Prepare Analysis Results
            analysis_results = {
                "visualizations": {
                    "correlation_heatmap": {
                        "plot": correlation_plot,
                        "type": "image/png",
                        "encoding": "base64"
                    },
                    "factor_scatter_plots": {
                        "plot": scatter_plots,
                        "type": "image/png",
                        "encoding": "base64"
                    }
                },
                "correlation_analysis": {
                    "strong_positive_factors": [
                        {
                            "factor": factor,
                            "correlation": float(corr)
                        }
                        for factor, corr in strong_positive.items()
                    ],
                    "strong_negative_factors": [
                        {
                            "factor": factor,
                            "correlation": float(corr)
                        }
                        for factor, corr in strong_negative.items()
                    ],
                    "all_correlations": [
                        {
                            "factor": factor,
                            "correlation": float(corr)
                        }
                        for factor, corr in correlations.items()
                        if factor != 'RPR%'
                    ]
                },
                "city_factor_analysis": [
                    {
                        "city": row['city_name'],
                        "rpr_percentage": float(row['RPR%']),
                        "metrics": {
                            "avg_rating": float(row['Avg_Rating']),
                            "avg_fare": float(row['Avg_Fare']),
                            "avg_distance": float(row['Avg_Distance']),
                            "fare_per_km": float(row['Fare_per_km']),
                            "total_trips": int(row['Total_Trips'])
                        },
                        "impact_scores": {
                            "rating_impact": float(row['Rating_Impact']),
                            "fare_impact": float(row['Fare_Impact'])
                        }
                    }
                    for _, row in city_analysis.sort_values('RPR%', ascending=False).iterrows()
                ],
                "key_findings": {
                    "strongest_positive_factor": {
                        "factor": strong_positive.index[0] if not strong_positive.empty else None,
                        "correlation": float(strong_positive.iloc[0]) if not strong_positive.empty else None
                    },
                    "strongest_negative_factor": {
                        "factor": strong_negative.index[0] if not strong_negative.empty else None,
                        "correlation": float(strong_negative.iloc[0]) if not strong_negative.empty else None
                    }
                }
            }

            return analysis_results

        except Exception as e:
            raise Exception(f"Error analyzing RPR factors: {str(e)}")
