import socket
import numpy as np
import processing
import dsp
from enum import IntEnum

class ClientTypeId(IntEnum):
    LED_STRIP_CLIENT = 1
    CONTROLLER_CLIENT = 2

class Client:
    def __init__(self, config):
        self.config = config
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data):
        self.sock.sendto(processing.process(data, self.config), (self.config.ip, self.config.port))

class LedStripClient(Client):
    def __init__(self, config):
        self.p_filt = dsp.ExpFilter(np.tile(1, (3, config.num_pixels // 2)), alpha_decay=0.1, alpha_rise=0.99)
        self.p = np.tile(1.0, (3, config.num_pixels // 2))
        super().__init__(self, config)

class ControllerClient(Client):
    def __init__(self, config):
        super().__init__(self, config)

    def onConnected(self):
        #TODO server config
        server_config = ""
        self.sock.sendto(server_config, (self.ip, self.port))

class ClientConfig:
    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.name = name

class LedStripConfig(ClientConfig):
    def __init__(self, ip, port, name, num_pixels, sigma, color, min_freq, max_freq):
        self.num_pixels = num_pixels
        self.sigma = sigma
        self.color = color
        self.min_freq = min_freq
        self.max_freq = max_freq
        super().__init__(self, ip, port, name)
   
    @staticmethod
    def object_decoder(self, obj):
        if '__type__' in obj and obj['__type__'] == 'LedStripConfig':
            return LedStripConfig(obj['ip'], obj['port'], obj['name'], obj['num_pixels'], obj['sigma'], obj['color'], obj['min_freq'], obj['max_freq'])
        return obj

class ConrollerConfig(ClientConfig):
    def __init__(self, ip, port, name, web_socket_url):
        self.web_socket_url = web_socket_url
        super().__init__(self, ip, port, name)

    @staticmethod
    def object_decoder(self, obj):
        if '__type__' in obj and obj['__type__'] == 'ConrollerConfig':
            return ConrollerConfig(obj['ip'], obj['port'], obj['name'], obj['web_socket_url'])
        return obj