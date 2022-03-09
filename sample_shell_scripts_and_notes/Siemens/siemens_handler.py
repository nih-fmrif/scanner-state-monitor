
#!/usr/bin/env python

# Basic infrastruture to parse Siemens scanner logs

import      re





scanner_events = ['MSR_OK', 'MSR_STARTED', 'MSR_SCANNER_FINISHED',
                  'MSR_ACQ_FINISHED', 'MSR_MEAS_FINISHED',
                  'EVENT_PATIENT_DEREGISTERED']

event_date     = re.compile(r'\d{4}-\d{2}-\d{2}')
event_time     = re.compile(r'\d{2}:\d{2}:\d{2}.\d{3}')





class log_parser():

   """
      Parser of scanner log files to catch events,
      and determine the date and time of those events.
   """



   def __init__():

      """
         Nothing currently implemented for init.
         Keep in mind to catch scanner vendor, and
         possibly platform version here, as entry
         point for more specific implementations.
      """



   def find_event (event_to_find, log_to_search):

      """
         Parse through logs passed to this routine
         (usually an array containing lines of text,
         read in from scanner's log files).
      """

      for current_line in log_to_search:

         # first determine if the line contains any
         # event of interest.

         # # if an event *is* in current_line
         # if any(this_event in current_line for this_event in scanner_events):

            # # get the event itself, by finding intersection of set of events
            # # possible, and the text in the line.
            # # have to remove parentheses to match to array of events.
            # current_line_elements   = current_line.replace("(","").replace(")","").split()
            # current_event           = set(current_line_elements) & set(scanner_events)

         # slightly modify code to search for a specific event, versus searching
         # over all possible events, as was done above
         if (event_to_find in current_line):

            # then get the event's date and time.
            this_event_date         = event_date.search(current_line)
            this_event_time         = event_time.search(current_line)

            print ("Event %s happened at date: %s, time: %s" % (event_to_find, this_event_date.group(), this_event_time.group()))

            # return (event_to_find, this_event_date.group(), this_event_time.group())

         else:

            # Have to handle error for event being searched for not in
            # list of events.

            print ("Event %s not found!" % event_to_find)
            # pass

