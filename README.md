# Fleet Tracking Case Study

**Author:** Rishiram Senthil Ganesh

| Task | Question | Solution |
|---|---|---|
| 1 – Activity Monitoring | a) Which vehicles are active? b) Which has the most tracking points? | SQL (DuckDB) |
| 2 – Geo Tracing | When did each vehicle first leave the location? | Python (pandas + shapely) |

## Project structure

```
data/      vehicles.csv, trackings.csv, location.geojson   (input)
sql/       task1_activity_monitoring.sql                   (Task 1)
src/       run_task1.py                                    (runs the SQL file)
           task2_geo_tracing.py                            (Task 2)
output/    result CSV files (created when you run the scripts)
```

## How to run

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python src/run_task1.py            # Task 1
python src/task2_geo_tracing.py    # Task 2
```

## Results

**Task 1a – Active / inactive vehicles**

| vehicle_id | active_boolean |
|---|---|
| 0 | true |
| 1 | true |
| 2 | false |
| 3 | false |
| 4 | false |

**Task 1b – Most tracking points**

| vehicle_id | number_of_tracking_points |
|---|---|
| 1 | 320 |

**Task 2 – First exit from the location**

| vehicle_id | first_exit_time |
|---|---|
| 0 | 2021-01-12 11:22:24 |
| 1 | 2021-01-12 11:28:18 |

Only vehicles 0 and 1 have tracking data, so only they appear in Task 2.

## Approach

**Task 1**
- **1a:** Start from `vehicles` and check with `EXISTS` whether tracking rows exist. This keeps vehicles with no data (an INNER JOIN would drop them).
- **1b:** Count rows per vehicle and use `RANK()` so a tie returns all top vehicles.

**Task 2**
1. Mark each tracking point as inside or outside the polygon.
2. Sort points by vehicle and time.
3. Exit = previous point inside **and** current point outside.
4. Keep the first exit per vehicle.

A vehicle that starts outside must enter before it can leave, so this rule handles it automatically.

## Assumptions

- Exit time = time of the first point recorded outside the polygon.
- A point exactly on the border counts as inside.
- "Tracking point" = one row in `trackings.csv`. Counting only distinct positions would change 1b (vehicle 0: 231, vehicle 1: 224), because vehicle 1 sends duplicate pings while parked.

## Data notes

- Files use `;` as the delimiter and a decimal comma (`48,557`). Both are set explicitly when reading.
- GeoJSON coordinates are `[lng, lat]`, so points are tested in that order.
- Vehicles 2, 3 and 4 have no tracking data.
