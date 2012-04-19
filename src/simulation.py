import analyzer
import node
import time_converter
import random
import trust


#time_slice = int(raw_input("Please enter the time slice value for encounter graph"\
#                       +"(in hours: mail <arijit@cise.ufl.edu> for details): "))
time_slice = 6
target = raw_input("Please enter location of files: ")
f = open(target+"/trace_training").read()

# Format: <user_id1, user_id2, unix_timestamp, location>
lines = [line.strip(" ") for line in f.split('\n')]
# lines.remove(lines[len(lines)-1]) # just to clean the data

users = []
locations = []

for line in lines:
    arr = line.split(' ')
    users.append(int(arr[0]))
    locations.append(arr[3])

users = list(set(users))
total_users = len(users)
locations = list(set(locations))

# Contains class instances of User
user_list = [node.User(user,len(users),len(locations)) for user in users]

tags = (("football", locations[random.randint(0,len(locations)-1)]),\
        ("study", locations[random.randint(0,len(locations)-1)]),\
        ("eat", locations[random.randint(0,len(locations)-1)]))

# A python dictionary for quickly finding locations
location_dict = dict([(locations[i],i) for i in range(len(locations))])
    
# use training data to fill up user scores
for line in lines:
    arr = line.split(' ')

    time_unit = time_converter.unix_timestamp_convert(int(arr[2]), time_slice)
    # <user_id:integer, location_id:integer, timestamp:unix_timestamp>
    user_list[users.index(int(arr[0]))].add_witness_data((int(arr[1]), \
                                                   location_dict[arr[3]], time_unit))        

print "Analyzed training data"
threshold = int(raw_input("Please enter a threshold value (0-low, 1-medium, 2-high): "))
f = open(target+"/trace_testing").read()

# Format: <user_id1, user_id2, unix_timestamp, location>
lines = [line.strip(" ") for line in f.split('\n')]
# lines.remove(lines[len(lines)-1]) # just to clean the data

encounters = []

# Add tags
print("Adding tags: ")
print tags

for user in user_list:
    for tag in tags:
        user.update_tag(tag)

time_units = []

for line in lines:
    arr = line.split(' ')
    user1 = int(arr[0])
    user2 = int(arr[1])
    time_stamp = int(arr[2])
    time_unit = time_converter.unix_timestamp_convert(time_stamp, time_slice)
    location = location_dict[arr[3]]
    time_units.append(time_unit)
    
    encounters.append((user1, user2, time_unit, location))

time_units.sort()

total_encounters = len(encounters)

#asker = encounters[random.randint(0,total_encounters-1)][0]
#expert = encounters[random.randint(0,total_encounters-1)][0]
#while asker == expert:
#    expert = encounters[random.randint(0,total_encounters-1)][0]
    
asker = 3
expert = 1

# incoming packet:
# [source, destination, asker, expert, TTL, question, answer,
# {{tag1,location1}, {tag2,location2}...{tagn, locationN}},
# {confidence1, confidence2...confidenceN}, ev_asker, ev_expert]

print "Starting simulation"
print "\nCreating a simulation packet with following contents: "
print "\t1. source_id: source id of transmitting node"
print "\t2. destination_id: destination id of receiving node"
print "\t3. asker: user_id of asker (randomly generated for simulation: " +\
 str(asker) + ")"
print "\t4. expert: user_id of expert (randomly generated for simulation: " +\
 str(expert) + ")"
#ttl = int(raw_input("\t5. enter TTL(time-to-live): "))
ttl = 4
print "\t6. question: Where can be play football?"
print "\t7. answer: NULL"
print "\t8. tags (array): {<tag1,location1>, <tag2,location2>,...}"
print "\t9. confidence (array): {confidence1, confidence2,...}"
print "\t10. ev_asker (array): Eigen value of asker"
print "\t11. ev_expert (array): Eigen value of expert"

print "Placing packet in input message buffer of asker..."

# epidemic flooding starting with asker
question_tag = ("Where can we watch movies?", "movies")
user_list[users.index(asker)].questions.append(question_tag[0])

for encounter in encounters:
    # epidemic flooding
    sent_list = []
    if encounter[0] == asker:
        if encounter[1] not in sent_list:
            sent_list.append(encounter[1])
        else:
            continue
        this_packet = (asker, encounter[1], asker, 0, ttl,\
       question_tag[0], 0,[(question_tag[1],0)],\
       [0],user_list[users.index(asker)].generate_ev(), [0])
        user_list[users.index(encounter[1])].add_to_buffer(this_packet)
        
user_list[users.index(expert)].is_expert = 1


o = open(target+"/plotter.py",'w')
o.write('import networkx as nx\n')
o.write('import matplotlib.pyplot as plt\n')

for time_unit in time_units:
    o.write('\nplt.clf()\n')
    o.write('G=nx.DiGraph()\n')

    # process each users incoming and outgoing packets
    for user in user_list:
        if len(user.seek_input_msg_buffer()) > 0:
            for packet in user.seek_input_msg_buffer():
                arr = analyzer.analyzePacket(time_unit, packet, \
                              threshold, user_list, users, encounters)
                if arr[0] != -1:
                    o.write("G.add_edge("+str(arr[0])+","+str(arr[1])+")\n")
                    
#    print "time: "+str(time_unit)
#    for user in user_list:
#        for msg in user.seek_input_msg_buffer():
#            print msg
#        if len(user.answer_folder) > 0:
#            print user.answer_folder
#        print "\n"

    o.write("nx.draw_random(G)\n")
    o.write("plt.savefig('path_"+str(time_unit)+".png')")
o.close()

print "\n\nQuestion asked: '" + question_tag[0] + "' by Asker: " + str(asker)
if len(user_list[users.index(asker)].answer_folder) > 0:
    print 'Simulation successful.'
    for msg in user_list[users.index(asker)].answer_folder: 
        print "Answer: '" + msg[2] + "' by Expert: " + str(msg[0])
else:
    bad_replies = []
    if len(user_list[users.index(asker)].input_msg_buffer) > 0:
        for msg in  user_list[users.index(asker)].input_msg_buffer:
            if msg[3] != 0:
                if trust.enough_confidence(msg[8], 0) != 1:
                    # format: <expert_id, confidence, answer>
                    bad_replies.append((msg[3],msg[8],msg[6]))
    if len(bad_replies) > 0:
        print 'Received bad responses such as: Expert: '+\
        str(bad_replies[0][0])+' Confidence Score: '+\
        ' '.join([str(reply) for reply in bad_replies[0][1]])+' Answer: '+bad_replies[0][2]
    else:
        print 'No bad responses'
