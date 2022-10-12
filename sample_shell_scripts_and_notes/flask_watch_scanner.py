#!/usr/bin/env python



import   time, os, re, sys

sys.path.insert(0, os.path.abspath('.'))
import   Siemens
import   GE



from flask import Flask, jsonify, request

app = Flask(__name__)



# Using Flask to run an action based on the call to the ReST API (here, just 'GET'
# calls are supported) removed the need for the watchdog and asyncio libraries, as
# one can just read the log files, when the status of the scanner is requested.
# This greatly simplifies the logic and structure, but leave open the idea of using
# those other libraries again, as needed.

class _EventHandler():

   def __init__(self, scanner_vendor, scanner_name, log_file_path, *args, **kwargs):

      super(*args, **kwargs)

      self._vendor                   = scanner_vendor
      self.scanner_name              = scanner_name
      self.log_file_dir              = log_file_path

      if (self._vendor == 'Siemens'):
         self.scanner_event_detector = Siemens.handler.event_catcher()
         self.log_file_read_mode     = 'r'
      else:
         self.scanner_event_detector = GE.handler.event_catcher()
         self.log_file_read_mode     = 'rb'

   def read_scanner_state(self):

      log_lines = self.scanner_event_detector.process_scanner_logs(self.log_file_dir, log_file_read_mode=self.log_file_read_mode)

      scanner_log_events_and_times = []
      scanner_log_events_and_times = self.scanner_event_detector.sort_dict(self.scanner_event_detector.generate_dict_of_scanner_events(log_lines))
      for event in scanner_log_events_and_times:

         print ("Event %36s happened at %s" % (event[0], event[1]))

      # Use dictionary to represent scanner info and state with a set of key-value pairs
      return jsonify({"scanner AE Title": self.scanner_name,
                      "state": self.scanner_event_detector.determine_state_and_actions(scanner_log_events_and_times)})




# Default for ReST GET method
@app.route('/scanner_state')

def get_info_and_state():

   # reading logging location from environment from account running this.
   try:
      os.environ['MRI_SCANNER_LOG_DIR']
   except:
      print ('\n   !!! Please define the environment variable MRI_SCANNER_LOG_DIR !!!\n')
      sys.exit(1)

   handler = _EventHandler('Siemens', 'fmrif3td', os.environ['MRI_SCANNER_LOG_DIR'])

   return handler.read_scanner_state()

