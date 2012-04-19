import ui
import trust

msg = ''
out_ttl = 6
response_threshold = 1
# threshold values: 0 (low), 1 (medium), 2 (high)

# incoming packet:
# [source, destination, asker, expert, TTL, question, answer,
# {{tag1,location1}, {tag2,location2}...{tagn, locationN}},
# {confidence1, confidence2...confidenceN}, ev_asker, ev_expert]

def analyzePacket(simulation_time, incoming_packet, threshold, user_list, users, encounters):
    source = incoming_packet[0]
    destination = incoming_packet[1]
    asker = incoming_packet[2]
    expert = incoming_packet[3]
    ttl = incoming_packet[4]
    question = incoming_packet[5]
    answer = incoming_packet[6]
    tags = incoming_packet[7]
    confidence = incoming_packet[8]
    
    ev_asker = incoming_packet[9]
    ev_expert = incoming_packet[10]
    
    this_user = user_list[users.index(destination)]
    
    if ttl < 1:
        # drop packet if it has expired
        this_user.remove_from_buffer(incoming_packet)
        if answer == 0:
            msg = question
        else:
            msg = answer
        return (-1, -1, msg)
    
    if this_user.user_id == asker:
        # dynamic tagging initiation phase
        if trust.enough_confidence(confidence, threshold) == 1:
            # if participating users are confident of expert
            # send expert's response (answer) offline to
            # storage where it will be clustered along
            # other expert responses and displayed on
            # user's screen asynchronously (not in simulation)
            this_user.add_expert_to_response(expert, ev_expert, question, answer)
            if answer == 0:
                msg = question
            else:
                msg = answer
            # drop packet
        this_user.remove_from_buffer(incoming_packet)
        if answer == 0:
            msg = question
        else:
            msg = answer
        return (source, destination, msg)

    if expert == 0:
        # broadcast message: looking for experts!
        # query creation and forwarding phase
        
        owner_response = ui.display_user(this_user, tags, question)
        # owner_response: {yes/no, {{tag, location}...}, answer, ev_thisNode}
        if  owner_response[0] == 1:
            # current node's device owner 
            # identifies him/herself as an expert
            
            # send packet containing expert response to nbrs
            response = 0
            for encounter in encounters:
                if encounter[2] == simulation_time:
                    if encounter[0] == this_user.user_id:
                        response = response + 1
                        # send response to nbr
                        this_packet = (this_user.user_id, encounter[1], asker, this_user.user_id,\
                                       out_ttl, question, owner_response[2],\
                                       owner_response[1],\
                                       [0 for i in range(len(owner_response[1]))],\
                                       ev_asker,\
                                       owner_response[3])
                        user_list[users.index(encounter[1])].\
                        add_to_buffer(this_packet)
            if response > response_threshold:
                this_user.remove_from_buffer(incoming_packet)
            # keep message in buffer
            if answer == 0:
                msg = question
            else:
                msg = answer
            return (source, destination, msg)
        else:
            # no response from owner just forward packet
            response = 0
            # epidemic flooding
            for encounter in encounters:
                if encounter[2] == simulation_time:
                    if encounter[0] == this_user.user_id:
                        response = response + 1
                        this_packet = (this_user.user_id, encounter[1], asker, expert,\
                                       ttl-1, question, answer, tags,\
                                       confidence, ev_asker, [])
                        user_list[users.index(encounter[1])].\
                        add_to_buffer(this_packet)
            if response > response_threshold:
                this_user.remove_from_buffer(incoming_packet)
            
            if answer == 0:
                msg = question
            else:
                msg = answer
            return (source, destination, msg)
    else:
        # expert identification phase
        # message is being sent by self-identified
        # ...expert to asker
        
        if this_user.user_id == expert:
            this_user.remove_from_buffer(incoming_packet)
            if answer == 0:
                msg = question
            else:
                msg = answer
            return (-1, -1, msg)
        else:
            
            # scoped routing/gradient descent:

            if trust.enough_confidence(confidence, threshold) == 1:
                # enough confidence votes (negative/positive)
                # have been obtained. Send packet to users who mobility
                # matches Asker
                
                # confidence is high but drop packet current user is not similar
                # to asker
                          
                if this_user.is_similar(ev_asker, threshold) == 0:
                    # asker is not similar to me
                    # drop packet
                    this_user.remove_from_buffer(incoming_packet)
                    color = 'red'
                    return (source, destination, color)               
                response = 0
                for encounter in encounters:
                    if encounter[2] == simulation_time:
                        if encounter[0] == this_user.user_id:
                            response = response + 1
                            this_packet = (this_user.user_id, encounter[1], asker, expert,\
                                           ttl-1, question, answer, tags,\
                                           confidence, ev_asker, ev_expert)
                            user_list[users.index(encounter[1])].\
                            add_to_buffer(this_packet)
                if response > response_threshold:
                    this_user.remove_from_buffer(incoming_packet)
            
            elif trust.enough_confidence(confidence, threshold) == -1:
                # bad response
                # drop packet
                this_user.remove_from_buffer(incoming_packet)
            else:
                # need to forward the packet to users whose mobility
                # matches expert to obtain more votes 
                for i in range(len(tags)):
                    seen_before = this_user.has_seen(expert, tags[i], threshold)
                    if  seen_before == 1:
                        # this node visits tag,location frequently
                        # ...and has seen expert
                        confidence[i] = confidence[i] + 1
                    elif seen_before == -1:
                        # this node visits tag,location frequently
                        # ...and has NOT seen expert
                        confidence[i] = confidence[i] - 1
                
                response = 0
                for encounter in encounters:
                    if encounter[2] == simulation_time:
                        if encounter[0] == this_user.user_id:
                            response = response + 1
                            this_packet = (this_user.user_id, encounter[1], asker, expert,\
                                           ttl-1, question, answer, tags,\
                                           confidence, ev_asker, [])
                            user_list[users.index(encounter[1])].\
                            add_to_buffer(this_packet)
                if response > response_threshold:
                    this_user.remove_from_buffer(incoming_packet)
            if answer == 0:
                msg = question
            else:
                msg = answer
            return (source, destination, msg)