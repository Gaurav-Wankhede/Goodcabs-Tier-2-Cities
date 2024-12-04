WITH NewPassengers AS (
    SELECT 
        dc.city_name,
        SUM(fps.new_passengers) AS total_new_passengers
    FROM 
        trips_db.fact_passenger_summary fps
    JOIN 
        trips_db.dim_city dc ON fps.city_id = dc.city_id
    GROUP BY 
        dc.city_name
)
SELECT 
    city_name, 
    total_new_passengers,
    CASE 
        WHEN RANK() OVER (ORDER BY total_new_passengers DESC) <= 3 THEN 'Top 3'
        WHEN RANK() OVER (ORDER BY total_new_passengers ASC) <= 3 THEN 'Bottom 3'
        ELSE NULL
    END AS city_category
FROM 
    NewPassengers
ORDER BY 2 DESC;