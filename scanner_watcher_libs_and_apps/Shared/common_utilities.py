
#!/usr/bin/env python

import   os
import   logging



logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%Y_%m_%d %H:%M:%S :',
                    level=logging.WARNING)
common_event_logger = logging.getLogger(__name__)



class routines():

   """
      This will serve as a place-holder for routines and functions
      that can be used by any module.

      Routines added here must be self-contained, and should *NOT*
      depend on external or global variables for functionality.
   """



   def __init__(self):

      """
         Place-holder initializer routine.
      """

      pass



   def check_env_vars(env_variables_list):

      '''
         Utility to check that all needed enviroment variables are defined before
         executing rest of code.
      '''

      for each_variable in env_variables_list:
         try:
            os.environ[each_variable]
            common_event_logger.info(f"Environment variable: {each_variable} set to {os.environ[each_variable]}.")
         except KeyError:
            common_event_logger.error(f"Unable to find required variable: {each_variable} in environment - please define.")
            raise SystemExit(1)

