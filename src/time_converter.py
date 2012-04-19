import datetime
from time import strftime

def unix_timestamp_convert(timestamp, time_slice):
    return timestamp
#    return int(datetime.datetime.fromtimestamp(timestamp).strftime("%j")) +\
#         (int(datetime.datetime.fromtimestamp(timestamp).strftime("%H"))/time_slice)