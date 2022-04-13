
import re, os, sys, gzip
sys.path.insert(0, os.path.abspath('.'))
import handler



gh = handler.event_catcher()

for each_file in gh.log_files_dict.keys():
   gh.log_files_dict[each_file] = os.path.getmtime(os.getenv('MRI_SCANNER_LOG') + '/' + each_file)

log_files_time_sorted = gh.sort_dict(gh.log_files_dict)


for each_file in log_files_time_sorted:
   print (each_file)

try:
   with open (os.getenv('MRI_SCANNER_LOG'), 'rb') as raw_log:
   # with gzip.open (os.getenv('MRI_SCANNER_LOG'), mode='rb') as raw_log:  # for compressed log files
      log_lines = raw_log.readlines()
except:
   print ('\n   !!! Please define the environment variable MRI_SCANNER_LOG !!!\n')
   sys.exit(1)

gh.find_event('Calling startSession',              log_lines)
gh.find_event('Save Series',                       log_lines)
gh.find_event(' series UID',                       log_lines)
gh.find_event('downloadDone',                      log_lines)
gh.find_event('Sending ready',                     log_lines)
gh.find_event('Send Image Install Request to TIR', log_lines)
gh.find_event('Got scanStopped',                   log_lines)
gh.find_event('Entry gotScanStopped',              log_lines)
gh.find_event('EM_HC_STOP_BUTTON_PRESS',           log_lines)
gh.find_event('exam_path of image',                log_lines)
gh.find_event('updateOnReconDone',                 log_lines)
gh.find_event('Got reconStop',                     log_lines)
gh.find_event('gotImgXfrDone',                     log_lines)
gh.find_event('resetMGDStart',                     log_lines)
gh.find_event('resetMGDComplete',                  log_lines)
gh.find_event('operator confirmed',                log_lines)

# Example of event that should NOT be in the logs
gh.find_event('EVENT_PATIENT_REGISTERED',    log_lines)

