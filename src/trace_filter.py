# Created by Arijit Choudhury
# A python file for filtering the UF traces

from operator import itemgetter
from datetime import datetime

import time

input_folder = raw_input("Please provide the location (folder) of your trace file: ")

f = open(input_folder + '/nov07_trace_sorted_id').read()
lines = f.split('\n')

lines.remove(lines[len(lines)-1])

# Trace format: user_id1 user_id2 unix_timestamp location_id encounter_duration

records = []
for line in lines:
    arr = line.split(' ')
    user_id1 = arr[0]
    user_id2 = arr[1]
    unix_timestamp = datetime.fromtimestamp(int(arr[2]))
    location_id = arr[3]
    records.append((user_id1, user_id2, unix_timestamp, location_id))

records = sorted(records, key = itemgetter(2))

print "Total number of records (encounters): " + str(len(records))
print "Start Date of Records: " + records[0][2].strftime('%m/%d/%Y %H:%M:%S')
print "End Date of Records: " + records[len(records)-1][2].strftime('%m/%d/%Y %H:%M:%S')

choice = 'y'

while choice.lower() == 'y':
    # Python datetime format: (yyyy, mm, dd, ss, 00)
    arr = raw_input("Please enter the start date (mm/dd/yyyy): ").strip(' ').split('/')
    start_time = datetime(int(arr[2]), int(arr[0]), int(arr[1]), 0 , 0)
    
    arr = raw_input("Please enter the end date (mm/dd/yyyy): ").strip(' ').split('/')
    end_time = datetime(int(arr[2]), int(arr[0]), int(arr[1]), 0 , 0)
    
    location = raw_input("Please enter a location to filter (see http://campusmap.ufl.edu/)"+\
                    " e.g. for Computer Science building type 'CSE': ").lower().strip(' ')
    filtered_records = []
    
    for record in records:
        if record[2] >= start_time and record[2] <= end_time:
            filtered_records.append(record)
    
    cise_users = []
    
    for record in filtered_records:
        if location in record[3]:
            cise_users.append((record[0], record[2].timetuple()[2]))
    
    cise_users = list(set(cise_users))
    unique_users = list(set([user[0] for user in cise_users]))
    
    final_users = []
    
    for user in unique_users:
        days = []
        for someuser in cise_users:
            if someuser[0] == user:
                days.append(someuser[1])
        if len(set(days)) > 4:
            final_users.append(user)
    
    print final_users
    
    filtered_records = []
    for record in records:
        if record[2] >= start_time and record[2] <= end_time:
            if record[0] in final_users and record[1] in final_users:
                filtered_records.append(record)
    
    filtered_records = [str(record[0])+' '+str(record[1])+' '+\
                        str(int(int(record[2].timetuple()[2]) * 4 + int(record[2].timetuple()[3]) % 6))+' '+\
                        record[3] for record in filtered_records]
    
    filtered_records = list(set(filtered_records))
    
    o = open(input_folder+'/nov07_'+str(start_time)+'_'+str(end_time)+'_trace_sorted_id', 'w')
    print 'Results written to: '+input_folder+'/nov07_'+str(start_time)+'_'+str(end_time)+'_trace_sorted_id'
    o.write('\n'.join(filtered_records))
    o.close()
    
    choice = raw_input("Any more samples required? (Y/N): ")
