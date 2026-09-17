from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.throttling import ScopedRateThrottle



class ProductThrottle(UserRateThrottle):
    rate = '10/minute'


