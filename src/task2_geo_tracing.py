"""
Task 2 - Geo Tracing
Finds the first time each vehicle leaves the location polygon.
Exit = previous point inside AND current point outside.
Exit time = time of the first point outside the polygon.
"""

import json
from pathlib import Path

import pandas as pd
import shapely
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"


def load_polygon(path):
    # GeoJSON coordinates are [lng, lat]
    with open(path, encoding="utf-8") as f:
        geojson = json.load(f)
    return shape(geojson["features"][0]["geometry"])


def load_trackings(path):
    # ';' delimiter and decimal comma
    df = pd.read_csv(path, sep=";", decimal=",")
    df["time"] = pd.to_datetime(df["time"], utc=True).dt.tz_convert("Europe/Berlin")
    return df


def tag_inside(df, polygon):
    # True if the point is inside the polygon (border counts as inside)
    df = df.copy()
    points = shapely.points(df["lng"], df["lat"])  # x = lng, y = lat
    df["inside"] = shapely.covers(polygon, points)
    return df


def first_exits(df):
    df = df.sort_values(["vehicle_id", "time"]).reset_index(drop=True)

    # Was the previous point of the same vehicle inside?
    # First point has no previous point -> False (so it can't be an exit)
    prev_inside = df.groupby("vehicle_id")["inside"].shift(1, fill_value=False).astype(bool)
    df["is_exit"] = prev_inside & ~df["inside"]

    # Earliest exit per vehicle
    exits = (
        df[df["is_exit"]]
        .groupby("vehicle_id", as_index=False)
        .first()[["vehicle_id", "time"]]
        .rename(columns={"time": "first_exit_time"})
    )

    # Keep vehicles that never leave (exit time stays empty)
    all_vehicles = df[["vehicle_id"]].drop_duplicates()
    return all_vehicles.merge(exits, on="vehicle_id", how="left")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    polygon = load_polygon(DATA_DIR / "location.geojson")
    trackings = load_trackings(DATA_DIR / "trackings.csv")

    tagged = tag_inside(trackings, polygon)
    result = first_exits(tagged)

    print("\n=== Task 2 - first time each vehicle left the location ===")
    print(result.to_string(index=False))

    result.to_csv(OUTPUT_DIR / "task2_first_exit.csv", index=False)
    print("\nSaved: output/task2_first_exit.csv")


if __name__ == "__main__":
    main()