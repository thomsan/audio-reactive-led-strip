import sys
import time
from threading import Thread
from udp_listener import ClientUDPListener

if __name__ == '__main__':
    try:
        client_udp_listener = ClientUDPListener()
        client_udp_listener_thread = Thread(target = client_udp_listener.listen)
        client_udp_listener_thread.start()

        run = True
        while run:
            print("Connected clients: " + str(client_udp_listener.clients))
            time.sleep(1)

    except KeyboardInterrupt:
        print('Interrupted')
        client_udp_listener.stop()
        client_udp_listener_thread.join()
        sys.exit(0)