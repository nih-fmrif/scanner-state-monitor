
## Description of Siemens scripts

The scripts initially checked into this repository leverage Siemens' "real-time
data export" feature, enabling DICOM files to be written to a local or network
volume, as they are reconstructed and become available on the console.  To turn
this feature on, reach out to your Siemens research contact for instructions on
how to do this.

When activating this feature, the console is configured to write DICOM image
data to a specified location, while simultaneously sending messages via TCP to
a specified IP address and port.  The location and IP can be local or remote to
the scanner console, but in either case, must be accessible from it. For example,
on FMRIF's scanners, the scanner is configured to export DICOM data to a network
Samba share, exported from a linux computer, and mounted locally at:

   V:\DICOM

on the scanner's console computer.

The same linux computer is also configured to listen to the messages sent via
TCP by the console, telling what state the scanner is in.

For images to be written to the specified volume, a listener **must** be running
on the specified IP address and network port.  This is accomplished by setting
up a systemd 'dicom_listener' service (defined using the materials in the 'usr'
folder at the same level as this README), which in turn, depends on the
"dicom_export_listener.py' script in the 'bin' directory here.  The sample DICOM
listener service configuration should be copied to the corresponding location
on the host system, then enabled and started, as with any other systemd service.
Previous implementations had the messages about the scanner state output to a
file on disk, while the current implementation writes log messages to a FIFO
buffer, which can be accessed via the "tail" command like a file on disk being
appended to.

The messages sent to the listener indicate when data acquisition has started,
the name of the DICOM image files written out to disk, and when acquisition has
stopped.  Note that because of the asynchronous nature of image reconstruction
versus data acquisition, it is possible for reconstruction to continue, images
written to disk, etc, **after** an acquisition ended message has been received.

The sample systemd service configuration provided here takes care of setting
the appropriate IP and port to listen on, as well as setting up the FIFO where
messages are written to.  The values specified here must match what is entered
into Siemens' tools to activate real-time DICOM export.

The "start_AFNI" script does exactly what its names says, starts up AFNI. But
it does a few other useful things.  It will create a location/folder (specified
by the user) from which AFNI will be launched, and real-time data for that
session written to.  The script will also set a few environmental variable to
set and control AFNI's behavior while it is running.  The script also launches
AFNI in "real-time" mode, so it is ready to receive data via it's real-time
plugin.



## Potential sources of information for the system for future functionality

- Mount operational directory on the scanner's console PC on a Linux PC (via a
Samba export), and parse the files in that directory to determine if any info
about the scanner's state is present there.  This directory is already exported
to the scanner's reconstruction computer, most likely in read-write mode, to
facilitate scanner operation.  For the functionality desired here, a read-only
export should suffice.

