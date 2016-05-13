#!/usr/bin/python

import struct
import os, sys, getopt
import re



# default user and terminal
USER = "rtadmin"
TERM = ":0"



def printHelp ():

    print ""
    print "    Script to check whether user is logged into a specific"
    print "    port or terminal on a machine.  The program returns a"
    print "    value of 1 if the specified user is logged into the"
    print "    specified terminal, or another value if the specified"
    print "    user + terminal combination is not found."
    print ""
    print "    Usage:\n"
    print "        checkLogin.py -u USER -t TERMINAL\n"
    print "    where:\n"
    print "        USER is the user login name to check for."
    print "        TERM is the terminal on which user is logged in.\n"
    print "            e.g.    :0    or    pts/1 \n"
    print "    At least one of these (USER or TERMINAL) must be specified.\n"



def processOptions (argv):

    global USER, TERM

    try:
        opts, args = getopt.getopt(argv, "u:t:", ["user=", "term="])
    except getopt.GetoptError:
        sys.stderr.write ('\n    Unrecognized options.\n')
        printHelp()
        sys.exit(2)

    if (len(opts) < 1):
        printHelp()
        sys.exit(-1)

    for option, argument in opts:
        if option in ("-u", "--user"):
            USER = argument
            # sys.stderr.write ('Setting user to ' + USER + '\n')
        elif option in ("-t", "--term"):
            TERM = argument
            # sys.stderr.write ('Setting login terminal to ' + TERM + '\n')



if __name__ == "__main__":
    processOptions (sys.argv[1:])

allLogins = os.popen ("w") # run who command to get list of logins

i = 0

# Iterate over all logins to check if user is logged into desired port
for eachLogin in allLogins.readlines():
    i += 1

    # print "Login " + str(i) + " is: " + eachLogin

    matched = re.search (USER + '\s+' + TERM, eachLogin)

    if matched:
        break

if matched:
    # print "\n  User " + USER + " was found logged in on terminal " + TERM + "\n"
    sys.exit (1)
else:
    # print "\n  No login for " + USER + " found on terminal " + TERM + "\n"
    sys.exit (-1)

