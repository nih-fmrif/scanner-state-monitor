
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
     programToKeepAlive=`echo $@ | cut -d " " -f 1 - | awk -F/ '{print $(NF)}' -` # Get last element of 1st argument

       programProcessID=`ps -o pid= -C "$programToKeepAlive"`
       # remove space before returned process ID string
       programProcessID=`echo $programProcessID | cut -d " " -f 1 -`



# Take appropriate action, whether program is already running, or not:

if [ "$programProcessID" == "" ]; then
   # Make logging directory for that program, if not available

   mkdir $logDirectory/$programToKeepAlive.log/

   logFile=log.starting.`date "+%Y.%m.%d.%H.%M.%S"`.txt

   echo "No process ID found for $programToKeepAlive, starting ..."

   # Start program (with all of its arguments) and enable logging
   $@ >> $logDirectory/$programToKeepAlive.log/$logFile 2>&1 &
else
   echo "Program $programToKeepAlive is running and has process ID = $programProcessID"
   exit 0
fi

