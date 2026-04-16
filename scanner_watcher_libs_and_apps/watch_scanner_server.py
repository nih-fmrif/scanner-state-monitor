#!/usr/bin/env python



import   time, os, re, sys
import   gzip
import   json
import   asyncio
import   datetime

sys.path.insert(0, os.path.abspath('.'))
import   Siemens
import   GE



# The server is being refactored as an application employing 'asyncio' to be able
# to poll multiple sources of information in parallel, to get more information to
# better identify the current state of the scanner.

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

      self.scanner_event_detector.sort_dict = self.sort_dict
 


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



   async def process_scanner_logs (self, log_file_dir, log_files_dict, latest_files,
                                   log_file_read_mode='rb'):
      """
         On scanners, this routine takes the directory containing the
         MR scanner's log files, and using the dictionary of log file
         names (i.e. self.log_files_dict) sorts them by modification
         time.  It then returns the contents of the latest written
         files on disk.
      """

      for each_file in log_files_dict:
         log_files_dict[each_file] =  os.path.getmtime(log_file_dir + '/' + each_file)

      time_sorted_logs = self.sort_dict(log_files_dict)

      log_lines = []

      # For initial implementation, try reading "just" the last / latest 3
      # log files only (for performance reasons).  I know that sometimes,
      # the most current log files lack all events, and sometimes even the
      # explicit current date entry.  So try this for now, till a better /
      # more efficient way is developed to parse through more of the logs.

      for each_file in time_sorted_logs[latest_files:]:

         file_name = each_file[0] # i.e. the name of the file. [1] is its
                                  # modification time.
         file_path = log_file_dir + '/' + file_name

         if ("gz" in file_name):
            # print ("Prepare for reading   compressed file: %s" % file_name)
            log_file_open_function = gzip.open
         else:
            # print ("Prepare for reading uncompressed file: %s" % file_name)
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



   async def read_scanner_state(self):

      """
         Entry point into calling scanner specific capabilities to poll vendors'
         logs.
      """

      while True:

         log_lines = await self.process_scanner_logs(self.log_file_dir,
                                                     self.scanner_event_detector.log_files_dict,
                                                     self.scanner_event_detector.latest_files,
                                                     log_file_read_mode=self.log_file_read_mode)

         if not log_lines:
            await asyncio.sleep(0.5)
         else:
            # Grab the dictionary of events from the scanner's logs
            scanner_log_events_and_times  = self.scanner_event_detector.generate_dict_of_scanner_events(log_lines)

            # Use dictionary to represent scanner info and state with a set of key-value pairs
            scanner_state_data = {"scanner vendor": self._vendor,
                                  "scanner AE Title": self.scanner_name,
                                  "all_events": str(self.scanner_event_detector.determine_state_and_actions(scanner_log_events_and_times)),
                                  "current time": str(datetime.datetime.now())}

            print (json.dumps(scanner_state_data))

            # with open (scanner_state_info_file, 'w') as state_file_handle:

               # json.dump(scanner_state_data, state_file_handle)

               # state_file_handle.flush()

         await asyncio.sleep(0.5)



async def main():

   # reading logging location from environment from account running this.
   try:
      os.environ['MRI_SCANNER_LOG_DIR']
   except:
      print ('\n   !!! Please define the environment variable MRI_SCANNER_LOG_DIR !!!\n')
      sys.exit(1)

   vendor       = os.environ['MRI_SCANNER_VENDOR']
   scanner_AET  = os.environ['MRI_SCANNER_AETITLE']

   handler = _EventHandler(vendor, scanner_AET, os.environ['MRI_SCANNER_LOG_DIR'])

   scanner_monitoring_tasks = []

   scanner_read_log_task = asyncio.create_task(handler.read_scanner_state())

   scanner_monitoring_tasks.append(scanner_read_log_task)

   scanner_aux_info_task = asyncio.create_task(handler.scanner_event_detector.read_other_resources(handler.scanner_event_detector.scanner_events_dict))

   scanner_monitoring_tasks.append(scanner_aux_info_task)

   await asyncio.gather(*scanner_monitoring_tasks)



if __name__ == "__main__":

   asyncio.run(main())

