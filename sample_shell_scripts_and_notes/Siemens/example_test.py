
import re, os, sys
sys.path.insert(0, os.path.abspath('.'))
import handler

try:
   os.getenv('MRI_SCANNER_LOG')
   with open (os.getenv('MRI_SCANNER_LOG'), 'r') as raw_log:
      log_lines = raw_log.readlines()
except:
   print ('\n   !!! Please define the environment variable MRI_SCANNER_LOG !!!\n')
   sys.exit(1)

sh = handler.event_catcher()

# sh.find_event('Patient registered',          log_lines[30:]) - no longer need to offset read from
#                                                                example as now the log parser reads
#                                                                from the bottom of the file upwards
sh.find_event('Patient registered',          log_lines)
sh.find_event('MSR_OK',                      log_lines)
sh.find_event('MSR_STARTED',                 log_lines)
sh.find_event('MSR_SCANNER_FINISHED',        log_lines)
sh.find_event('MSR_ACQ_FINISHED',            log_lines)
sh.find_event('MSR_MEAS_FINISHED',           log_lines)
sh.find_event('EVENT_PATIENT_DEREGISTERED',  log_lines)

# Example of event that should NOT be in the logs
sh.find_event('EVENT_PATIENT_REGISTERED',    log_lines)

# Now, find last event of interest in log.
sh.find_most_recent_event (log_lines)

