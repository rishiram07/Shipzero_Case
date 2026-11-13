# Fleet Tracking Case Study

**Author:** Rishiram Senthil Ganesh

Two tasks on truck tracking data:

| Task | Question | Tool |
|---|---|---|
| 1 – Activity Monitoring | a) Which vehicles are active/inactive? b) Which vehicle has the most tracking points? | SQL (DuckDB) |
| 2 – Geo Tracing | When did each vehicle leave the location polygon for the first time? | Python (pandas + shapely) |

---

## 1. Project structure

```
fleet-case-study/
├── data/                              # raw input files from the client (never modified)
│   ├── vehicles.csv                   #   vehicle_id;licence_plate
│   ├── trackings.csv                  #   vehicle_id;time;lat;lng
│   └── location.geojson               #   polygon of the location
├── sql/
│   └── task1_activity_monitoring.sql  # Task 1: the actual SQL answer
├── src/
│   ├── run_task1.py                   # runs the SQL file with DuckDB, prints and saves results
│   ├── task2_geo_tracing.py           # Task 2: first exit per vehicle
│   └── make_map.py                    # bonus: interactive map of routes and exits
├── output/                            # generated results (created when you run the scripts)
├── .vscode/                           # VS Code settings, recommended extensions, run buttons
├── requirements.txt                   # Python packages
├── .gitignore
└── README.md
```

**Why this layout?** It separates input (`data/`), logic (`sql/`, `src/`) and results (`output/`).
Anyone can clone the repo, run two commands and get the same results, and the raw data is never
overwritten. The Task 1 answer is a real `.sql` file, because the task asks for "a SQL script".

---

## 2. Data observations (found before writing any logic)

| Observation | Why it matters |
|---|---|
| Files use `;` as delimiter and a **decimal comma** (`48,557`) | Default CSV readers would read lat/lng as text or split them wrongly. Both readers declare this explicitly. |
| Timestamps look like `2021-01-12 01:04:07.6700000 +01:00` (7 fractional digits + UTC offset) | Parsed as timezone-aware, shown in Europe/Berlin time. |
| GeoJSON coordinates are `[lng, lat]` | Points must be tested as (lng, lat). Swapping them is the classic bug: every point ends up "outside". |
| 5 vehicles in `vehicles.csv`, tracking data only for vehicles 0 and 1 | Vehicles 2, 3 and 4 are inactive. This is why Task 1a must start from `vehicles`. |
| The device often sends the same position twice within a second | Affects what "individual tracking point" means (see Task 1b). |
| No tracking rows for unknown vehicle_ids | No orphan data to handle. |

---

## 3. Results

### Task 1a – Active / inactive vehicles
| vehicle_id | active_boolean |
|---|---|
| 0 | true |
| 1 | true |
| 2 | false |
| 3 | false |
| 4 | false |

### Task 1b – Most tracking points
| vehicle_id | number_of_tracking_points |
|---|---|
| 1 | 320 |

**Note on "individual":** vehicle 1 has the most rows (320 vs 298). Counting **distinct positions**
instead, vehicle 0 is ahead (231 vs 224), because vehicle 1 sends more duplicate pings while standing
still. The main answer uses raw rows (each row is one recorded tracking point). The alternative
count is in the data-quality section of the SQL file, so the definition can be discussed with the client.

### Task 2 – First exit from the location
| vehicle_id | starts inside? | last point inside | first point outside (= exit time) |
|---|---|---|---|
| 0 | no | 2021-01-12 11:17:24 | **2021-01-12 11:22:24** |
| 1 | no | 2021-01-12 11:23:18 | **2021-01-12 11:28:18** |

Both vehicles start outside, drive into the polygon, then leave it once. The result doesn't change when
2 or 3 consecutive outside points are required, so these are real exits, not GPS noise at the border.

---

## 4. Approach and reasoning

### Task 1 (SQL)
- **1a:** `FROM vehicles` + `EXISTS (... trackings ...)`. Starting from the vehicle list keeps vehicles
  with zero tracking rows. An `INNER JOIN` would silently drop exactly the inactive ones.
  `EXISTS` returns a real boolean and can never duplicate rows.
- **1b:** `GROUP BY` + `COUNT(*)`, then `RANK()` instead of `LIMIT 1`, so a tie for first place
  returns all tied vehicles instead of an arbitrary one.

### Task 2 (Python)
1. Tag each point inside/outside the polygon (`shapely.covers`, boundary counts as inside).
2. Sort each vehicle's points by time and compare each point with the previous one.
3. **Exit = previous point inside AND current point outside.**
   A vehicle that starts outside has no such transition until it has entered first, so the
   "may start outside" rule is handled with no special case.
4. Keep the earliest exit per vehicle. Vehicles that never leave get a clear status instead of disappearing.

**Assumptions** (stated so they can be challenged):
- Exit time = first point recorded outside. The last inside time is also reported, because the actual
  crossing happened somewhere between the two.
- `MIN_CONSECUTIVE_OUTSIDE` (default 1) can be raised to ignore single GPS jumps across the border.

---

## 5. How to run

```bash
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt

python src/run_task1.py          # Task 1
python src/task2_geo_tracing.py  # Task 2
python src/make_map.py           # bonus map -> output/task2_map.html
```

---

## 6. Why DuckDB?

- Runs SQL **directly on CSV files**: no database server, no import step, no passwords.
- One `pip install`, works the same on Windows, macOS and Linux.
- Standard SQL. The queries in sections 1–3 of the SQL file run unchanged on PostgreSQL, SQLite or BigQuery.
- Explicit control over the German CSV format (`delim=';'`, `decimal_separator=','`).

**Alternatives:** PostgreSQL (+ PostGIS for Task 2) is the production-grade choice but needs a server
and a data import. SQLite is built into Python but has no proper boolean type and a weaker CSV import.
Either would work for the Task 1 logic.
