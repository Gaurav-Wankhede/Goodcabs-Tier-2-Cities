WITH MonthlyRevenue AS (
    SELECT 
        dc.city_name,
        dd.month_name,
        SUM(ft.fare_amount) AS monthly_revenue
    FROM 
        trips_db.fact_trips ft
    JOIN 
        trips_db.dim_city dc ON ft.city_id = dc.city_id
    JOIN 
        trips_db.dim_date dd ON ft.date = dd.date
    GROUP BY 
        dc.city_name, dd.month_name
),
CityTotalRevenue AS (
    SELECT 
        city_name,
        SUM(monthly_revenue) AS total_revenue
    FROM 
        MonthlyRevenue
    GROUP BY 
        city_name
),
HighestRevenueMonth AS (
    SELECT 
        mr.city_name,
        mr.month_name AS highest_revenue_month,
        mr.monthly_revenue,
        (mr.monthly_revenue / ctr.total_revenue) * 100 AS percentage_contribution
    FROM 
        MonthlyRevenue mr
    JOIN 
        CityTotalRevenue ctr ON mr.city_name = ctr.city_name
    WHERE 
        (mr.city_name, mr.monthly_revenue) IN (
            SELECT 
                city_name, MAX(monthly_revenue)
            FROM 
                MonthlyRevenue
            GROUP BY 
                city_name
        )
)
SELECT 
    city_name,
    highest_revenue_month,
    monthly_revenue AS revenue,
    percentage_contribution
FROM 
    HighestRevenueMonth;