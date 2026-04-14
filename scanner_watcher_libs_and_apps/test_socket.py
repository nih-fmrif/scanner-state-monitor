
# Simple utility to send messages to another program listening on a TCP socket
# so scanner doesn't have to be running the entire time for testing.

import time, socket, datetime



host = 'localhost'
port = 5000

while True:

   with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:

      client_socket.connect ((host, port))

      message = "Hi RT-listener! Sending this message at " + str(datetime.datetime.now())

      print (message)

      client_socket.sendall(message.encode('utf-8'))

   time.sleep(1)

