"""Different environment settings."""

# TODO: Add correct objects
LOCATION_TYPE_MAP = {
    "floor": {"color": "gray", "gray_color": "gray", "mesh": "../objects/floor.obj",},
    "rack": {"color": "green", "gray_color": "gray", "mesh": "../objects/rack.obj",},
    "wall": {"color": "black", "gray_color": "black", "mesh": "../objects/floor.obj",},
    "inbound_door": {
        "color": "blue",
        "gray_color": "#222",
        "mesh": "../objects/floor.obj",
    },
    "outbound_door": {
        "color": "orange",
        "gray_color": "#aaa",
        "mesh": "../objects/floor.obj",
    },
    "staging_area": {
        "color": "yellow",
        "gray_color": "#ddd",
        "mesh": "../objects/floor.obj",
    },
    "custome": {"color": "red", "gray_color": "white", "mesh": "../objects/floor.obj",},
}
