
# inspired by examples at:
#
#   https://tutorialedge.net/python/concurrency/asyncio-event-loops-tutorial/

import asyncio
import requests
import datetime
import logging
import json


state_poll_interval = 0.5   # in seconds
state_src_url       = 'http://localhost:5000/scanner_state'
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y_%m_%d %H:%M:%S :', level=logging.WARNING)
scan_event_logger   = logging.getLogger(__name__)



async def poll_state(state_url, polling_interval):

   while True:

      current_state_dict  = {}

      await asyncio.sleep(polling_interval)

      try:

         # poll URL where state is published to
         state = requests.get(state_url)

      except:

          print("Couldn't reach URL: %s to determine scanner state." % state_url)

          continue # To next iteration of while loop, skipping code below

      # get date and time at which scanner state is polled
      current_state_check_date_time = datetime.datetime.now().strftime("%Y_%m_%d_%H:%M:%S")

      # Convert published JSON struct to Python dictionary
      data = state.json()

      # Extract desired information from packet
      current_state_dict = data['all_events']

      scan_event_logger.info('Scanner: ' + data['scanner AE Title']
            + " from vendor: " + data['scanner vendor'] + " has events: "
            + str(data['all_events']) + ' detected at '
            + current_state_check_date_time + '\n')

      process_current_state (data)  # Pass along request response as json, and
                                    # process appropriately in calling function.



def process_current_state(state_to_process):

   scanner_ae_title   = state_to_process['scanner AE Title']
   scanner_vendor     = state_to_process['scanner vendor']

   # Convert dictionary of scanner state events directly into time-ordered list,
   # using lambda function
   time_ordered       = sorted(state_to_process['all_events'].items(),
                               key=lambda item: item[1], reverse=False)

   print ("\n *** For scanner %s, from vendor %s, current order of events at %s is:\n"
          % (scanner_ae_title, scanner_vendor, datetime.datetime.now().strftime("%Y_%m_%d_%H:%M:%S")))

   for events in time_ordered:
      print ("Event, %32s, occurred at %26s" % (events[0], events[1]))
   print ("\n")

   return



if __name__ == "__main__":

   loop = asyncio.get_event_loop()

   try:
      asyncio.ensure_future(poll_state(state_src_url, state_poll_interval))
      loop.run_forever()
   except KeyboardInterrupt:
      pass
   finally:
      print("Stopping task.")
      loop.close()

