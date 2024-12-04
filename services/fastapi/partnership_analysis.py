import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import numpy as np
from config.__init__ import DataPaths

class PartnershipAnalysisService:
    # Constants for partnership scoring
    WEEKEND_WEIGHT = 0.35
    NEW_CUSTOMER_WEIGHT = 0.25
    RATING_WEIGHT = 0.20
    FARE_WEIGHT = 0.20
    
    # Constants for revenue projections
    HOTEL_COMMISSION_RATE = 0.10  # 10% commission on hotel-referred rides
    MALL_COMMISSION_RATE = 0.08   # 8% commission on mall-referred rides
    EVENT_COMMISSION_RATE = 0.12  # 12% commission on event-referred rides
    
    @staticmethod
    def analyze_partnership_opportunities():
        """
        Analyze potential partnership opportunities with local businesses
        """
        try:
            # 1. Data Import
            fact_trips = pd.read_csv(DataPaths.FACT_TRIPS)
            dim_date = pd.read_csv(DataPaths.DIM_DATE)
            dim_city = pd.read_csv(DataPaths.DIM_CITY)
            fact_passenger = pd.read_csv(DataPaths.FACT_PASSENGER_SUMMARY)

            # 2. Basic Analysis Setup
            trips_analysis = fact_trips.merge(
                dim_date[['date', 'day_type', 'month_name']], 
                on='date'
            )
            trips_analysis = trips_analysis.merge(
                dim_city[['city_id', 'city_name']], 
                on='city_id'
            )

            # 3. Calculate Partnership Metrics
            partnership_metrics = pd.DataFrame()

            # 3.1 Weekend vs Weekday Analysis
            weekend_volume = trips_analysis[
                trips_analysis['day_type'] == 'Weekend'
            ].groupby('city_name')['trip_id'].count()
            
            weekday_volume = trips_analysis[
                trips_analysis['day_type'] == 'Weekday'
            ].groupby('city_name')['trip_id'].count()
            
            partnership_metrics['weekend_ratio'] = (
                weekend_volume / weekday_volume * 100
            ).round(2)

            # 3.2 New Customer Analysis
            city_passengers = fact_passenger.merge(
                dim_city[['city_id', 'city_name']], 
                on='city_id'
            )
            new_customer_ratio = city_passengers.groupby('city_name').agg({
                'new_passengers': 'sum',
                'total_passengers': 'sum'
            })
            partnership_metrics['new_customer_ratio'] = (
                new_customer_ratio['new_passengers'] / 
                new_customer_ratio['total_passengers'] * 100
            ).round(2)

            # 3.3 Trip Metrics
            avg_metrics = trips_analysis.groupby('city_name').agg({
                'fare_amount': 'mean',
                'distance_travelled(km)': 'mean',
                'passenger_rating': 'mean'
            }).round(2)
            
            partnership_metrics = partnership_metrics.join(avg_metrics)

            # 3.4 Calculate Partnership Score
            partnership_metrics['partnership_score'] = (
                partnership_metrics['weekend_ratio'] * PartnershipAnalysisService.WEEKEND_WEIGHT +
                partnership_metrics['new_customer_ratio'] * PartnershipAnalysisService.NEW_CUSTOMER_WEIGHT +
                partnership_metrics['passenger_rating'] * PartnershipAnalysisService.RATING_WEIGHT +
                partnership_metrics['fare_amount'] * PartnershipAnalysisService.FARE_WEIGHT
            ).round(2)

            # Sort by partnership potential
            partnership_metrics = partnership_metrics.sort_values(
                'partnership_score', 
                ascending=False
            )

            # 4. Monthly Trend Analysis
            monthly_trends = trips_analysis.groupby(
                ['city_name', 'month_name']
            )['trip_id'].count().unstack()

            # 5. Revenue Projections
            city_revenue = trips_analysis.groupby('city_name').agg({
                'fare_amount': 'sum'
            })

            # Project potential partnership revenue
            partnership_metrics['hotel_revenue'] = (
                city_revenue['fare_amount'] * 
                PartnershipAnalysisService.HOTEL_COMMISSION_RATE
            ).round(2)
            
            partnership_metrics['mall_revenue'] = (
                city_revenue['fare_amount'] * 
                PartnershipAnalysisService.MALL_COMMISSION_RATE
            ).round(2)
            
            partnership_metrics['event_revenue'] = (
                city_revenue['fare_amount'] * 
                PartnershipAnalysisService.EVENT_COMMISSION_RATE
            ).round(2)

            # 6. Generate Visualizations
            plt.style.use('dark_background')

            # 6.1 Partnership Score Plot
            fig1, ax1 = plt.subplots(figsize=(12, 6), facecolor='#2e2e2e')
            
            bars = ax1.bar(
                partnership_metrics.index,
                partnership_metrics['partnership_score'],
                color=plt.cm.RdYlGn(
                    np.linspace(0.2, 0.8, len(partnership_metrics))
                )
            )

            ax1.set_title('Partnership Potential Score by City')
            ax1.set_xlabel('City')
            ax1.set_ylabel('Partnership Score')
            plt.xticks(rotation=45, ha='right')

            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax1.text(
                    bar.get_x() + bar.get_width()/2.,
                    height,
                    f'{height:.1f}',
                    ha='center',
                    va='bottom'
                )

            plt.tight_layout()

            # Save partnership score plot
            buf1 = io.BytesIO()
            fig1.savefig(buf1, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf1.seek(0)
            score_plot = base64.b64encode(buf1.getvalue()).decode()
            plt.close(fig1)

            # 6.2 Revenue Projection Plot
            fig2, ax2 = plt.subplots(figsize=(12, 6), facecolor='#2e2e2e')
            
            x = np.arange(len(partnership_metrics.index))
            width = 0.25

            ax2.bar(x - width, partnership_metrics['hotel_revenue']/1000, 
                   width, label='Hotel Partnerships')
            ax2.bar(x, partnership_metrics['mall_revenue']/1000, 
                   width, label='Mall Partnerships')
            ax2.bar(x + width, partnership_metrics['event_revenue']/1000, 
                   width, label='Event Partnerships')

            ax2.set_title('Projected Annual Revenue from Partnerships')
            ax2.set_xlabel('City')
            ax2.set_ylabel('Projected Revenue (Thousand USD)')
            ax2.set_xticks(x)
            ax2.set_xticklabels(partnership_metrics.index, rotation=45, ha='right')
            ax2.legend()

            plt.tight_layout()

            # Save revenue projection plot
            buf2 = io.BytesIO()
            fig2.savefig(buf2, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf2.seek(0)
            revenue_plot = base64.b64encode(buf2.getvalue()).decode()
            plt.close(fig2)

            # 7. Prepare Analysis Results
            total_potential_revenue = (
                partnership_metrics['hotel_revenue'].sum() +
                partnership_metrics['mall_revenue'].sum() +
                partnership_metrics['event_revenue'].sum()
            )

            analysis_results = {
                "visualizations": {
                    "partnership_scores": {
                        "plot": score_plot,
                        "type": "image/png",
                        "encoding": "base64"
                    },
                    "revenue_projections": {
                        "plot": revenue_plot,
                        "type": "image/png",
                        "encoding": "base64"
                    }
                },
                "partnership_metrics": {
                    "city_scores": [
                        {
                            "city": city,
                            "score": float(data['partnership_score']),
                            "metrics": {
                                "weekend_ratio": float(data['weekend_ratio']),
                                "new_customer_ratio": float(data['new_customer_ratio']),
                                "avg_fare": float(data['fare_amount']),
                                "avg_rating": float(data['passenger_rating'])
                            }
                        }
                        for city, data in partnership_metrics.iterrows()
                    ],
                    "top_partnership_cities": partnership_metrics.head(3).index.tolist()
                },
                "revenue_projections": {
                    "total_potential_revenue": float(total_potential_revenue),
                    "city_projections": [
                        {
                            "city": city,
                            "hotel_revenue": float(data['hotel_revenue']),
                            "mall_revenue": float(data['mall_revenue']),
                            "event_revenue": float(data['event_revenue']),
                            "total_revenue": float(
                                data['hotel_revenue'] + 
                                data['mall_revenue'] + 
                                data['event_revenue']
                            )
                        }
                        for city, data in partnership_metrics.iterrows()
                    ]
                },
                "recommendations": {
                    "priority_cities": [
                        f"Focus on {city} - High partnership score of {score:.1f}"
                        for city, score in partnership_metrics['partnership_score'].head(3).items()
                    ],
                    "partnership_types": [
                        {
                            "type": "Hotels",
                            "commission_rate": f"{PartnershipAnalysisService.HOTEL_COMMISSION_RATE*100}%",
                            "target_cities": partnership_metrics.nlargest(3, 'hotel_revenue').index.tolist()
                        },
                        {
                            "type": "Shopping Malls",
                            "commission_rate": f"{PartnershipAnalysisService.MALL_COMMISSION_RATE*100}%",
                            "target_cities": partnership_metrics.nlargest(3, 'mall_revenue').index.tolist()
                        },
                        {
                            "type": "Event Venues",
                            "commission_rate": f"{PartnershipAnalysisService.EVENT_COMMISSION_RATE*100}%",
                            "target_cities": partnership_metrics.nlargest(3, 'event_revenue').index.tolist()
                        }
                    ],
                    "action_items": [
                        "Develop tiered partnership programs based on partner type and city potential",
                        "Create customized marketing campaigns for each city's top-performing sectors",
                        "Implement loyalty program integration with partner businesses",
                        "Set up dedicated support channels for business partners",
                        "Monitor and optimize commission structures based on performance"
                    ]
                }
            }

            return analysis_results

        except Exception as e:
            raise Exception(f"Error analyzing partnership opportunities: {str(e)}")
