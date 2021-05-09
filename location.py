import geocoder  # need to run pip install geocoder

g = geocoder.ip("me")
print(g.latlng)
user_latitude = g.latlng[0]
user_longitude = g.latlng[1]

print(user_latitude)
print(type(user_longitude))
