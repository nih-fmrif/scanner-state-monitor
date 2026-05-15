
#!/usr/bin/env python3

import asyncio
import datetime



async def simple_async_socket_server(reader, writer):

      """
         Create simple async socket initialization and listening
         routine.
      """

   # while True:

      data  = await reader.read(1*1024*1024)
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



async def main():

   try:
      # Create the server
      socket_server = await asyncio.start_server(simple_async_socket_server,
                                                 host='localhost', port=5000)
      async with socket_server:
         await socket_server.serve_forever()
   finally:
      exit()



if __name__ == "__main__":

   asyncio.run(main())

