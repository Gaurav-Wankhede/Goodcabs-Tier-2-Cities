WITH RepeatTripFrequency AS (
    SELECT 
        c.city_name,
        rtd.trip_count,
        rtd.repeat_passenger_count,
        SUM(rtd.repeat_passenger_count) OVER (PARTITION BY c.city_name) AS total_repeat_passengers,
        ROUND(rtd.repeat_passenger_count * 100.0 / SUM(rtd.repeat_passenger_count) OVER (PARTITION BY c.city_name), 2) AS percentage
    FROM 
        dim_repeat_trip_distribution rtd
    JOIN 
        dim_city c ON rtd.city_id = c.city_id
)

SELECT 
    city_name,
    trip_count,
    repeat_passenger_count,
    total_repeat_passengers,
    percentage
FROM 
    RepeatTripFrequency
ORDER BY 
    city_name, 
    CAST(SUBSTRING(trip_count, 1, 1) AS UNSIGNED)