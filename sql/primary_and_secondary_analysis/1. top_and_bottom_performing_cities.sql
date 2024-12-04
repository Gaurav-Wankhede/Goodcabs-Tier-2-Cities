WITH CityTrips AS (
    SELECT 
        c.city_name,
        COUNT(*) as total_trips,
        RANK() OVER (ORDER BY COUNT(*) DESC) as top_rank,
        RANK() OVER (ORDER BY COUNT(*)) as bottom_rank
    FROM fact_trips ft
    JOIN dim_city c ON ft.city_id = c.city_id
    GROUP BY c.city_name
)
SELECT 
    city_name,
    total_trips,
    CASE 
        WHEN top_rank <= 3 THEN 'Top 3'
        WHEN bottom_rank <= 3 THEN 'Bottom 3'
    END as performance_category
FROM CityTrips
WHERE top_rank <= 3 OR bottom_rank <= 3
ORDER BY total_trips DESC;