import geocoder  # need to run pip install geocoder
from timezonefinder import (
    TimezoneFinder,
)  # need to install pip install timezonefinder[numba] # also installs numba -> x100 speedup


def my_timezone():
    g = geocoder.ip("me")
    print(g.latlng)
    user_latitude = g.latlng[0]
    user_longitude = g.latlng[1]
    tf = TimezoneFinder()
    timezone = tf.timezone_at(lng=user_longitude, lat=user_latitude)
    return timezone
