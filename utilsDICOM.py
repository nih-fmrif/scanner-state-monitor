
# With the real time system for Siemens scanners being built in python,
# create this library of classes and functions that can hopefully be used
# and re-used for this (and maybe even other) software.

import os, sys, getopt, subprocess
import dicom
import re   # Regular expression parsing
import select



class utilsDICOM:
    '''Utilization of pydicom to return specific values from a DICOM
       image header as a plain text string.
    '''



def removeNewLine (oldString):
    firstCleanedString = oldString.replace          ('\n', '')
    finalCleanedString = firstCleanedString.replace ('\r', '')

    return (finalCleanedString)



def convertWinFileNameToUnixName (winFileNameText):
    winFileName = str(winFileNameText[(len(winFileNameText) - 1)])
    return winFileName.replace ('\\', '/')



def runProgramAndReturnCleanedOuput (commandString, shellBoolean):
    commandArray = commandString.split()

    # print "commandArray is " + str (commandArray)

    programOutput = subprocess.Popen (commandArray, shell=shellBoolean,
                                      stdout=subprocess.PIPE)

    stringOutput = programOutput.stdout.read()

    return (removeNewLine(stringOutput))



def printAFNIDirectory (dicomFilePath):

    if (dicomFilePath == ""):
        print ""
        print "  This function prints out the name of the lowest"
        print "  level directory that is supposed to hold AFNI"
        print "  datasets resulting from a (series of) dicom"
        print "  image(s)."
        print ""

        return (-1)

    dicomFilePtr = dicom.read_file (dicomFilePath)

    # Get elements from DICOM header that we decide to use to form the
    # directory, which need additional processing.  Elements which do
    # not need additional processing will be accessed and used as is.

    dicomStudyName    = str (dicomFilePtr.StudyDescription)
    studyName         = dicomStudyName.replace ('^', '_')

    # The StudyTime element from the DICOM header is in the format:
    # HHMMSS.dddddd, where the 6 'd' characters seem to represent a
    # component of the time in microseconds when the study was set
    # up on the scanner.  We just want the HHMMSS component, which
    # is why all we want to do is match 6 consecutive integers.

    dicomStudyTime    = str (dicomFilePtr.StudyTime)
    studyTimePieces   = re.search ('\d{6}', dicomStudyTime)
    studyTime         = str (studyTimePieces.group(0))

    dicomRealTimeDirectory = str (dicomFilePtr.SeriesDate) + '.' + studyTime + '.' + studyName

    return (removeNewLine(dicomRealTimeDirectory))



def getSeriesDescription (dicomFilePath):

   dicomFilePtr = dicom.read_file (dicomFilePath)

   return (removeNewLine(str (dicomFilePtr.SeriesDescription)))



def getRepetitionTime (dicomFilePath):

   dicomFilePtr = dicom.read_file (dicomFilePath)

   return (dicomFilePtr[0x18, 0x80].value)



def getSequenceName (dicomFilePath):

   dicomFilePtr = dicom.read_file (dicomFilePath)

   return (dicomFilePtr[0x18, 0x24].value)

