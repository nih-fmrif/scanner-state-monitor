
# *D*ynamic *M*ulti-*V*endor *MRI* *S*canner-*Watch*er

This reposiotry hosts a Python-based framework that can monitor the state of
a MRI system, and publish that state information so it can be used to monitor
equipment on which this software is installed, and potentially drive MRI and
FMRI experiments, based on that published information.

The 'scanner\_watcher\_libs\_and\_apps' folder contain server-type utilities,
which make information about the scanner available, as well as folders which
contain code to handle the respective vendor's information streams. Currently,
General Electric and Siemens MRI systems are supported.

The 'resources' folder in this repository holds sample code and URLs which
detail various libraries and techniques (such as celery, watchdog, and other
task queue and file system managers) that were considered initially when
building this library.

