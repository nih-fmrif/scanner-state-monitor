
#!/usr/bin/env python

# Basic infrastruture to parse Siemens scanner logs

import      re





class log_parser():

   """
      Parser of scanner log files to catch events,
      and determine the date and time of those events.
   """



   def __init__(self, scanner_vendor='siemens', platform_version='ve11c'):

      """
         Nothing currently implemented for init.
         Keep in mind to catch scanner vendor, and
         possibly platform version here, as entry
         point for more specific implementations.
      """

      if (scanner_vendor == 'siemens') and (platform_version == 've11c'):
         self.event_date      = re.compile(r'\d{4}-\d{2}-\d{2}')
         self.event_time      = re.compile(r'\d{2}:\d{2}:\d{2}.\d{3}')

         self.scanner_events  = ['MSR_OK', 'MSR_STARTED', 'MSR_SCANNER_FINISHED',
                                 'MSR_ACQ_FINISHED', 'MSR_MEAS_FINISHED',
                                 'EVENT_PATIENT_DEREGISTERED']



   def find_event (self, event_to_find, log_to_search):

      """
         Parse through logs passed to this routine
         (usually an array containing lines of text,
         read in from scanner's log files).
      """

      for current_line in log_to_search:

         # # If any event is in current_line - capture and print.
         # if any(this_event in current_line for this_event in self.scanner_events):

            # # get the event itself, by finding intersection of set of events
            # # possible, and the text in the line.
            # # have to remove parentheses to match to array of events.
            # current_line_elements   = current_line.replace("(","").replace(")","").split()
            # current_event           = set(current_line_elements) & set(self.scanner_events)

         # Make sure we are dealing with event we can handle
         if (event_to_find in self.scanner_events):
            # Then determine if the line contains the event of interest.
            if (event_to_find in current_line):

               # If it does, then get the event's date and time.
               this_event_date         = self.event_date.search(current_line)
               this_event_time         = self.event_time.search(current_line)

               print ("Event %s happened at date: %s, time: %s" % (event_to_find, this_event_date.group(), this_event_time.group()))

               # return (event_to_find, this_event_date.group(), this_event_time.group())

         else:

            # Have to handle error for event being searched for not in list
            # of events.

            print ("Event %s not in list of possible events!" % event_to_find)
            break

