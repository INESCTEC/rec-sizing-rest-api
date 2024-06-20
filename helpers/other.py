import math
def haversine(coord1, coord2):
    """
    Calculate the great-circle distance between two points on the Earth given their latitude and longitude.
    :param coord1: Tuple of (latitude, longitude) for the first point.
    :param coord2: Tuple of (latitude, longitude) for the second point.
    :return: Distance in kilometers.
    """
    R = 6371  # Radius of the Earth in km

    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c  # Output distance in km
    return distance