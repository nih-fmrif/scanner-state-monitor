
#!/usr/bin/env python3

import socketserver
import sys
import datetime



HOST = "192.168.2.5"    # listening host for real time server
PORT = 5000             # port on server real time is listening on
FILE = "/tmp/.dcmRxInfo.log"



class simple_tcp_handler(socketserver.BaseRequestHandler):

    """
       The RequestHandler class for our server.

       It is instantiated once per connection to the server, and must
       override the handle() method to implement communication to the
       client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.server.cno = self.server.cno + 1
        sys.stderr.write ("\n%s made a connection:\n" % self.client_address[0])
        # print "Connection # %d:" % self.server.cno

        # Get data and write it to the file    
        while 1: 
            data = self.request.recv(1*1024*1024)
            if not data:
                # no more data
                break

            lines = data.decode('utf-8').splitlines()

            if len(lines) > 0:
                for each_line in lines:
                    dcmMsgPipe = open(FILE, 'a')

                    # Check for MEAS_ in message string, and if present, add
                    # current system date and time to that line.
                    if "MEAS_".casefold() in each_line.casefold():
                        # Pre-pend date and time, match format already used in
                        # Siemens' logs, i.e. date: yyyy-mm-dd, and time:
                        # HH:MM:SS.milliseconds
                        current_time = datetime.datetime.now()
                        dcmMsgPipe.write (current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + ' ' + each_line + '\n')
                    else:
                        dcmMsgPipe.write (each_line + '\n')

                    # These are needed only for files, not pipes
                    # dcmMsgPipe.flush ()
                    # os.fsync (dcmMsgPipe.fileno())

                    # Close pipe/file
                    dcmMsgPipe.close()

        # The connection has been closed
        sys.stderr.write ("%s closed the connection:\n" % self.client_address[0])



class simple_socket_server(socketserver.TCPServer):

    """
       Base class for simple TCP socket server.
    """

    connection_counter = 0

    def __init__(self, server_address, RequestHandlerClass):
      socketserver.TCPServer.__init__(self, server_address, RequestHandlerClass)
      self.connection_counter = 0



if __name__ == "__main__":

   try:
      # Create the server
      server = simple_socket_server((HOST, PORT), simple_tcp_handler)

      # Activate the server
      # this will keep running until you interrupt with Ctrl-C
      server.serve_forever()
   finally:
      server.shutdown()

