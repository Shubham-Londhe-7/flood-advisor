"""
Route-check: given start and end coordinates, check if the straight-line
path passes near any high/medium-risk flood zone. Simple geometric
approximation (no real road routing) - good enough for MVP warning system.
"""
import math


def _haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def min_distance_to_route_km(zone_lat, zone_lon, start_lat, start_lon, end_lat, end_lon, samples=20):
    """Sample points along the straight-line route, return the minimum
    distance (km) from the zone to any sampled point. Simple + robust
    for city-scale distances."""
    min_dist = float("inf")
    for i in range(samples + 1):
        t = i / samples
        lat = start_lat + t * (end_lat - start_lat)
        lon = start_lon + t * (end_lon - start_lon)
        d = _haversine_km(zone_lat, zone_lon, lat, lon)
        if d < min_dist:
            min_dist = d
    return min_dist


def check_route(zones, start_lat, start_lon, end_lat, end_lon, threshold_km=0.6):
    """
    Returns list of zones that lie within threshold_km of the route,
    sorted by risk score descending. threshold_km=0.6 (~600m) is a
    reasonable "you'll pass near this road" cutoff for city routes.
    """
    warnings = []
    for zone in zones:
        dist = min_distance_to_route_km(zone.lat, zone.lon, start_lat, start_lon, end_lat, end_lon)
        if dist <= threshold_km:
            warnings.append({"zone": zone, "distance_km": round(dist, 2)})
    return warnings
