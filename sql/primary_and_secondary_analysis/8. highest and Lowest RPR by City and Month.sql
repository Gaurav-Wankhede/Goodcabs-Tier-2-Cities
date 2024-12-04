-- Part 1: Repeat Passenger Rate by City
SELECT 
    city_id,
    month,
    total_passengers,
    new_passengers,
    repeat_passengers,
    ROUND(
        (repeat_passengers * 100.0) / NULLIF(total_passengers, 0), 
        2
    ) AS repeat_passenger_rate,
    RANK() OVER (ORDER BY repeat_passengers DESC) AS city_rpr_rank_desc,
    RANK() OVER (ORDER BY repeat_passengers ASC) AS city_rpr_rank_asc
FROM 
    fact_passenger_summary
ORDER BY 
    repeat_passenger_rate DESC;

-- Part 2: Repeat Passenger Rate by Month
SELECT 
    month,
    ROUND(
        SUM(repeat_passengers) * 100.0 / NULLIF(SUM(total_passengers), 0), 
        2
    ) AS avg_repeat_passenger_rate,
    RANK() OVER (ORDER BY SUM(repeat_passengers) DESC) AS month_rpr_rank_desc,
    RANK() OVER (ORDER BY SUM(repeat_passengers) ASC) AS month_rpr_rank_asc
FROM 
    fact_passenger_summary
GROUP BY 
    month
ORDER BY 
    avg_repeat_passenger_rate DESC;