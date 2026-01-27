
# inspired by examples at:
#
#   https://tutorialedge.net/python/concurrency/asyncio-event-loops-tutorial/

import asyncio
import requests
import datetime



state_poll_interval = 1.0   # in seconds
state_src_url       = 'http://localhost:5000/scanner_state'



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

      print('   \n   Scanner: ' + data['scanner AE Title'] + " from vendor: " + data['scanner vendor'] + " has events: " + str(data['all_events'])
            + ' detected at ' + current_state_check_date_time + '\n')

      process_current_state (current_state_dict)



def process_current_state(state_to_process):

   print ("\n *** Additional code to execute here ***, based on dictionary of state: %s \n" % (str(state_to_process)))

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

