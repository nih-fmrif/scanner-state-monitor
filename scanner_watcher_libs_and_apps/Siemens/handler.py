
#!/usr/bin/env python

# Basic infrastruture to parse Siemens scanner logs

import      re, os, sys
from        itertools   import   repeat
import      datetime
import      select
import      asyncio



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

            self.log_files       = ['MrMeas_container.log']

            self.log_files_dict  = dict.fromkeys(self.log_files)

            self.latest_files    = -1 # use this to determine how many of the
                                      # last / latest log files written to disk
                                      # are read in and searched.

            self.event_time_00   = re.compile(r'\d{2}:\d{2}:\d{2}.\d{3}')  # time format: HH:MM:SS.milliseconds
            self.event_date_00   = re.compile(r'\d{4}-\d{2}-\d{2}')        # date format: yyyy-mm-dd
            self.event_date_01   = re.compile(r'\D{3} \D{3} \d{2}')        # date format: DOW MON dd (DOW == day of the week,
                                                                           #                          MON == month,
                                                                           #                          dd  == day in month)

            self.scanner_events  = ['MSR_OK',
                                    'SCANNER prepare finished ok',         # Prescanning / adjustments complete?
                                    'MSR_STARTED',
                                    'MSR_SCANNER_FINISHED',
                                    'MSR_ACQ_FINISHED',
                                    'MSR_MEAS_FINISHED',
                                    'Patient registered',                  # Patient registered and deregistered
                                    'EVENT_PATIENT_DEREGISTERED']          # Patient deregistered only

            # Initialize dictionary values with nonsensical value, so if an
            # event is not found in the logs, it can still processed by the
            # 'sort_dict' routine.
            self.scanner_events_dict = dict(zip(self.scanner_events, repeat('0001-01-01-00-00-00.001')))



   def generate_dict_of_scanner_events (self, log_to_search):

      """
         This function will be used to parse through the supplied log, find all
         events in this scanner object's "self.scanner_events_dict" dictionary
         of all possible events on a scanner, and return a dictionary of events
         and their time of occurence.

         This is also the anchor function that is called every time the scanner
         state is queried, so might be able to serve as a base for setting up
         and calling asynchronous events.

      """

      # Reverse order of log, as above.
      reversed_log = log_to_search[-1:0:-1]

      for event_to_find in self.scanner_events_dict.keys():

         for current_line in reversed_log:

            if (event_to_find in current_line):

               try:
                  this_event_time      = self.event_time_00.search(current_line)

                  if (event_to_find == 'Patient registered'):
                     patient_event_date = self.event_date_01.search(current_line)
                     # Patient registered event doesn't contain the year of the event, so grab current year.
                     # Note the fragility of this assumption for scanning over midnight from New Year's Eve
                     # to New Year's Day.  So we are parsing an event that looks like this:
                     #
                     # Tue Sep 07 10:54:45.453 SBM INFO: -->Patient registered

                     this_event_year    = '{num:{fill}{width}}'.format(num=datetime.date.today().year, fill='0', width=4)
                     date_time_string   = patient_event_date.group() + ' ' + this_event_year + ' ' + this_event_time.group()

                     date_time_object   = datetime.datetime.strptime(date_time_string, '%a %b %d %Y %H:%M:%S.%f')
                  else:
                     this_event_date    = self.event_date_00.search(current_line)
                     date_time_string   = this_event_date.group() + ' ' + this_event_time.group()
                     date_time_object   = datetime.datetime.strptime(date_time_string, '%Y-%m-%d %H:%M:%S.%f')

                  # Previously, converted date object to string to store as
                  # dictionary value, using:
                  #
                  #    date_time_object.strftime('%Y-%m-%d-%H-%M-%S.%f')
                  #
                  # and sorted on that string. Now, use time object directly:
                  self.scanner_events_dict[event_to_find] = date_time_object
                  # and sort on that object directly.

                  break # Should break out the "this_line" loop, and go to next
                        # iteration in "event_to_find" loop.

               except AttributeError:

                  print ("Log line not properly formed. Move to next, properly written, event.")

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

         The events fed to this function should be an event label (as
         the 'key' for that event in the dictionary, and the 'value'
         corresponding to that key is now a Python 'datetime' object.

      """

      std_event_dict_returned = {}

      for event in scanner_events.keys():

         if (event == 'Patient registered'):
            patient_time_object_registered   = scanner_events[event]
         if (event == 'EVENT_PATIENT_DEREGISTERED'):
            patient_time_object_deregistered = scanner_events[event]

      # In the Siemens log, the 'Patient registered' message shows up *BOTH*
      # when the patient is registered, *AND* when the patient is deregistered.
      # However, in the latter case, the 'EVENT_PATIENT_DEREGISTERED' flag is
      # almost immediately adjacent in time.  Pick a small time delta (here 3s)
      # to determine the separation of the flags, to figure out if a patient has
      # been registered on the console interface or not.
      if ((patient_time_object_registered - patient_time_object_deregistered).total_seconds() < 3):
         scanner_state = 'End scanning session'
      else:
         scanner_state = 'Start scanning session'

      # Now, iterate through list of events, translate dictionary keys to more
      # standardized labels, and keep times of each event
      standardized_scanner_events = {}
      for event in scanner_events.keys():
         if (event == 'Patient registered'):
            standardized_scanner_events[scanner_state] = scanner_events[event]
         if (event == 'SCANNER prepare finished ok'):
            standardized_scanner_events['Pulse sequence prepped'] = scanner_events[event]
         if ((event == 'MSR_OK') or (event == 'MSR_STARTED')):
            standardized_scanner_events['Scanner is acquiring data'] = scanner_events[event]
         if ((event == 'MSR_MEAS_FINISHED') or (event == 'MSR_ACQ_FINISHED') or (event == 'MSR_SCANNER_FINISHED')):
            standardized_scanner_events['Scanner is done acquiring data'] = scanner_events[event]

      return (standardized_scanner_events)



   """

      Up till this point in this 'handler' module there are matching/corresponding
      functions in each vendors' library, but with implementations specific to each
      vendor.

      Below this will likely be functions specific to each vendors' platform.

   """



   async def read_other_resources (self, scanner_events_dict):

      """
         General entry point to aggregate vendor specific methods to read and
         parse other sources of info.

      """

      # await self.check_inline_export_log(scanner_events_dict, export_log='/tmp/.dcmRxInfo.log')
      await self.check_inline_export_tcp(scanner_events_dict, host="10.0.144.50", port=8111)



   async def check_inline_export_tcp (self, scanner_events_dictionary,
                                      host="192.168.2.5", port=5000):
      """
         This routine will parse the log output from the inline real-time export log.
         It will determine the start (MEAS_START) and stop (MEAS_FINISHED) of image
         reconstruction, as flags for these are not reliably written to the system's
         logs on the console that routines here get most of their info from.
      """

      socket_server = await asyncio.start_server(self.simple_async_socket_server,
                                                 host=host, port=port)
      async with socket_server:
         await socket_server.serve_forever()

      return



   async def simple_async_socket_server(self, reader, writer):

      """
         Create simple async socket initialization and listening
         routine.
      """

      data = await reader.read(1 * 1024 * 1024)
      lines = data.decode('utf-8').splitlines()

      if len(lines) > 0:
         for each_line in lines:

            # Check for MEAS_ in message string, and if present, add
            # current system date and time to that line.
            if "MEAS_".casefold() in each_line.casefold():
               # Pre-pend date and time, match format already used in
               # Siemens' logs, i.e. date: yyyy-mm-dd, and time:
               # HH:MM:SS.milliseconds
               current_time = datetime.datetime.now()
               print(current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + ' ' + each_line)
            else:
               print(each_line)



   async def check_inline_export_log (self, scanner_events_dictionary,
                                      export_log='/var/log/dcmRxInfo.log'):
      """
         This routine will parse the log output from the inline real-time export log.
         It will determine the start (MEAS_START) and stop (MEAS_FINISHED) of image
         reconstruction, as flags for these are not reliably written to the system's
         logs on the console that routines here get most of their info from.
      """

      event_date_time_00 = re.compile(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}')

      # with open (export_log, 'r') as fifo_rt:
      async with aiofiles.open (export_log, mode='r') as fifo_rt:

         print (f"FIFO '{export_log}' opened for reading. Waiting for data...")

         # os.set_blocking(fifo_rt.fileno(), False)

         while True:

            select.select([fifo_rt], [], [], 0.1)

            data = await fifo_rt.read()

            if data:
               current_line = data.strip()

               if ('MEAS_' in current_line):
                  meas_event_time = event_date_time_00.search(current_line)
                  meas_event_datetime = datetime.datetime.strptime(meas_event_time.group(),
                                                                   '%Y-%m-%d  %H:%M:%S')
                  if ('MEAS_START' in current_line):
                     print ("Image recon started at: %s" % str(meas_event_datetime))
                  else: # MEAS_FINISHED
                     print ("Image recon ended at: %s" % str(meas_event_datetime))
               elif ('DICOMIMA' in current_line):
                  print ('Image file written:' + current_line)
                  pass
               else:
                  print (f'Unknown line received: {current_line}')
            else:
               await asyncio.sleep (0.1)  # If no new lines, sleep briefly
               pass

      return

