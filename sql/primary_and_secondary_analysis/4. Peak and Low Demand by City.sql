WITH MonthlyTripCounts AS (
    SELECT 
        c.city_name,
        EXTRACT(MONTH FROM ft.date) AS month_number,
        dd.month_name,
        COUNT(*) AS total_trips,
        RANK() OVER (PARTITION BY c.city_name ORDER BY COUNT(*) DESC) AS peak_rank,
        RANK() OVER (PARTITION BY c.city_name ORDER BY COUNT(*) ASC) AS low_rank
    FROM 
        fact_trips ft
    JOIN 
        dim_city c ON ft.city_id = c.city_id
    JOIN 
        dim_date dd ON ft.date = dd.date
    GROUP BY 
        c.city_name, 
        EXTRACT(MONTH FROM ft.date),
        dd.month_name
)

SELECT 
    city_name,
    MAX(CASE WHEN peak_rank = 1 THEN month_name END) AS peak_demand_month,
    MAX(CASE WHEN peak_rank = 1 THEN total_trips END) AS peak_trips,
    MAX(CASE WHEN low_rank = 1 THEN month_name END) AS low_demand_month,
    MAX(CASE WHEN low_rank = 1 THEN total_trips END) AS low_trips
FROM 
    MonthlyTripCounts
GROUP BY 
    city_name
ORDER BY 
    peak_trips DESC;