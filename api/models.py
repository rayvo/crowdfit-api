from django.db import models

# Create your models here.
from api import utils


class BLEPostData(object):

    def __init__(self, data):
        self.timestamp = data.get('timestamp', None)
        self.type = data.get('type', None)
        self.mac = data.get('mac', None)
        self.gatewayFree = data.get('gatewayFree', None)
        self.gatewayLoad = data.get('gatewayLoad', None)
        self.bleName = data.get('bleName', None)
        self.rssi = data.get('rssi', None)
        self.rawData = data.get('rawData', None)

    def __set_name__(self, owner, name):
        self.name = name

    def is_gateway(self):
        return utils.is_gateway(self)


class GateWayData(object):

    def __init__(self, ble_post_data, apt_device):
        self.ble_post_data = ble_post_data
        self.apt_device = apt_device

    def __set_name__(self, owner, name):
        self.name = name


class UserDeviceData(object):

    def __init__(self, ble_post_data, user_device):
        self.ble_post_data = ble_post_data
        self.user_device = user_device

    def __set_name__(self, owner, name):
        self.name = name
