
#!/bin/sh

# This little script is called via a cron job to make sure whatever program
# it is called with (as an argument) is running when a user is logged in. If
# the user is logged in, and the program is alredy running, no action is
# taken.  If the user is logged and the program is not running, this script
# starts it up, and creates a directory to log its output (if it doesn't
# already exist), and starts a log file with the time logging started in the
# name of log file.
#
# If the user is not logged in, the last part of the script checks for the
# process ID of the running program, and kills it.

           # logDirectory=$HOME/RTafni/var/log
           logDirectory=/home/rtadmin/RTafni/var/log
     programToKeepAlive=`echo $@ | cut -d " " -f 1 -` # Get 1st argument

       programProcessID=`ps -o pid= -C "$programToKeepAlive"`
       # remove space before returned process ID string
       programProcessID=`echo $programProcessID | cut -d " " -f 1 -`

# User that has access to the console, and who will most likely run AFNI.
        consoleAFNIUser=meduser
   consoleLoginTerminal=":"



# Check if $consoleAFNIUser is logged into $consoleLoginTerminal

checkLogin.py -u $consoleAFNIUser -t $consoleLoginTerminal

loginReturnValue=$? # gets return value of above command.  That
                    # program returns 1 if user is logged in to
                    # the specified terminal, and -1 if not.



# Take appropriate action, whether logged in, or not.

if [ $loginReturnValue == 1 ]; then
    echo $consoleAFNIUser is logged into terminal $consoleLoginTerminal.

    if [ "$programProcessID" == "" ]; then
        # Make logging directory for that program, if not available

        directoryCheck.pl $logDirectory/$programToKeepAlive.log/

        logFile=log.starting.`date "+%Y.%m.%d.%H.%M.%S"`.txt

        echo "No process ID found for $programToKeepAlive, starting ..."

        # Start program (with all of its arguments) and enable logging
        $@ >> $logDirectory/$programToKeepAlive.log/$logFile 2>&1 &
    else
        echo "Program $programToKeepAlive is running and has process ID = $programProcessID"
        exit 0
    fi
else
    echo $consoleAFNIUser is _NOT_ logged into terminal $consoleLoginTerminal.

    # kill process if running and user not logged in

    if [ "$programProcessID" != "" ]; then
        echo Killing program $programToKeepAlive with process ID $programProcessID.
        kill -9 $programProcessID
    else
        echo Program $programToKeepAlive is not running.
        exit 0
    fi
fi

