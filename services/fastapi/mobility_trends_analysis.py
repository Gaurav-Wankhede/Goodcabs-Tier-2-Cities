import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import numpy as np
from config.__init__ import DataPaths

class MobilityTrendsAnalysisService:
    # Constants for environmental calculations
    CURRENT_CARBON_PER_KM = 0.14  # kg CO2/km for regular vehicles
    EV_CARBON_PER_KM = 0.053  # kg CO2/km for electric vehicles
    CARBON_PRICE_PER_TON = 25  # USD per ton of CO2
    EV_COST_PREMIUM = 15000  # USD additional cost per EV
    EV_MAINTENANCE_SAVINGS = 0.03  # USD/km maintenance savings
    ELECTRICITY_COST_PER_KM = 0.05  # USD/km for EV charging
    FUEL_COST_PER_KM = 0.12  # USD/km for regular fuel

    @staticmethod
    def analyze_mobility_trends():
        """
        Analyze mobility trends and potential impact of EV adoption
        """
        try:
            # 1. Data Import
            fact_trips = pd.read_csv(DataPaths.FACT_TRIPS)
            dim_city = pd.read_csv(DataPaths.DIM_CITY)

            # 2. City-wise Analysis
            city_metrics = fact_trips.merge(
                dim_city[['city_id', 'city_name']], 
                on='city_id'
            )
            
            city_analysis = city_metrics.groupby('city_name').agg({
                'distance_travelled(km)': ['mean', 'sum', 'count'],
                'fare_amount': ['mean', 'sum'],
                'trip_id': 'count'
            }).round(2)

            # Flatten column names
            city_analysis.columns = [
                'avg_distance', 'total_distance', 'trip_count',
                'avg_fare', 'total_fare', 'total_trips'
            ]

            # 3. Environmental Impact Calculations
            city_analysis['current_carbon_kg'] = (
                city_analysis['total_distance'] * 
                MobilityTrendsAnalysisService.CURRENT_CARBON_PER_KM
            ).round(2)
            
            city_analysis['ev_carbon_kg'] = (
                city_analysis['total_distance'] * 
                MobilityTrendsAnalysisService.EV_CARBON_PER_KM
            ).round(2)
            
            city_analysis['carbon_savings_kg'] = (
                city_analysis['current_carbon_kg'] - 
                city_analysis['ev_carbon_kg']
            ).round(2)

            # 4. Economic Impact Calculations
            city_analysis['current_fuel_cost'] = (
                city_analysis['total_distance'] * 
                MobilityTrendsAnalysisService.FUEL_COST_PER_KM
            ).round(2)
            
            city_analysis['ev_energy_cost'] = (
                city_analysis['total_distance'] * 
                MobilityTrendsAnalysisService.ELECTRICITY_COST_PER_KM
            ).round(2)
            
            city_analysis['maintenance_savings'] = (
                city_analysis['total_distance'] * 
                MobilityTrendsAnalysisService.EV_MAINTENANCE_SAVINGS
            ).round(2)

            # Calculate fleet size and investment needed
            avg_daily_distance = city_analysis['total_distance'] / 365
            city_analysis['estimated_fleet_size'] = (
                (avg_daily_distance / 200).round()  # Assume 200km per day per vehicle
            ).astype(int)
            
            city_analysis['ev_investment_needed'] = (
                city_analysis['estimated_fleet_size'] * 
                MobilityTrendsAnalysisService.EV_COST_PREMIUM
            ).round(2)

            # 5. Generate Visualizations
            plt.style.use('dark_background')

            # 5.1 Carbon Emissions Comparison
            fig1, ax1 = plt.subplots(figsize=(12, 6), facecolor='#2e2e2e')
            x = range(len(city_analysis.index))
            width = 0.35

            current_emissions = ax1.bar(
                x, 
                city_analysis['current_carbon_kg'], 
                width, 
                label='Current Emissions',
                color='red'
            )
            ev_emissions = ax1.bar(
                [i + width for i in x], 
                city_analysis['ev_carbon_kg'], 
                width, 
                label='EV Emissions',
                color='green'
            )

            ax1.set_title('Current vs EV Carbon Emissions by City')
            ax1.set_xlabel('City')
            ax1.set_ylabel('Carbon Emissions (kg CO2)')
            ax1.set_xticks([i + width/2 for i in x])
            ax1.set_xticklabels(city_analysis.index, rotation=45, ha='right')
            ax1.legend()

            # Add value labels
            for bars in [current_emissions, ev_emissions]:
                for bar in bars:
                    height = bar.get_height()
                    ax1.text(
                        bar.get_x() + bar.get_width()/2.,
                        height,
                        f'{int(height):,}',
                        ha='center', 
                        va='bottom'
                    )

            plt.tight_layout()

            # Save emissions plot
            buf1 = io.BytesIO()
            fig1.savefig(buf1, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf1.seek(0)
            emissions_plot = base64.b64encode(buf1.getvalue()).decode()
            plt.close(fig1)

            # 5.2 Cost Analysis Plot
            fig2, ax2 = plt.subplots(figsize=(12, 6), facecolor='#2e2e2e')
            
            # Create investment vs savings comparison
            investment = city_analysis['ev_investment_needed'] / 1000  # Convert to thousands
            annual_savings = (
                (city_analysis['current_fuel_cost'] - city_analysis['ev_energy_cost'] + 
                 city_analysis['maintenance_savings']) / 1000  # Convert to thousands
            )
            
            x = np.arange(len(city_analysis.index))
            width = 0.35

            ax2.bar(x - width/2, investment, width, label='Investment Needed (K USD)')
            ax2.bar(x + width/2, annual_savings, width, label='Annual Savings (K USD)')

            ax2.set_title('EV Investment vs Annual Savings by City')
            ax2.set_xlabel('City')
            ax2.set_ylabel('Amount (Thousand USD)')
            ax2.set_xticks(x)
            ax2.set_xticklabels(city_analysis.index, rotation=45, ha='right')
            ax2.legend()

            plt.tight_layout()

            # Save cost analysis plot
            buf2 = io.BytesIO()
            fig2.savefig(buf2, format='png', bbox_inches='tight', facecolor='#2e2e2e')
            buf2.seek(0)
            cost_plot = base64.b64encode(buf2.getvalue()).decode()
            plt.close(fig2)

            # 6. Prepare Analysis Results
            total_current_emissions = city_analysis['current_carbon_kg'].sum()
            total_ev_emissions = city_analysis['ev_carbon_kg'].sum()
            total_carbon_savings = city_analysis['carbon_savings_kg'].sum()
            
            total_investment = city_analysis['ev_investment_needed'].sum()
            total_annual_savings = (
                (city_analysis['current_fuel_cost'] - city_analysis['ev_energy_cost'] + 
                 city_analysis['maintenance_savings']).sum()
            )
            
            payback_years = total_investment / total_annual_savings

            analysis_results = {
                "visualizations": {
                    "emissions_comparison": {
                        "plot": emissions_plot,
                        "type": "image/png",
                        "encoding": "base64"
                    },
                    "cost_analysis": {
                        "plot": cost_plot,
                        "type": "image/png",
                        "encoding": "base64"
                    }
                },
                "environmental_impact": {
                    "total_current_emissions_kg": float(total_current_emissions),
                    "total_ev_emissions_kg": float(total_ev_emissions),
                    "total_carbon_savings_kg": float(total_carbon_savings),
                    "emission_reduction_percentage": float(
                        (total_carbon_savings / total_current_emissions * 100).round(2)
                    ),
                    "city_wise_impact": [
                        {
                            "city": city,
                            "current_emissions": float(data['current_carbon_kg']),
                            "ev_emissions": float(data['ev_carbon_kg']),
                            "carbon_savings": float(data['carbon_savings_kg'])
                        }
                        for city, data in city_analysis.iterrows()
                    ]
                },
                "economic_analysis": {
                    "total_investment_needed": float(total_investment),
                    "total_annual_savings": float(total_annual_savings),
                    "payback_period_years": float(payback_years.round(2)),
                    "city_wise_economics": [
                        {
                            "city": city,
                            "fleet_size": int(data['estimated_fleet_size']),
                            "investment_needed": float(data['ev_investment_needed']),
                            "annual_savings": float(
                                data['current_fuel_cost'] - 
                                data['ev_energy_cost'] + 
                                data['maintenance_savings']
                            )
                        }
                        for city, data in city_analysis.iterrows()
                    ]
                },
                "recommendations": {
                    "environmental": [
                        "Implement a phased EV adoption strategy starting with cities showing highest emission savings",
                        "Consider renewable energy sources for EV charging to further reduce emissions",
                        "Monitor and report emission reductions to enhance brand value"
                    ],
                    "economic": [
                        f"Total investment of ${total_investment:,.2f} needed for complete EV transition",
                        f"Expected annual savings of ${total_annual_savings:,.2f}",
                        f"Payback period of {payback_years:.1f} years indicates long-term financial viability"
                    ],
                    "operational": [
                        "Start with pilot programs in cities with highest potential savings",
                        "Develop charging infrastructure partnerships",
                        "Train maintenance staff for EV servicing",
                        "Consider battery leasing options to reduce upfront costs"
                    ]
                }
            }

            return analysis_results

        except Exception as e:
            raise Exception(f"Error analyzing mobility trends: {str(e)}")
