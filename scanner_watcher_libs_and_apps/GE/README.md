
## Implementation of real-time software on FMRIF's General Electric's MRI scanners

The implementation used at FMRIF is based on the worked presented at the OHBM
2008 Annual Meeting, abstract 303 T-AM, "Real Time Software for Monitoring MRI
Scanner Operation," by Bodurka and Bandettini.

A handful of PERL scripts are at the core of this stack of software.  These are
split between the scanner's console (Linux) computer, and an associated (and
separate) secondary Linux PC.

The set of scripts running on the scanner's console parses a set of system log
files for various events.  The order in which these events occur can be used to
deduce the state the scanner is in.  These scripts use network connections and
messages to transmit the state information about the scanner to the secondary
Linux PC.  The portion of the real-time software running on the secondary PC
uses this information to control AFNI to perform certain actions, and to also
control other programs on that computer.

In addition to PERL, (later Python,) and shell scripts - a binary C-program is
also leveraged by the set of software running on the console.  This C-program
is used to parse the MRI raw (*k-space*) data header that is generated for each
acqusition to provide more in-depth information for the type and properties of
the scan being run.



## Potential sources of information for the system for future functionality

Instead of having 2 pieces of the software running on 2 different computers, it
should be possible to export the directories (on the scanner console) with data
needed by the real-time system, as read-only mounts to the secondary Linux PC.
This could correspond to the model that could be used for the Siemens real-time
system.

In both cases, there would be locations holding information about the scanner's
state on the secondary Linux PC and it would be a matter of parsing appropriate
files for each vendor, or watching other locations or resources, to determine
the state the scanner is in.



## Sources of information for current real-time implementation on GE

- System directories:

   1. /usr/g/bin/

   1. /usr/g/mrraw/ (#dir-raw)

   1. /export/home1/sdc\_image\_pool/images

   1. /usr/g/service/log/

In [i] vendor and site pulse sequence binaries are installed.

In [ii] - raw k-space and other potential data for reconstruction are written. Contains HEADER\_POOL.

Directory [iii] contains DICOM data, in a directory tree structure, with format:

   p????/e????/s????

which represents patient index / exam index / series index.

Directory [iv] contains a series of system log files that are parsed to determine the state the scanner is in.  Files of potential use in [iv] include:

- coilid.log (log of active coils for a given session / scan)
- review.out (a dump of values on the scanners interface, in a plain text
  format)
- rdbm\_log.out (log of a portion of the raw header for each acquisition)
- scn.out - a general/'catch-all' log of events happening on the system.  In
  DV26, the events listed here include:

   + "beginNewExam" (should represet a new exam being started)
   + "Save Series" (should be self explanatory)
   + " series UID" (have to check)
   + "Sending ready" (should be after successful pre-scan, when scanner is
     "prepped")
   + "downloadDone" (scanner parameters downloaded to sequencer hardware)
   + "Send Image Install Request to TIR" (should be start of data acquisition)
   + "exam\_path of image" (should indicate location where images are written
     to)
   + "Entry gotScanStopped" (should represent a scan being stopped by a
     button press on the scaner)
   + "EM\_HC\_STOP\_BUTTON\PRESS" (should represent a scan being stopped by the
     emergency button press on the scaner)
   + "Got scanStopped" (should represent successful completion of a scan) 
   + "updateOnReconDone" (have to check)
   + "Got reconStop" (have to check)
   + "gotImgXfrDone" (have to check)
   + "operator confirmed" (end of exam/session)
   + "resetMGDStart" (reset of real-time scanner hardware initiated == "TPS
     Reset" on GE)
   + "resetMGDComplete" (reset of real-time scanner hardware completed)

