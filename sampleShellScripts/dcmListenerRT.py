
#!/usr/bin/python



import SocketServer
import struct
import os, sys, getopt



HOST = "192.168.2.5"    # listening host for real time server
PORT = 5000             # port on server real time is listening on
FILE = "/home/rtadmin/RTafni/tmp/dcmRxInfo.log"



class MyTCPHandler(SocketServer.BaseRequestHandler):
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

            lines = data.splitlines ()

            if len(lines) > 0:
                for eachLine in lines:
                    dcmMsgPipe = open(FILE, 'a')
                    dcmMsgPipe.write (eachLine + '\n')

                    # These are needed only for files, not pipes
                    # dcmMsgPipe.flush ()
                    # os.fsync (dcmMsgPipe.fileno())

                    # Close pipe/file
                    dcmMsgPipe.close()

        # The connection has been closed
        sys.stderr.write ("%s closed the connection:\n" % self.client_address[0])



class MySocketServer(SocketServer.TCPServer):
    """
    The class for our server.
    It adds a counter for connection number.

    """
    cno = 0 # counter
    def __init__(self, server_address, RequestHandlerClass):
      SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)
      self.cno = 0



def processOptions (argv):

    global HOST, PORT, FILE

    # print "Processing commmand line options"

    try:
        opts, args = getopt.getopt(argv, "h:p:f:", ["host=", "port=", "file="])
    except getopt.GetoptError:
        sys.stderr.write ('Unrecognized options\n')
        sys.exit(2)

    for option, argument in opts:
        if option in ("-h", "--host"):
            HOST = argument
            sys.stderr.write ('Setting host to ' + HOST + '\n')
        elif option in ("-p", "--port"):
            PORT = int(argument)
            sys.stderr.write ('Setting port to ' + str(PORT) + '\n')
        elif option in ("-f", "--file"):
            FILE = argument
            sys.stderr.write ('Setting output file to ' + FILE + '\n')
        else:
            sys.stderr.write ('Using host ' + HOST + ' on port ' + str(PORT) + ' and debug output will be written to STDERR\n')

    # Check to make sure output file/pipe exists
    if not os.path.exists (FILE):
        try:
            os.system ('mkfifo --mode=664 ' + FILE)
            # These are needed only for files, not pipes
            # os.system ('touch     ' + FILE)
            # os.system ('chmod 664 ' + FILE)
        except OSError:
            print 'Cannot find or make PIPE file ' + FILE + ' for communication.'



if __name__ == "__main__":

   # Remove old instance of log file / pipe.  A "clean" version of the pipe /
   # file will be created.
   if os.path.isfile(FILE):
      os.unlink(FILE)

   processOptions (sys.argv[1:])

   try:
      # Create the server
      server = MySocketServer((HOST, PORT), MyTCPHandler)

      # Activate the server
      # this will keep running until you interrupt with Ctrl-C
      server.serve_forever()
   finally:
      # remove the log file when the server is killed
      if os.path.isfile(FILE):
         os.unlink(FILE)

