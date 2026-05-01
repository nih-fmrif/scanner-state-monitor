
## Scanner watching applications and support libraries

This folder contains a few applications and libraries with code to support vendors'
information streams.  Currently, these are:

* 'watch\_scanner\_server\_flask.py' is the initial implementation. This utility
leverage only routines that parse each vendor's text logs. The information gleaned
from those text logs are then made available via a simple Flask application.  The
'boot\_watch\_scanner.sh' script creates a basic Flask environment in which this
utility can be run, then runs it.

* 'watch\_scanner\_server.py' is the follow-on implementation. This utility can
leverage information from multiple streams asynchronously (using Python's *asyncio*
library), including vendors' text logs (as mentioned for the Flask-flavored version
of this application), and now TCP sockets. This utility, instead of leveraging a
Flask application, publishes the scanner's state to another TCP socket, also in a
asynchronous task.  This utility should also be able to leverage more information
sources as capabilities are added to the vendors' supporting libraries.

* 'watch\_scanner\_client.py' - which, as the name suggests, is the sample client
program showing how to access the information provided. This sample client will
only provide a time-ordered list of detected events on each vendor's systems, but
this can serve as a template for building applications that can use this state
information. It also leverages Python's asyncio library so that listening to and
receiving information from the network socket does not block execution of the main
thread/event loop.



### System setup

In order to access the information these utilities need, the computer on which
they are run needs access to the scanner's log directories.

The testing and work done on this code have been on Linux systems where MR
scanners' log directories have been mounted read-only (NFS and Samba both seem
to work adequately) and are accessible to the accounts and processes running
these tasks. The local implemention should be tailored to what is available and
possibly locally, but since a wide scale of implementations are possible, these
should be verified and tested for performance and reliability.



### Environment variables used when running the watcher server Python script

* MRI\_SCANNER\_VENDOR - the vendor of the scanner being watched (currently,
  only values of 'GE' and 'Siemens' are supported).
* MRI\_SCANNER\_AETITLE - the Application Entity title of the scanner embedded
  in the DICOM images it generates
* MRI\_SCANNER\_LOG\_DIR - the location (on the local filesystem from where the
  watcher script is run) where the log directory from the scanner (whose contents
  are parsed to determine the state of the scanner) is mounted read-only.
* MRI\_SCANNER\_INFO\_PUBLISH\_TO\_HOST - hostname or IP address for TCP socket
  where scanner info is published to (also used by client program)
* MRI\_SCANNER\_INFO\_PUBLISH\_TO\_PORT - port number for TCP socket where
  scanner info is published to (also used by client program)

