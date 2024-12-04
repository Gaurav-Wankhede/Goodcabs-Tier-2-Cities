WITH RepeatPassengerTrips AS (
    SELECT 
        c.city_name,
        COUNT(*) AS total_repeat_trips,
        COUNT(DISTINCT ft.trip_id) AS unique_trips,
        COUNT(DISTINCT ft.trip_id) AS trip_frequency
    FROM 
        fact_trips ft
    JOIN 
        dim_city c ON ft.city_id = c.city_id
    WHERE 
        ft.passenger_type = 'repeat'
    GROUP BY 
        c.city_name,
        ft.trip_id
)

SELECT 
    city_name,
    trip_frequency,
    COUNT(*) AS passengers_at_this_frequency,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY city_name), 2) AS percentage_of_repeat_passengers
FROM 
    RepeatPassengerTrips
GROUP BY 
    city_name, 
    trip_frequency
ORDER BY 
    city_name, 
    trip_frequency;