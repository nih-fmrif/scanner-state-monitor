
'''
   This module attempts to create a common location to set up the list of needed
   / expected generic MRI scanner events, and their corresponding items on the
   various vendors' platforms.

   This will be set as a Pandas data frame, which each vendor as a column label,
   and with each 'event' forming a row.
'''



import pandas



vendors = ['Generic', 'GEHC', 'Siemens']
events  = [['00_Generic', '00_GEHC', '00_Siemens'],
           ['01_Generic', '01_GEHC', '01_Siemens'],
           ['02_Generic', '02_GEHC', '02_Siemens']]

base_df = pandas.DataFrame.from_records(events, index=None, columns=vendors)

# Now, take data frame of generic and vendor-specific scan events, and make a new
# data frame, with the vendors as the column labels, and the generic scan events
# as the row keys/labels.

scanner_events_df = pandas.DataFrame(base_df.loc[:, vendors[1:]].to_numpy(), index=base_df['Generic'].values.tolist(), columns=vendors[1:])

# Check each vendor's list of events
print(scanner_events_df['GEHC'])
print(scanner_events_df['Siemens'])

# and entire new data frame
print(scanner_events_df)

