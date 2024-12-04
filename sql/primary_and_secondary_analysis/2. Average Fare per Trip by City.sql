WITH CityFareAnalysis AS (
            SELECT 
                c.city_name,
                ROUND(AVG(ft.fare_amount), 2) as avg_fare,
                ROUND(AVG(ft.distance_travelled_km), 2) as avg_distance,
                ROUND(AVG(ft.fare_amount / NULLIF(ft.distance_travelled_km, 0)), 2) as fare_per_km
            FROM fact_trips ft
            JOIN dim_city c ON ft.city_id = c.city_id
            WHERE ft.distance_travelled_km > 0
            GROUP BY c.city_name
        )
        SELECT 
            city_name,
            avg_fare,
            avg_distance,
            fare_per_km,
            RANK() OVER (ORDER BY avg_fare DESC) as fare_rank_desc,
            RANK() OVER (ORDER BY avg_fare ASC) as fare_rank_asc
        FROM CityFareAnalysis
        ORDER BY avg_fare DESC;