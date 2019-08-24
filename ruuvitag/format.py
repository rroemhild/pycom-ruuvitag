from ucollections import namedtuple


RuuviTagURL = namedtuple(
    "RuuviTagURL",
    (
        "mac",
        "rssi",
        "format",
        "humidity",
        "temperature",
        "pressure",
        "id",
    ),
)


RuuviTagRAW = namedtuple(
    "RuuviTagRAW",
    (
        "mac",
        "rssi",
        "format",
        "humidity",
        "temperature",
        "pressure",
        "acceleration_x",
        "acceleration_y",
        "acceleration_z",
        "battery_voltage",
        "power_info",
        "movement_counter",
        "measurement_sequence",
    ),
)
