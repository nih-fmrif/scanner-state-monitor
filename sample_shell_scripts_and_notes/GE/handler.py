
#!/usr/bin/env python

# Basic infrastruture to parse GE scanner logs

import      re





class event_catcher():

   """
      Parser of scanner log files to catch events,
      and determine the date and time of those events.
   """



   def __init__(self, scanner_vendor='ge', platform_version='dv26.0_r02'):

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
      if (scanner_vendor == 'ge'):
         if (platform_version == 'dv26.0_r02'):

            self.log_files = ['scn.out.0.gz', 'scn.out.1.gz', 'scn.out.2.gz',
                              'scn.out.3.gz', 'scn.out.4.gz', 'scn.out.5.gz',
                              'scn.out.6.gz', 'scn.out.7.gz', 'scn.out.8.gz',
                              'scn.out.9.gz', 'scn.out']

            self.log_files_dict = dict.fromkeys(self.log_files)

            self.event_date_00   = re.compile(r'\s{3} \s{3} \d{2} \d{4}')  # date format: Day-of-week Month Day-of-month YYYY
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



   def find_event (self, event_to_find, log_to_search):

      """
         Parse through logs passed to this routine
         (usually an array containing lines of text,
         read in from scanner's log files).
      """

      # Reverse order of log, so events that are recorded towards the end/bottom of the log
      # (i.e. later in time) show up first in this loop.  We want to catch the last/latest
      # occurence of each event.
      reversed_log = log_to_search[-1:0:-1]

      for this_line in reversed_log:

         try:
            current_line = this_line.decode('utf-8').strip()
         except UnicodeDecodeError:
            # print ("Cannot decode %s" % this_line)
            continue

         if (self.event_date_00.search(current_line) != None):
            this_event_date = self.event_date_00.search(current_line)

         # Make sure we are dealing with event we can handle
         if (event_to_find in self.scanner_events):
            # Then determine if the line contains the event of interest.

            if (event_to_find in current_line):

               # If it does, then get the event's date and time.
               this_event_time         = self.event_time_00.search(current_line)

               # print ("Event %45s happened at date: %s, time: %s" % (event_to_find, this_event_date.group(), this_event_time.group()))

               # return (event_to_find, this_event_date.group(), this_event_time.group())

               print ("Event %45s happened at time: %s" % (event_to_find, this_event_time.group()))

               return (event_to_find, None, this_event_time.group())

         else:

            # Have to handle error for event being searched for not in list
            # of events.

            print ("Event %45s not in list of possible events!" % event_to_find)
            return (None, None, None)

      # Handle event being valid, but not found at all in log.

      print ("Event %45s not found in log." % (event_to_find))

      return (event_to_find, None, None)

