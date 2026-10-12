"""
NIRMAAN AI - Unit Tests: Geospatial Hotspot Clustering & Haversine Distance
"""

import pytest
from src.database.connection import init_db
from src.database.repository import Repository
from src.ml.clustering import run_hotspot_clustering, haversine_distance_meters


def test_haversine_distance():
    # Bengaluru coordinates: distance between Koramangala and Indiranagar (~4.5 km)
    dist = haversine_distance_meters(12.9352, 77.6245, 12.9719, 77.6412)
    assert 4000 < dist < 5500


def test_hotspot_clustering_groups_nearby_reports(tmp_path):
    test_db = tmp_path / "test_cluster.db"
    init_db(test_db)
    repo = Repository(test_db)

    # Add 3 tightly clustered reports in Koramangala (< 100 meters apart)
    repo.create_report("REP-C1", 12.9352, 77.6245, "Koramangala", "plastic")
    repo.create_report("REP-C2", 12.9354, 77.6247, "Koramangala", "organic")
    repo.create_report("REP-C3", 12.9350, 77.6243, "Koramangala", "mixed_trash")

    # Add 1 isolated report in Whitefield (> 10 km away)
    repo.create_report("REP-ISO", 12.9863, 77.7289, "Whitefield", "paper")

    hotspots = run_hotspot_clustering(repo)
    assert len(hotspots) == 1
    assert hotspots[0]["incident_count"] == 3
    assert hotspots[0]["ward_name"] == "Koramangala"
