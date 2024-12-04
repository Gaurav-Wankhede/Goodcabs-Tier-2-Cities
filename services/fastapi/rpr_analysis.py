import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from config.__init__ import DataPaths

class RPRAnalysisService:
    @staticmethod
    def analyze_rpr():
        """
        Analyze Repeat Passenger Rate (RPR%) by city and month.
        Returns visualizations and detailed metrics for both city and monthly analysis.
        """
        try:
            # 1. Data Import
            fact_passenger = pd.read_csv(DataPaths.FACT_PASSENGER_SUMMARY)
            dim_city = pd.read_csv(DataPaths.DIM_CITY)
            dim_date = pd.read_csv(DataPaths.DIM_DATE)

            # 2. Calculate RPR%
            fact_passenger['RPR%'] = (fact_passenger['repeat_passengers'] / 
                                    fact_passenger['total_passengers'] * 100).round(2)

            # 3. City-wise Analysis
            city_rpr = fact_passenger.groupby('city_id')['RPR%'].mean().round(2).reset_index()
            city_rpr = city_rpr.merge(dim_city[['city_id', 'city_name']], on='city_id')
            city_rpr_sorted = city_rpr.sort_values('RPR%', ascending=False)

            # Get detailed city metrics including total passengers
            city_metrics = fact_passenger.groupby('city_id').agg({
                'RPR%': 'mean',
                'total_passengers': 'sum',
                'repeat_passengers': 'sum'
            }).round(2).reset_index()
            city_metrics = city_metrics.merge(dim_city[['city_id', 'city_name']], on='city_id')
            city_metrics_sorted = city_metrics.sort_values('RPR%', ascending=False)

            # 4. Monthly Analysis
            month_mapping = dim_date[['start_of_month', 'month_name']].drop_duplicates()
            fact_passenger = fact_passenger.merge(month_mapping, 
                                                left_on='month', 
                                                right_on='start_of_month')
            
            monthly_rpr = fact_passenger.groupby(['month', 'month_name']).agg({
                'RPR%': 'mean',
                'total_passengers': 'sum',
                'repeat_passengers': 'sum'
            }).round(2).reset_index()
            monthly_rpr_sorted = monthly_rpr.sort_values('RPR%', ascending=False)

            # 5. Generate Visualizations
            # City RPR Plot
            plt.style.use('dark_background')
            fig1, ax1 = plt.subplots(figsize=(12, 6), facecolor='#2e2e2e')
            
            sns.barplot(data=city_rpr_sorted, x='city_name', y='RPR%', 
                       palette='RdYlGn', ax=ax1)
            ax1.set_title('Repeat Passenger Rate (RPR%) by City', pad=20)
            ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45)
            ax1.set_ylabel('RPR%')
            ax1.set_xlabel('City')

            for i, v in enumerate(city_rpr_sorted['RPR%']):
                ax1.text(i, v, f'{v}%', ha='center', va='bottom')

            plt.tight_layout()
            
            # Save city plot
            buf1 = io.BytesIO()
            fig1.savefig(buf1, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf1.seek(0)
            city_plot = base64.b64encode(buf1.getvalue()).decode()
            plt.close(fig1)

            # Monthly RPR Plot
            fig2, ax2 = plt.subplots(figsize=(12, 6), facecolor='#2e2e2e')
            
            sns.barplot(data=monthly_rpr_sorted, x='month_name', y='RPR%', 
                       palette='RdYlGn', ax=ax2)
            ax2.set_title('Monthly Repeat Passenger Rate (RPR%)', pad=20)
            ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)
            ax2.set_ylabel('RPR%')
            ax2.set_xlabel('Month')

            for i, v in enumerate(monthly_rpr_sorted['RPR%']):
                ax2.text(i, v, f'{v}%', ha='center', va='bottom')

            plt.tight_layout()
            
            # Save monthly plot
            buf2 = io.BytesIO()
            fig2.savefig(buf2, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf2.seek(0)
            monthly_plot = base64.b64encode(buf2.getvalue()).decode()
            plt.close(fig2)

            # 6. Prepare Analysis Results
            analysis_results = {
                "visualizations": {
                    "city_rpr": {
                        "plot": city_plot,
                        "type": "image/png",
                        "encoding": "base64"
                    },
                    "monthly_rpr": {
                        "plot": monthly_plot,
                        "type": "image/png",
                        "encoding": "base64"
                    }
                },
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
