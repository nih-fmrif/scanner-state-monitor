
#!/usr/bin/env python

# Basic infrastruture to parse Siemens scanner logs

import      re, os
import      gzip
from        itertools   import   repeat





class event_catcher():

   """
      Parser of scanner log files to catch events,
      and determine the date and time of those events.
   """



   def __init__(self, scanner_vendor='siemens', platform_version='ve11c'):

      """
         Right now, this is entry point to general object to parse data from the
         scanners.  However, not sure if this will be a general entry point that
         will 'hand-off' to objects to deal with the different scanner vendors,
         and vendor-specific implementations, or if this object itself will be
         particular to a vendor, and the create corresponding objects for other
         vendors.

         Start with the former case (general object, hand off to vendor specific
         within here).  If it stays this way, change name of module to reflect
         this.
      """

      # Since we are looking for order of events to determine what the scanner
      # is doing, and what state it is in, set up regular expression parsers to
      # get the date and time, and set up list of events to search for.
      if (scanner_vendor == 'siemens'):
         if (platform_version == 've11c'):

            self.log_files = ['MrMeas_container.log']

            self.log_files_dict  = dict.fromkeys(self.log_files)

            self.latest_files    = -1 # use this to determine how many of the
                                      # last / latest log files written to disk
                                      # are read in and searched.

            self.event_date_00   = re.compile(r'\d{4}-\d{2}-\d{2}')        # date format: yyyy-mm-dd
            self.event_time_00   = re.compile(r'\d{2}:\d{2}:\d{2}.\d{3}')  # time format: HH:MM:SS.milliseconds
            self.event_date_01   = re.compile(r'\D{3} \D{3} \d{2}')        # date format: DOW MON dd (DOW == day of the week,
                                                                           #                          MON == month,
                                                                           #                          dd  == day in month)

            self.scanner_events  = ['MSR_OK',
                                    'MSR_STARTED',
                                    'MSR_SCANNER_FINISHED',
                                    'MSR_ACQ_FINISHED',
                                    'MSR_MEAS_FINISHED',
                                    'Patient registered',                  # Patient registered and deregistered
                                    'EVENT_PATIENT_DEREGISTERED']          # Patient deregistered only

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
         On Siemens, this routine takes the directory containing the
         MR scanner's log files, and using the dictionary of log file
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

      # Reverse order of log, as above.
      reversed_log = log_to_search[-1:0:-1]

      for event_to_find in self.scanner_events_dict.keys():

         for current_line in reversed_log:

            if (event_to_find in current_line):

               if (event_to_find == 'Patient registered'):
                  event_date_current = self.event_date_01
               else:
                  event_date_current = self.event_date_00

               try:
                  this_event_date         = event_date_current.search(current_line)
                  this_event_time         = self.event_time_00.search(current_line)

                  self.scanner_events_dict[event_to_find] = this_event_date.group() + ' ' + this_event_time.group()

                  break # Should break out the "this_line" loop, and go to next
                        # iteration in "event_to_find" loop.

               except AttributeError:

                  print ("Log line not properly formed. Move to next, properly written, event.")

               # print ("Event %45s happened at date: %s, time: %s" % (event_to_find, this_event_date.group(), this_event_time.group()))

      return (self.scanner_events_dict)

