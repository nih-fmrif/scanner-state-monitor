
import re, os, sys, gzip
sys.path.insert(0, os.path.abspath('.'))
import handler



try:
   os.getenv('MRI_SCANNER_LOG')
except:
   print ('\n   !!! Please define the environment variable MRI_SCANNER_LOG !!!\n')
   sys.exit(1)

gh = handler.event_catcher()

for each_file in gh.log_files_dict.keys():
   gh.log_files_dict[each_file] = os.path.getmtime(os.getenv('MRI_SCANNER_LOG') + '/' + each_file)

log_files_time_sorted = gh.sort_dict(gh.log_files_dict)

log_lines = []

# For initial implementation, try reading "just" the last / latest 3
# log files only (for performance reasons).  I know that sometimes,
# the most current log files lack all events, and sometimes even the
# explicit current date entry.  So try this for now, till a better /
# more efficient way is developed to parse through more of the logs.

for each_file in log_files_time_sorted[-3:]:

   file_name = each_file[0] # i.e. the same of the file. [1] is its
                            # modification time.
   file_path = os.getenv('MRI_SCANNER_LOG') + '/' + file_name

   if ("gz" in file_name):
      print ("Prepare for reading   compressed file: %s" % file_name)
      # with gzip.open (file_path, mode='rb') as raw_log:
         # this_file_lines = raw_log.readlines()
      log_file_open_function = gzip.open
   else:
      print ("Prepare for reading uncompressed file: %s" % file_name)
      # with open (file_path, mode='rb') as raw_log:
         # this_file_lines = raw_log.readlines()
      log_file_open_function = open

   # Use the "list.extend()" method here, to add / stack the entries
   # from each log file together, into one LARGE list of log entries.
   # If the more common "list.append()" is used, then the whole list
   # of entries 
   with log_file_open_function (file_path, mode='rb') as raw_log:
       this_file_lines = raw_log.readlines()
   log_lines.extend(this_file_lines)

print ("Total numnber of lines in log is %d" % len(log_lines))

print (log_lines[999])

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

