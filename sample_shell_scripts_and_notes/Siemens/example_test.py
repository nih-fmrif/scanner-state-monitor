
import re, os, sys
sys.path.insert(0, os.path.abspath('.'))
import siemens_handler

with open ('MrMeas_container.log.sample-2021-09-07', 'r') as raw_log:
   log_lines = raw_log.readlines()

sh = siemens_handler.event_catcher()

sh.find_event('MSR_OK',                      log_lines[30:])
sh.find_event('MSR_STARTED',                 log_lines[30:])
sh.find_event('MSR_SCANNER_FINISHED',        log_lines[30:])
sh.find_event('MSR_ACQ_FINISHED',            log_lines[30:])
sh.find_event('MSR_MEAS_FINISHED',           log_lines[30:])
sh.find_event('EVENT_PATIENT_DEREGISTERED',  log_lines[30:])

# Example of event that should NOT be in the logs
sh.find_event('EVENT_PATIENT_REGISTERED',    log_lines[30:])

