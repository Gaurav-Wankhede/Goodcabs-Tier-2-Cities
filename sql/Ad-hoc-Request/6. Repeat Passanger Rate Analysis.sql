WITH MonthlyRates AS (
    SELECT 
        dc.city_name,
        dd.month_name,
        fps.total_passengers,
        fps.repeat_passengers,
        (fps.repeat_passengers / fps.total_passengers) * 100 AS monthly_repeat_passenger_rate
    FROM 
        trips_db.fact_passenger_summary fps
    JOIN 
        trips_db.dim_city dc ON fps.city_id = dc.city_id
    JOIN 
        trips_db.dim_date dd ON fps.month = dd.start_of_month
),
CityWideRates AS (
    SELECT 
        dc.city_name,
        SUM(fps.total_passengers) AS total_city_passengers,
        SUM(fps.repeat_passengers) AS total_city_repeat_passengers,
        (SUM(fps.repeat_passengers) / SUM(fps.total_passengers)) * 100 AS city_repeat_passenger_rate
    FROM 
        trips_db.fact_passenger_summary fps
    JOIN 
        trips_db.dim_city dc ON fps.city_id = dc.city_id
    GROUP BY 
        dc.city_name
)
SELECT 
    mr.city_name,
    mr.month_name,
    mr.total_passengers,
    mr.repeat_passengers,
    mr.monthly_repeat_passenger_rate,
    cwr.city_repeat_passenger_rate
FROM 
    MonthlyRates mr
JOIN 
    CityWideRates cwr ON mr.city_name = cwr.city_name;