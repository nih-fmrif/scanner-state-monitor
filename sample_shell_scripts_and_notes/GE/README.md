
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

