#!/usr/bin/env python
# coding: utf-8


import os, re
import select
import datetime
import asyncio
import aiofiles



FIFO_PATH = "/tmp/.dcmRxInfo.log"
EVENT_LOG = os.environ['MRI_SCANNER_LOG_DIR'] + "MrMeas_container.log"



async def check_inline_export_log (scanner_events_dictionary,
                             export_log='/var/log/dcmRxInfo.log'):

   """
      This routine will parse the log output from the inline real-time export log.
      It will determine the start (MEAS_START) and stop (MEAS_FINISHED) of image
      reconstruction, as flags for these are not reliably written to the system's
      logs on the console that routines here get most of their info from.
   """

   event_date_time_00 = re.compile(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}')

   # with open (export_log, 'r') as fifo_rt: # Blocking I/O - if used.
   async with aiofiles.open (export_log, mode='r') as fifo_rt:

      print (f"FIFO '{export_log}' opened for reading. Waiting for data...")

      # await fifo_rt.seek(0, os.SEEK_END)   # No need to seek to end of a pipe

      while True:

         select.select([fifo_rt], [], [], 0.1)

         data = await fifo_rt.read()   # For FIFO object, need to use 'read'
                                       # method. For files, 'readline' works.
         if not data:
            await asyncio.sleep (0.1)  # If no new lines, sleep briefly

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
               # print ('Image file written')
               pass
            else:
               print (f'Unknown line received: {current_line}')
         else:
            pass

   return



async def check_scanner_events_log (scanner_events_dictionary,
                              events_log='MrMeasContainer.log'):

   """
      This routine will tail the log output from the scanner's generic event log.
   """

   async with aiofiles.open (events_log, mode='r') as fifo_rt:

      await fifo_rt.seek(0, os.SEEK_END)  # Go to end of file and tail new lines

      while True:

         line = await fifo_rt.readline()

         if not line:
            await asyncio.sleep (0.1) # If no new lines, sleep briefly

         current_line = line.strip()

         if ('sending SCT start command' in current_line):
            print (f'starting sequence line received: {current_line}')
         elif ('MeasCtrlService::handleEvent: Event ' in current_line):
            print (f'meas control line received: {current_line}')
         else:
            pass

   return



async def main():

   scan_events_dict = dict()
   read_file_tasks  = []

   print ("Opening scanner event log at: %s" % EVENT_LOG)
   read_scanner_log = asyncio.create_task(check_scanner_events_log (scan_events_dict, events_log=EVENT_LOG))
   read_file_tasks.append(read_scanner_log)

   print ("Opening export log FIFO pipe at: %s" % FIFO_PATH)
   read_export_log  = asyncio.create_task(check_inline_export_log  (scan_events_dict, export_log=FIFO_PATH))
   read_file_tasks.append(read_export_log)

   await asyncio.gather(*read_file_tasks)



asyncio.run(main())

