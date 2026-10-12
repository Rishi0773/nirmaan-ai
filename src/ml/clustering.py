"""
NIRMAAN AI - Geospatial Hotspot Clustering Engine
Implements spatial aggregation using DBSCAN (Haversine distance)
to identify recurring garbage blackspots across municipal wards.
Pure-NumPy vectorized implementation for fast, reliable, and zero-DLL dependency execution.
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from collections import deque

from src.config import HOTSPOT_CLUSTER_RADIUS_METERS, MIN_SAMPLES_CLUSTER
from src.database.repository import Repository

EARTH_RADIUS_METERS = 6371000.0


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two GPS coordinates in meters."""
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)

    a = (np.sin(delta_phi / 2.0) ** 2 +
         np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * np.arctan2(np.sqrt(a), np.sqrt(1.0 - a))
    return float(EARTH_RADIUS_METERS * c)


def compute_pairwise_haversine_matrix(coords: np.ndarray) -> np.ndarray:
    """Computes pairwise distance matrix in meters across all coordinates."""
    n = len(coords)
    dist_matrix = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i + 1, n):
            d = haversine_distance_meters(coords[i, 0], coords[i, 1], coords[j, 0], coords[j, 1])
            dist_matrix[i, j] = d
            dist_matrix[j, i] = d
    return dist_matrix


def dbscan_haversine_clustering(coords: np.ndarray, eps_meters: float, min_samples: int) -> np.ndarray:
    """
    Exact, pure-NumPy DBSCAN implementation using Haversine distance.
    Guarantees fast, robust spatial clustering without external C-extension risks.
    """
    n = len(coords)
    if n == 0:
        return np.array([], dtype=int)

    dist_mat = compute_pairwise_haversine_matrix(coords)
    labels = np.full(n, -1, dtype=int)
    visited = np.zeros(n, dtype=bool)
    cluster_id = 0

    for i in range(n):
        if visited[i]:
            continue
        visited[i] = True

        # Find neighbors within eps_meters
        neighbors = np.where(dist_mat[i] <= eps_meters)[0]

        if len(neighbors) < min_samples:
            labels[i] = -1  # Noise
        else:
            labels[i] = cluster_id
            queue = deque([idx for idx in neighbors if idx != i])

            while queue:
                curr = queue.popleft()
                if not visited[curr]:
                    visited[curr] = True
                    curr_neighbors = np.where(dist_mat[curr] <= eps_meters)[0]
                    if len(curr_neighbors) >= min_samples:
                        for cn in curr_neighbors:
                            if cn not in queue and not visited[cn]:
                                queue.append(cn)

                if labels[curr] == -1:
                    labels[curr] = cluster_id

            cluster_id += 1

    return labels


def run_hotspot_clustering(repo: Repository) -> List[Dict[str, Any]]:
    """
    Retrieves all reports, runs DBSCAN clustering over latitude and longitude,
    re-populates the hotspots table, and links reports to clusters.
    """
    reports = repo.get_all_reports()
    if not reports:
        return []

    # Filter out reports with invalid/missing coordinates
    valid_reports = [r for r in reports if r["latitude"] and r["longitude"]]
    if len(valid_reports) < MIN_SAMPLES_CLUSTER:
        return []

    coords = np.array([[r["latitude"], r["longitude"]] for r in valid_reports])
    labels = dbscan_haversine_clustering(
        coords,
        eps_meters=HOTSPOT_CLUSTER_RADIUS_METERS,
        min_samples=MIN_SAMPLES_CLUSTER
    )

    # Clear existing hotspot associations
    repo.clear_hotspots()
    created_hotspots = []

    unique_labels = set(labels)
    cluster_idx = 1

    for label in unique_labels:
        if label == -1:
            # Noise points (isolated reports) - not recurring clusters
            continue

        cluster_mask = (labels == label)
        cluster_reports = [valid_reports[i] for i in range(len(valid_reports)) if cluster_mask[i]]

        # Compute cluster centroid
        clats = [r["latitude"] for r in cluster_reports]
        clons = [r["longitude"] for r in cluster_reports]
        centroid_lat = float(np.mean(clats))
        centroid_lon = float(np.mean(clons))

        # Compute cluster spread radius (max distance from centroid)
        max_dist = max([
            haversine_distance_meters(centroid_lat, centroid_lon, r["latitude"], r["longitude"])
            for r in cluster_reports
        ], default=50.0)
        radius_meters = max(50.0, min(float(max_dist), 400.0))

        # Metrics
        incident_count = len(cluster_reports)
        severities = [r.get("severity_score") or 50.0 for r in cluster_reports]
        avg_severity = float(np.mean(severities))

        # Recurrence score is scaled by incident frequency and repeat density
        recurrence_score = min(100.0, 25.0 * incident_count + (avg_severity * 0.15))

        # Dominant ward
        wards = [r["ward_name"] for r in cluster_reports if r["ward_name"]]
        dominant_ward = max(set(wards), key=wards.count) if wards else "Bengaluru Urban"

        hotspot_code = f"HS-BLR-{cluster_idx:03d}"
        cluster_idx += 1

        hid = repo.save_hotspot(
            hotspot_code=hotspot_code,
            ward_name=dominant_ward,
            centroid_lat=centroid_lat,
            centroid_lon=centroid_lon,
            radius_meters=round(radius_meters, 1),
            incident_count=incident_count,
            recurrence_score=round(recurrence_score, 1),
            avg_severity=round(avg_severity, 1),
            status="Active"
        )

        for cr in cluster_reports:
            repo.link_hotspot_report(hid, cr["id"])

        created_hotspots.append({
            "id": hid,
            "hotspot_code": hotspot_code,
            "ward_name": dominant_ward,
            "centroid_lat": centroid_lat,
            "centroid_lon": centroid_lon,
            "incident_count": incident_count,
            "recurrence_score": round(recurrence_score, 1),
            "avg_severity": round(avg_severity, 1)
        })

    return created_hotspots
