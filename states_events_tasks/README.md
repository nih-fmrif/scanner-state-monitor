
## List of states, events, and tasks to be handled by real-time software

This will capture the list of states a scanner can be in, series of events on
the scanner console that can indicate changes between states, and the tasks to
be driven by the real-time software as a result of the state a scanner is in,
or the states it switches between.

|     State or Event      |     General  Electric    |          Siemens         |
|-------------------------|--------------------------|--------------------------|
|    System start-up      |           TBD            |            TBD           |
|     System  ready       |           TBD            |            TBD           |
|    System shut-down     |           TBD            |            TBD           |
| System idle (- patient) |           TBD            |            TBD           |
| System idle (+ patient) |           TBD            |            TBD           |
|      pre-scanning       |           TBD            |            TBD           |
|    pre-scan failure     |           TBD            |            TBD           |
|    pre-scan success     |           TBD            |            TBD           |
|    scanner "prepped"    |           TBD            |            TBD           |
|     scanner "paused"    |           TBD            |            TBD           |
|        scanning         |           TBD            |            TBD           |
|      scan failure       |           TBD            |            TBD           |
|      scan success       |           TBD            |            TBD           |
|  reset system hardware  |           TBD            |            TBD           |



## List of more specialized states to detect, or applications to trigger:

1. Performing QA scans.

1. Automatic capture of physiology data. BIOPAC 'integration'?

1. Motion detection and alert user if motion > set threshold.

1. Triggering other software coincident with data acquisition (e.g. for
   neurofeedback).

1. Custom reconstruction of data, with data either going back to scanner in a
   standard vendor-recognized format (e.g. DICOMs on GE, pixel database on
   Siemens), or sent to another application directly (e.g. 2D+z+t data to AFNI
   via real-time channel).

1. Drive actions based on pulse sequence/scan properties and/or parameter
   values (by reading "HEADER_POOL" on GE, and XProtocol on Siemens?).
   Real-time access to TWIX?  Access at scanner "prepped" state.

1. Adaptive experiments (e.g. staircases) - change/update acquisition/experiment
   based on parameter estimation of parameters.

1. In-session registration of partial brain volume data.  Grab images generated
   by scanner, or potentially doing your own reconstruction.

1. Detect and respond by acquisition-by-acquisition or TR-by-TR?

