SELECT 
    dc.city_name,
    dd.month_name,
    COUNT(ft.trip_id) AS actual_trips,
    mtt.total_target_trips AS target_trips,
    CASE 
        WHEN COUNT(ft.trip_id) > mtt.total_target_trips THEN 'Above Target'
        ELSE 'Below Target'
    END AS performance_status,
    ((COUNT(ft.trip_id) - mtt.total_target_trips) / mtt.total_target_trips) * 100 AS percentage_difference
FROM 
    trips_db.fact_trips ft
JOIN 
    trips_db.dim_city dc ON ft.city_id = dc.city_id
JOIN 
    trips_db.dim_date dd ON ft.date = dd.date
JOIN 
    targets_db.monthly_target_trips mtt ON dc.city_id = mtt.city_id AND dd.start_of_month = mtt.month
GROUP BY 
    dc.city_name, dd.month_name, mtt.total_target_trips;