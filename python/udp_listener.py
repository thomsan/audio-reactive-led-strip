import socket
import config
from client import *
import json
import numpy as np
from enum import IntEnum

class ServerMessageId(IntEnum):
    CONNECT = 1
    LED_STRIP_UPDATE = 2

class ClientMessageId(IntEnum):
    CONNECT = 1

class ClientUDPListener:
    def __init__(self):
        self.clients = []
        self.bufferSize = 1024
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((config.SERVER_UDP_IP, config.SERVER_UDP_PORT))
        self.run = True

    def stop(self):
        self.run = False
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def listen(self):
        while(self.run):
            print("Waiting for new UDP message")
            valuePair = self.sock.recvfrom(self.bufferSize)
            message = valuePair[0]
            address = valuePair[1]
            messageId = message[0]
            message = message[1:]
            if(ClientMessageId(messageId) == ClientMessageId.CONNECT):
                print("Got connect message with data: " + str(message))
                typeId = message[0]
                message = message[1:]
                self.handleClientType(typeId, message)

                # Sending a reply to client
                response = bytes([int(ServerMessageId.CONNECT)])
                print(response)
                response_address = (address[0], 7777)
                print("Sending response to " + str(response_address) + ": " + str(response))
                self.sock.sendto(response, response_address)

            else:
                print("Received message: " + str(message) + " from: " + str(address))
                print("Unkown messageId: " + str(messageId))
                
    def handleClientType(self, typeId, message):
        try:
            clientTypeId = ClientTypeId(typeId)
        except:
            print("Unkown client typeId: " + str(typeId))

        if(clientTypeId == ClientTypeId.LED_STRIP_CLIENT):
            config = json.loads(message, object_hook=LedStripConfig.object_decoder)
            print("Got config: " + config)
            self.clients.append(LedStripClient(config))
        elif(clientTypeId == ClientTypeId.CONTROLLER_CLIENT):
            config = json.loads(message, object_hook=ControllerConfig.object_decoder)
            print("Got config: " + config)
            self.clients.append(ControllerClient(config))
