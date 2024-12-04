SELECT 
    dc.city_name,
    COUNT(ft.trip_id) AS total_trips,
    AVG(ft.fare_amount / ft.distance_travelled_km) AS avg_fare_per_km,
    AVG(ft.fare_amount) AS avg_fare_per_trip,
    (COUNT(ft.trip_id) / (SELECT COUNT(*) FROM trips_db.fact_trips)) * 100 AS percentage_contribution_to_total_trips
FROM 
    trips_db.fact_trips ft
JOIN 
    trips_db.dim_city dc ON ft.city_id = dc.city_id
GROUP BY 
    dc.city_name;