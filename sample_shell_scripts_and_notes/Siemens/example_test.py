
import os, sys
sys.path.insert(0, os.path.abspath('.'))
import handler



try:
   os.environ['MRI_SCANNER_LOG_DIR']
except:
   print ('\n   !!! Please define the environment variable MRI_SCANNER_LOG_DIR !!!\n')
   sys.exit(1)



sh = handler.event_catcher()

log_lines = sh.process_scanner_logs(os.getenv('MRI_SCANNER_LOG_DIR'), log_file_read_mode='r')

print ("Total numnber of lines in log is %d" % len(log_lines))

# scanner_log_events_and_times = sh.generate_dict_of_scanner_events(log_lines)

# for event in scanner_log_events_and_times.keys():

   # print ("Event %36s happened at %s" % (event, scanner_log_events_and_times[event]))

scanner_log_events_and_times = sh.sort_dict(sh.generate_dict_of_scanner_events(log_lines))

for event in scanner_log_events_and_times:

   print ("Event %36s happened at %s" % (event[0], event[1]))

