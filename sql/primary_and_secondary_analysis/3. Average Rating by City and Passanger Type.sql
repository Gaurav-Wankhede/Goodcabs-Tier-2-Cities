-- Average Passenger and Driver Ratings by City and Passenger Type

WITH RatingAnalysis AS (
    SELECT 
        c.city_name,
        ft.passenger_type,
        
        ROUND(AVG(ft.passenger_rating), 2) AS avg_passenger_rating,
        ROUND(AVG(ft.driver_rating), 2) AS avg_driver_rating,
        
        COUNT(*) AS total_trips,
        
        RANK() OVER (ORDER BY AVG(ft.passenger_rating) DESC) AS passenger_rating_rank,
        RANK() OVER (ORDER BY AVG(ft.driver_rating) DESC) AS driver_rating_rank
    
    FROM 
        fact_trips ft
    JOIN 
        dim_city c ON ft.city_id = c.city_id
    
    GROUP BY 
        c.city_name, 
        ft.passenger_type
)

SELECT 
    city_name,
    passenger_type,
    avg_passenger_rating,
    avg_driver_rating,
    total_trips,
    passenger_rating_rank,
    driver_rating_rank
FROM 
    RatingAnalysis
ORDER BY 
    avg_passenger_rating DESC, 
    total_trips DESC;