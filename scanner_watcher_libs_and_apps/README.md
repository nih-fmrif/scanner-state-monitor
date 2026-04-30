
### Environment variables used when running the watcher server Python script

* MRI\_SCANNER\_VENDOR - the vendor of the scanner being watched (currently, only values of 'GE' and 'Siemens' are supported).
* MRI\_SCANNER\_AETITLE - the Application Entity title of the scanner embedded in the DICOM images it generates
* MRI\_SCANNER\_LOG\_DIR - the location (on the local filesystem from where the watcher script is run) where the log directory from the scanner (whose contents are parsed to determine the state of the scanner) is mounted read-only.
* MRI\_SCANNER\_INFO\_PUBLISH\_TO\_HOST - hostname or IP address for TCP socket where scanner info is published to
* MRI\_SCANNER\_INFO\_PUBLISH\_TO\_PORT - port number for TCP socket where scanner info is published to
