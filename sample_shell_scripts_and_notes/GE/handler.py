
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

            self.latest_files    = -3 # use this to determine how many of the
                                      # last / latest log files written to disk
                                      # are read in and searched.

            self.event_date_00   = re.compile(r'\w{3} \w{3} \d{2} \d{4}')  # date format: Day-of-week Month Day-of-month YYYY
            self.event_time_00   = re.compile(r'\d{2}:\d{2}:\d{2}.\d{6}')  # time format: HH:MM:SS.microeconds

            self.scanner_events  = ['Calling startSession',                # Start of session / patient registered.
                                    'Save Series',                         # As named - probably for when a series' parameters and prescription have been saved for scanning.
                                    ' series UID',                         # Create series UID / new series.
                                    'downloadDone',                        # sequence downloaded into sequencer.
                                    'Sending ready',                       # Scan or Prep scan pressed.
                                    'Send Image Install Request to TIR',   # This should be common to both mouse click and keyboard button press to detect start of scanning and data acquisition
                                    'Got scanStopped',                     # Scan completed.
                                    'Entry gotScanStopped',                # Stop scan button pressed.
                                    'EM_HC_STOP_BUTTON_PRESS',             # Stop scan button pressed.
                                    'exam_path of image',                  # Should indicate as to where images are written to on disk.
                                    'updateOnReconDone',                   # Check scan log for most recent Exam(Ex)/series(Ser)/image(Img) numbers from recon.
                                    'Got reconStop',                       # Recon stopped?
                                    'gotImgXfrDone',                       # Images transfer to ???
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
            self.scanner_events_dict = dict(zip(self.scanner_events, repeat('AAA AAA 00 0000 (i.e. did not occur)')))



   def sort_dict (self, dictionary_to_sort,
                        sort_by = 'value',
                        sort_reverse_time_order = False):

      """
         This routine will take a dictionary, where we expect the 'value' of
         each key-value pair to be a date/time element.  This routine will
         then sort on time - earliest to latest, or latest-to-earliest can be
         chosen by setting 'sort_reverse_time_order' to be False or True,
         respectively.

         The option to sort on dictionary keys is also retained, by setting
         the value of the 'sort_by' argument to 'key'.  However, this is not
         expected to be heavily used.

         This routine will return an ordered ascending or descending list of
         key-value pairs.
      """

      if (sort_by == 'key'):
         index_to_sort_on = 0
      else:
         index_to_sort_on = 1

      return sorted(dictionary_to_sort.items(),
                    key = lambda x:x[index_to_sort_on],
                    reverse = sort_reverse_time_order)



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

               # self.scanner_events_dict[event_to_find] = this_event_date.group() + ' ' + this_event_time.group()

               try:
                  # Take time string as extract from the scanner logs, i.e. Day Mon Date Year HH:MM:SS.ms
                  date_time_object        = datetime.datetime.strptime(this_event_date_time, '%a %b %d %Y %H:%M:%S.%f')

                  # and convert it to completely numerical form, i.e. yyyy-mm-dd-HH-MM-SS.us, which can then be ordered trivially
                  self.scanner_events_dict[event_to_find] = date_time_object.strftime('%Y-%m-%d-%H-%M-%S.%f')

                  # print ("Event %45s happened at date-time: %s" % (event_to_find, self.scanner_events_dict[event_to_find]))

               except:
                  # print ("Event %s can't be matched with a valid date or time", event_to_find)
                  continue

      return (self.scanner_events_dict)



   def determine_state_and_actions (self, scanner_events_ordered):

      """
         This function will take a list of time-ordered events, i.e.
         the argument 'scanner_events_ordered', and from that, figure
         out what the scanner is doing, what state it is in, and what
         actions this script / library / object can drive.

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

      for event_time_pair in scanner_events_ordered:

         if (event_time_pair[0] == 'Calling startSession'):
            patient_time_object_registered   = datetime.datetime.strptime(event_time_pair[1],
                                                                          '%Y-%m-%d-%H-%M-%S.%f')
         if (event_time_pair[0] == 'operator confirmed'):
            patient_time_object_deregistered = datetime.datetime.strptime(event_time_pair[1],
                                                                          '%Y-%m-%d-%H-%M-%S.%f')

      if (patient_time_object_registered < patient_time_object_deregistered):
         print ("No patient registered")
      else:
         print ("Patient registered")

      # Otherwise - take a look at the last event in the list to determine the current state
      # of the scanner.

      if (scanner_events_ordered[-1][0] == 'downloadDone'):
         print ("Pulse sequence is downloaded into scanner and ready for pre-scanning.")

      if (scanner_events_ordered[-1][0] == 'Sending ready'):
         print ("Pre-scanning is complete and scanner is prepped and ready to acquire data.")

      if (scanner_events_ordered[-1][0] == 'Send Image Install Request to TIR'):
         print ("Scanner is acquiring data.")

      if (scanner_events_ordered[-1][0] == 'Got scanStopped'):
         print ("Scanner is done acquiring data.")

      if ((scanner_events_ordered[-1][0] == 'gotImgXfrDone') or
          (scanner_events_ordered[-1][0] == 'Got reconStop') or
          (scanner_events_ordered[-1][0] == 'updateOnReconDone')):
         print ("Scanner has completed data reconstruction.")

      print ("Last / most recent event in event queue is %s" % scanner_events_ordered[-1][0])

