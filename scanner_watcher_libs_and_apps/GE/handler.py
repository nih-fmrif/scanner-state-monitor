
#!/usr/bin/env python

# Basic infrastruture to parse GE scanner logs

import      re, os
import      gzip
from        itertools   import   repeat
import      datetime



class event_catcher():

   """
      Parser of scanner log files to catch events,
      and determine the date and time of those events.
   """



   read_scanner_info_methods = []

   def __init__(self, scanner_vendor='ge', platform_version='dv26.0_r02'):

      """
         This initializes an object to parse data from GE scanners.  However,
         list of parsed log files, as well as regular expressions for times
         and dates are set up, to be searched for later on.  Also set up the
         list of log events to search for.

         The list of log files and scanner events are converted to keys of a
         dictionary (log files are in one dictionary, scanner log events are
         in another).  The value (of each dictionary's key-value pair) will
         have a modification time, for log files, or an occurence time, for
         scanner events.
      """

      # Since we are looking for order of events to determine what the scanner
      # is doing, and what state it is in, set up regular expression parsers to
      # get the date and time, and set up list of events to search for.
      if (scanner_vendor == 'ge'):
         if (platform_version == 'dv26.0_r02'):

            self.log_files       = ['scn.out.0.gz', 'scn.out.1.gz', 'scn.out.2.gz',
                                    'scn.out.3.gz', 'scn.out.4.gz', 'scn.out.5.gz',
                                    'scn.out.6.gz', 'scn.out.7.gz', 'scn.out.8.gz',
                                    'scn.out.9.gz', 'scn.out']

            self.log_files_dict  = dict.fromkeys(self.log_files)

            self.latest_files    = -5 # use this to determine how many of the
                                      # last / latest log files written to disk
                                      # are read in and searched.

            self.event_date_00   = re.compile(r'\w{3} \w{3} \d{2} \d{4}')  # date format: Day-of-week Month Day-of-month YYYY
            self.event_time_00   = re.compile(r'\d{2}:\d{2}:\d{2}.\d{6}')  # time format: HH:MM:SS.microeconds

            self.scanner_events  = ['Calling startSession',                # Start of session / patient registered.
                                    # 'Save Series',                         # As named - probably for when a series' parameters and prescription have been saved for scanning. Commented out as causing later events to not show up in list.
                                    # ' series UID',                         # Create series UID / new series.
                                    # 'downloadDone',                        # sequence downloaded into sequencer.
                                    'Sending ready',                       # Scan or Prep scan pressed.
                                    'Send Image Install Request to TIR',   # This should be common to both mouse click and keyboard button press to detect start of scanning and data acquisition
                                    'Got scanStopped',                     # Scan completed.
                                    'Entry gotScanStopped',                # Stop scan button pressed.
                                    'EM_HC_STOP_BUTTON_PRESS',             # Stop scan button pressed.
                                    # 'exam_path of image',                  # Should indicate as to where images are written to on disk.
                                    # 'updateOnReconDone',                   # Check scan log for most recent Exam(Ex)/series(Ser)/image(Img) numbers from recon.
                                    # 'Got reconStop',                       # Recon stopped?
                                    # 'gotImgXfrDone',                       # Images transfer to ???
                                    # 'haltsys',                             # system shutdown / reboot / restart - this is a running process (from ps) not from sysytem log
                                    # 'stopvmx',                             # software shutdown (endsession)     - this is a running process (from ps) not from sysytem log
                                    'resetMGDStart',                       # Start reset of hardware sequencers (TPS reset).
                                    'resetMGDComplete',                    # Complete reset of hardware sequencers.
                                    'operator confirmed']                  # End of session / scanning complete / patient closed.

            # self.scanner_events_dict = dict.fromkeys(self.scanner_events)
            #
            # Initialize dictionary values with nonsensical value, so if an
            # event is not found in the logs, it can still processed by the
            # 'sort_dict' routine.
            self.scanner_events_dict = dict(zip(self.scanner_events, repeat('0000-00-00-00-00-00.000000 (i.e. did not occur)')))

      self.read_scanner_info_methods = [self.read_header_pool]


   def process_scanner_logs (self, log_file_dir, log_file_read_mode='rb'):

      """
         On GE, this routine takes the directory containing the MR
         scanner's log files, and using the dictionary of log file
         names (i.e. self.log_files_dict) sorts them by modification
         time.  It then returns the contents of the latest written
         files on disk.
      """

      for each_file in self.log_files_dict:
         self.log_files_dict[each_file] =  os.path.getmtime(log_file_dir + '/' + each_file)

      time_sorted_logs = self.sort_dict(self.log_files_dict)

      log_lines = []

      # For initial implementation, try reading "just" the last / latest 3
      # log files only (for performance reasons).  I know that sometimes,
      # the most current log files lack all events, and sometimes even the
      # explicit current date entry.  So try this for now, till a better /
      # more efficient way is developed to parse through more of the logs.

      for each_file in time_sorted_logs[self.latest_files:]:

         file_name = each_file[0] # i.e. the name of the file. [1] is its
                                  # modification time.
         file_path = log_file_dir + '/' + file_name

         if ("gz" in file_name):
            print ("Prepare for reading   compressed file: %s" % file_name)
            log_file_open_function = gzip.open
         else:
            print ("Prepare for reading uncompressed file: %s" % file_name)
            log_file_open_function = open

         # Use the "list.extend()" method here, to add / stack the entries
         # from each log file together, into one LARGE list of log entries.
         # If the more common "list.append()" is used, then the whole list
         # of entries becomes a list of lists of entries from each file -
         # which is not what is desired.  It preferable to have the entire
         # content of all log files in a single, time-ordered, list.  This
         # is generated, and returned.
         with log_file_open_function (file_path, mode=log_file_read_mode) as raw_log:
             this_file_lines = raw_log.readlines()
         log_lines.extend(this_file_lines)

      return log_lines



   def generate_dict_of_scanner_events (self, log_to_search):

      """
         This function will be used to parse through the supplied log, find all
         events in this scanner object's "self.scanner_events_dict" dictionary
         of all possible events on a scanner, and return a dictionary of events
         and their time of occurence.
      """

      # Set a dummy date, as this is not guaranteed to be found immedidately
      # but once found, will be set appropropriately.  Log fed here should be
      # in sequenetial time order, so any event after a proper date entry is
      # recorded to have happened on that date, till the next date entry.
      this_event_date = self.event_date_00.search('   XXX XXX 00 0000   ')

      for this_line in log_to_search:

         try:
            current_line = this_line.decode('utf-8').strip()
         except UnicodeDecodeError:
            # print ("Cannot decode %s" % this_line)
            continue

         if (self.event_date_00.search(current_line) != None):
            this_event_date = self.event_date_00.search(current_line)

         for event_to_find in self.scanner_events_dict.keys():

            # Determine if the line contains the event of interest.
            if (event_to_find in current_line):

               # If it does, then get the event's time.  Date is on a completely
               # separate line in GE logs, so has to be handled a bit differently.
               this_event_time         = self.event_time_00.search(current_line)

               this_event_date_time    = this_event_date.group() + ' ' + this_event_time.group()

               # print ("Event %45s happened at date: %s, time: %s" % (event_to_find, this_event_date.group(), this_event_time.group()))

               try:
                  # Take time string as extract from the scanner logs, i.e. Day Mon Date Year HH:MM:SS.ms
                  date_time_object        = datetime.datetime.strptime(this_event_date_time, '%a %b %d %Y %H:%M:%S.%f')

                  # Use time object as dictionary value
                  self.scanner_events_dict[event_to_find] = date_time_object

                  # print ("Event %45s happened at date-time: %s" % (event_to_find, self.scanner_events_dict[event_to_find]))

               except:
                  # print ("Event %s can't be matched with a valid date or time", event_to_find)
                  continue

      return (self.scanner_events_dict)



   def determine_state_and_actions (self, scanner_events):

      """
         This function will take a list of scanner events, i.e.  the
         argument 'scanner_events', and translate that into a more
         'standardized' set of scanner events, with the time of each
         event, figure out what the scanner is doing, what state it
         is in, and what actions this script / library / object can
         drive.

         This will, of course, be specific to each scanner platform -
         i.e. linking a message or label to a specific scanner state.
         However, the plan will be to make the states more generic and
         platform agnostic.

         The events fed to this function should be an event label that
         is paired with a time event, in the format:

               YYYY-MM-DD-HH-MM-SS.ususus

         so that a standard datetime call can be used for any parsing
         that might be 'time-sensitive'.

      """

      # Use time objects (stored as dictionary values) directly.
      if (scanner_events['Calling startSession'] < scanner_events['operator confirmed']):
         scanner_state = "End scanning session"
      else:
         scanner_state = "Start scanning session"

      # Iterate through scanner events list, and replace vendor's log flag with 'standard'
      standardized_scanner_events = {}
      for event in scanner_events.keys():
         if (event == 'Calling startSession'):
            standardized_scanner_events['Start scanning session'] = scanner_events[event]
         if (event == 'Sending ready'):
            standardized_scanner_events['Pulse sequence prepped'] = scanner_events[event]
         if (event == 'Send Image Install Request to TIR'):
            standardized_scanner_events['Scanner is acquiring data'] = scanner_events[event]
         if ((event == 'Entry gotScanStopped') or (event == 'EM_HC_STOP_BUTTON_PRESS')):
            standardized_scanner_events['Scan stopped before completion'] = scanner_events[event]
         if (event == 'Got scanStopped'):
            standardized_scanner_events['Scanner is done acquiring data'] = scanner_events[event]
         if (event == 'operator confirmed'):
            standardized_scanner_events['End scanning session'] = scanner_events[event]

      # return (scanner_state)
      return (standardized_scanner_events)



   def read_header_pool (self):

      """
         Temporarily empty method to start building up queue of parallel-ly executing events,
         to be handled concurrently.
      """

      while 1:

         print ("Should be reading raw header pool eventually, not doing anything else now.")

