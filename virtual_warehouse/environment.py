"""Different environment settings."""

# TODO: Add correct objects
LOCATION_TYPE_MAP = {
    "floor": {"color": "gray", "gray_color": "gray", "mesh": ":/objects/floor.obj",},
    "rack": {"color": "#62ca5f", "gray_color": "gray", "mesh": ":/objects/rack.obj",},
    "wall": {"color": "black", "gray_color": "black", "mesh": ":/objects/floor.obj",},
    "inbound_door": {
        "color": "#fde724",
        "gray_color": "#222",
        "mesh": ":/objects/floor.obj",
    },
    "outbound_door": {
        "color": "#fd8a24",
        "gray_color": "#aaa",
        "mesh": ":/objects/floor.obj",
    },
    "staging_area": {
        "color": "#2c728e",
        "gray_color": "#ddd",
        "mesh": ":/objects/floor.obj",
    },
    "custom": {
        "color": "#ca5f5f",
        "gray_color": "white",
        "mesh": ":/objects/floor.obj",
    },
}
