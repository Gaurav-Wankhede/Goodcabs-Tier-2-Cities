WITH TargetPerformance AS (
    SELECT 
        mtt.city_id,
        mtt.month,
        mtt.total_target_trips,
        mtnp.target_new_passengers,
        ctp.target_avg_passenger_rating
    FROM 
        monthly_target_trips mtt
    JOIN 
        monthly_target_new_passengers mtnp 
        ON mtt.month = mtnp.month AND mtt.city_id = mtnp.city_id
    JOIN 
        city_target_passenger_rating ctp 
        ON mtt.city_id = ctp.city_id
)

SELECT 
    city_id,
    month,
    total_target_trips,
    target_new_passengers,
    target_avg_passenger_rating,
    
    -- Target Achievement Categories
    CASE 
        WHEN total_target_trips > (SELECT AVG(total_target_trips) FROM TargetPerformance) THEN 'High Ambition'
        WHEN total_target_trips < (SELECT AVG(total_target_trips) FROM TargetPerformance) THEN 'Low Ambition'
        ELSE 'Average Ambition'
    END AS trips_target_category,
    
    CASE 
        WHEN target_new_passengers > (SELECT AVG(target_new_passengers) FROM TargetPerformance) THEN 'High Growth Target'
        WHEN target_new_passengers < (SELECT AVG(target_new_passengers) FROM TargetPerformance) THEN 'Low Growth Target'
        ELSE 'Average Growth Target'
    END AS new_passengers_target_category,
    
    CASE 
        WHEN target_avg_passenger_rating > (SELECT AVG(target_avg_passenger_rating) FROM TargetPerformance) THEN 'High Service Quality Target'
        WHEN target_avg_passenger_rating < (SELECT AVG(target_avg_passenger_rating) FROM TargetPerformance) THEN 'Low Service Quality Target'
        ELSE 'Average Service Quality Target'
    END AS rating_target_category
FROM 
    TargetPerformance
ORDER BY 
    city_id, 
    month;