SELECT 
    dc.city_name,
    SUM(CASE WHEN dtrtd.trip_count = 2 THEN dtrtd.repeat_passenger_count ELSE 0 END) * 100.0 / SUM(dtrtd.repeat_passenger_count) AS "2-Trips",
    SUM(CASE WHEN dtrtd.trip_count = 3 THEN dtrtd.repeat_passenger_count ELSE 0 END) * 100.0 / SUM(dtrtd.repeat_passenger_count) AS "3-Trips",
    SUM(CASE WHEN dtrtd.trip_count = 4 THEN dtrtd.repeat_passenger_count ELSE 0 END) * 100.0 / SUM(dtrtd.repeat_passenger_count) AS "4-Trips",
    SUM(CASE WHEN dtrtd.trip_count = 5 THEN dtrtd.repeat_passenger_count ELSE 0 END) * 100.0 / SUM(dtrtd.repeat_passenger_count) AS "5-Trips",
    SUM(CASE WHEN dtrtd.trip_count = 6 THEN dtrtd.repeat_passenger_count ELSE 0 END) * 100.0 / SUM(dtrtd.repeat_passenger_count) AS "6-Trips",
    SUM(CASE WHEN dtrtd.trip_count = 7 THEN dtrtd.repeat_passenger_count ELSE 0 END) * 100.0 / SUM(dtrtd.repeat_passenger_count) AS "7-Trips",
    SUM(CASE WHEN dtrtd.trip_count = 8 THEN dtrtd.repeat_passenger_count ELSE 0 END) * 100.0 / SUM(dtrtd.repeat_passenger_count) AS "8-Trips",
    SUM(CASE WHEN dtrtd.trip_count = 9 THEN dtrtd.repeat_passenger_count ELSE 0 END) * 100.0 / SUM(dtrtd.repeat_passenger_count) AS "9-Trips",
    SUM(CASE WHEN dtrtd.trip_count = 10 THEN dtrtd.repeat_passenger_count ELSE 0 END) * 100.0 / SUM(dtrtd.repeat_passenger_count) AS "10-Trips"
FROM 
    trips_db.dim_repeat_trip_distribution dtrtd
JOIN 
    trips_db.dim_city dc ON dtrtd.city_id = dc.city_id
GROUP BY 
    dc.city_name;