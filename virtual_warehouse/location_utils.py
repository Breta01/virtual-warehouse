"""Module for working with locations."""


def cluster_locations(locations: dict) -> dict:
    """Cluster locations which appears on same location.

    Args:
        locations (dict): Dictionary mapping IDs to location class.

    Returns:
        dict: Dictionary mapping (x, y) coord tuple to list of locations.
    """
    coord_to_locations = {}

    for key, loc in locations.items():
        if not loc.get_2d() in coord_to_locations:
            coord_to_locations[loc.get_2d()] = []
        coord_to_locations[loc.get_2d()].append(key)

    return coord_to_locations
