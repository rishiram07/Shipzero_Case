-- Task 1 - Activity Monitoring (DuckDB)
-- Run: python src/run_task1.py

-- Load the CSV files (';' delimiter, decimal comma)
CREATE OR REPLACE VIEW vehicles AS
SELECT *
FROM read_csv('data/vehicles.csv',
              delim = ';',
              header = true,
              columns = {'vehicle_id': 'INTEGER',
                         'licence_plate': 'VARCHAR'});

CREATE OR REPLACE VIEW trackings AS
SELECT *
FROM read_csv('data/trackings.csv',
              delim = ';',
              header = true,
              decimal_separator = ',',
              columns = {'vehicle_id': 'INTEGER',
                         'time': 'VARCHAR',
                         'lat': 'DOUBLE',
                         'lng': 'DOUBLE'});


-- Task 1a: active = vehicle has at least one tracking row
-- Start from vehicles so vehicles without tracking data are kept
SELECT
    v.vehicle_id,
    EXISTS (
        SELECT 1
        FROM trackings t
        WHERE t.vehicle_id = v.vehicle_id
    ) AS active_boolean
FROM vehicles v
ORDER BY v.vehicle_id;


-- Task 1b: vehicle with the most tracking points
-- RANK() returns all vehicles if there is a tie
WITH point_counts AS (
    SELECT
        vehicle_id,
        COUNT(*) AS number_of_tracking_points
    FROM trackings
    GROUP BY vehicle_id
),
ranked AS (
    SELECT
        vehicle_id,
        number_of_tracking_points,
        RANK() OVER (ORDER BY number_of_tracking_points DESC) AS rnk
    FROM point_counts
)
SELECT
    vehicle_id,
    number_of_tracking_points
FROM ranked
WHERE rnk = 1;