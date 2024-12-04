from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from services.fastapi.city_performance import CityPerformanceService
from services.fastapi.fare_analysis import FareAnalysisService
from services.fastapi.rating_analysis import RatingAnalysisService
from services.fastapi.demand_analysis import DemandAnalysisService
from services.fastapi.daytype_analysis import DayTypeAnalysisService
from services.fastapi.repeat_passenger_analysis import RepeatPassengerAnalysisService
from services.fastapi.target_analysis import TargetAnalysisService
from services.fastapi.rpr_analysis import RPRAnalysisService
from services.fastapi.rpr_factors_analysis import RPRFactorsAnalysisService
from services.fastapi.tourism_business_analysis import TourismBusinessAnalysisService
from services.fastapi.mobility_trends_analysis import MobilityTrendsAnalysisService
from services.fastapi.partnership_analysis import PartnershipAnalysisService
from services.fastapi.data_collection_analysis import DataCollectionAnalysisService
from services.fastapi.ml_satisfaction_prediction import MLSatisfactionPredictionService
from pydantic import BaseModel, Field

router = APIRouter()

@router.get("/analysis/city-performance", tags=["City Analysis"])
async def get_city_performance():
    """
    Get detailed analysis of top and bottom performing cities based on total trips.
    
    Returns:
    - Visualization: Base64 encoded plot comparing top and bottom cities
    - Top Cities: Details of top 3 performing cities
    - Bottom Cities: Details of bottom 3 performing cities
    - Overall Statistics: Summary statistics for all cities
    """
    try:
        analysis_results = CityPerformanceService.analyze_top_bottom_cities()
        return JSONResponse(content=analysis_results)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while analyzing city performance: {str(e)}"
        )

@router.get("/analysis/city-fares", tags=["City Analysis"])
async def get_city_fares():
    """
    Get detailed analysis of city fares and distances.
    
    Returns:
    - Visualization: Scatter plot of average fare vs distance for each city
    - City Metrics: Detailed fare and distance metrics for each city
    - Summary Statistics: Overall fare statistics and rankings
    - Fare Efficiency: Cities ranked by fare per kilometer
    """
    try:
        analysis_results = FareAnalysisService.analyze_city_fares()
        return JSONResponse(content=analysis_results)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while analyzing city fares: {str(e)}"
        )

@router.get("/analysis/city-ratings", tags=["City Analysis"])
async def get_city_ratings():
    """
    Get detailed analysis of city ratings by passenger type.
    
    Returns:
    - Visualization: Heatmap of passenger ratings by city and passenger type
    - Detailed Ratings: Complete rating metrics for each city and passenger type
    - City Rankings: Top and bottom rated cities by both passenger and driver ratings
    - Summary Statistics: Overall rating statistics and breakdowns by passenger type
    """
    try:
        analysis_results = RatingAnalysisService.analyze_city_ratings()
        return JSONResponse(content=analysis_results)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while analyzing city ratings: {str(e)}"
        )

@router.get("/analysis/city-demand", tags=["City Analysis"])
async def get_city_demand():
    """
    Get detailed analysis of monthly demand patterns for each city.
    
    Returns:
    - Visualization: Heatmap of monthly trip distribution by city
    - City Demand Patterns: Peak and low demand months for each city
    - Monthly Distribution: Detailed monthly trip counts for each city
    - Summary Statistics: Overall demand patterns and variability metrics
    """
    try:
        analysis_results = DemandAnalysisService.analyze_monthly_demand()
        return JSONResponse(content=analysis_results)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while analyzing city demand: {str(e)}"
        )

@router.get("/analysis/city-daytype", tags=["City Analysis"])
async def get_city_daytype():
    """
    Get detailed analysis of weekday vs weekend patterns for each city.
    
    Returns:
    - Visualization: Bar plot comparing weekday and weekend distributions
    - City Distributions: Detailed trip metrics for weekdays and weekends
    - Overall Statistics: Aggregated statistics for both day types
    - Pattern Insights: Cities with strongest weekday/weekend biases
    """
    try:
        analysis_results = DayTypeAnalysisService.analyze_weekday_weekend_patterns()
        return JSONResponse(content=analysis_results)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while analyzing day type patterns: {str(e)}"
        )

@router.get("/analysis/city-repeat-passengers", tags=["City Analysis"])
async def get_city_repeat_passengers():
    """
    Get detailed analysis of repeat passenger patterns across cities.
    
    Returns:
    - Visualizations: Heatmap of frequency distribution and bar plot of high-frequency passengers
    - Frequency Distribution: Detailed breakdown of trip frequencies by city
    - High Frequency Analysis: Statistics for passengers with 5+ trips per month
    - Overall Statistics: System-wide repeat passenger metrics
    - City Rankings: Cities with highest and lowest passenger retention
    """
    try:
        analysis_results = RepeatPassengerAnalysisService.analyze_passenger_frequency()
        return JSONResponse(content=analysis_results)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while analyzing repeat passenger patterns: {str(e)}"
        )

@router.get("/analysis/target-achievement", tags=["City Analysis"])
async def get_target_achievement():
    """
    Get detailed analysis of target achievement across cities for key metrics.
    
    Returns:
    - Visualization: Heatmap showing target achievement percentages by city and metric
    - City Performance: Detailed performance metrics for each city
    - Overall Statistics: Summary of target achievement across all cities
    - Top Performers: Cities with highest achievement in each metric
    - Improvement Needed: Cities requiring attention in each metric
    """
    try:
        analysis_results = TargetAnalysisService.analyze_target_achievement()
        return JSONResponse(content=analysis_results)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while analyzing target achievement: {str(e)}"
        )

@router.get("/analysis/rpr-metrics", tags=["City Analysis"])
async def get_rpr_metrics():
    """
    Get detailed analysis of Repeat Passenger Rate (RPR%) metrics by city and month.
    
    Returns:
    - Visualizations: Bar plots for city-wise and monthly RPR%
    - City Analysis: Top/bottom performers and all city metrics
    - Monthly Analysis: Highest/lowest months and all monthly metrics
    - Overall Statistics: System-wide RPR metrics and totals
    """
    try:
        analysis_results = RPRAnalysisService.analyze_rpr()
        return JSONResponse(content=analysis_results)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while analyzing RPR metrics: {str(e)}"
        )

@router.get("/analysis/rpr-factors", tags=["City Analysis"])
async def get_rpr_factors():
    """
    Analyze factors influencing Repeat Passenger Rate (RPR%) across cities.
    
    Returns:
    - Visualizations: Correlation heatmap and factor scatter plots
    - Correlation Analysis: Strong positive/negative correlations with RPR%
    - City Factor Analysis: Detailed metrics and impact scores by city
    - Key Findings: Most significant positive and negative factors
    """
    try:
        analysis_results = RPRFactorsAnalysisService.analyze_rpr_factors()
        return JSONResponse(content=analysis_results)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while analyzing RPR factors: {str(e)}"
        )

@router.get("/analysis/tourism-business", tags=["City Analysis"])
async def get_tourism_business_patterns():
    """
    Analyze tourism vs. business demand patterns across cities.
    
    Returns:
    - Visualizations: Weekend/weekday ratio plot and monthly patterns heatmap
    - City Classifications: Tourism-heavy vs business-heavy cities
    - Tourism Metrics: Key statistics about tourism patterns
    - Seasonal Insights: Peak months and seasonal patterns
    - Marketing Recommendations: City-specific marketing focus
    """
    try:
        analysis_results = TourismBusinessAnalysisService.analyze_tourism_business_patterns()
        return JSONResponse(content=analysis_results)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while analyzing tourism vs business patterns: {str(e)}"
        )

@router.get("/analysis/mobility-trends")
async def analyze_mobility_trends():
    """
    Analyze emerging mobility trends and potential impact of EV adoption
    """
    try:
        return MobilityTrendsAnalysisService.analyze_mobility_trends()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while analyzing mobility trends: {str(e)}"
        )

@router.get("/analysis/partnerships")
async def analyze_partnership_opportunities():
    """
    Analyze potential partnership opportunities with local businesses
    """
    try:
        return PartnershipAnalysisService.analyze_partnership_opportunities()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while analyzing partnership opportunities: {str(e)}"
        )

@router.get("/analysis/data-collection")
async def analyze_data_collection_needs():
    """
    Analyze current data coverage and recommend additional data collection needs
    """
    try:
        return DataCollectionAnalysisService.analyze_data_collection_needs()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while analyzing data collection needs: {str(e)}"
        )

class SatisfactionPredictionInput(BaseModel):
    distance_travelled_km: float = Field(alias='distance_travelled(km)')
    fare_amount: float
    passenger_rating: float
    driver_rating: float

    class Config:
        allow_population_by_field_name = True
        json_schema_extra = {
            "example": {
                "distance_travelled(km)": 15.5,
                "fare_amount": 250.0,
                "passenger_rating": 4.5,
                "driver_rating": 4.8
            }
        }

@router.post("/ml/train-satisfaction-model")
async def train_satisfaction_model():
    """
    Train the customer satisfaction prediction model
    """
    try:
        return MLSatisfactionPredictionService.train_model()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while training the model: {str(e)}"
        )

@router.post("/ml/predict-satisfaction")
async def predict_satisfaction(prediction_input: SatisfactionPredictionInput):
    """
    Predict customer satisfaction for given trip parameters
    """
    try:
        input_dict = {
            'distance_travelled(km)': prediction_input.distance_travelled_km,
            'fare_amount': prediction_input.fare_amount,
            'passenger_rating': prediction_input.passenger_rating,
            'driver_rating': prediction_input.driver_rating
        }
        return MLSatisfactionPredictionService.predict_satisfaction(input_dict)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while making prediction: {str(e)}"
        )