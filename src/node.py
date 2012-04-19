# A user class which stores information about each user
class User:
    
    user_id = 0
    total_number_of_users = 0
    
    # Format: [<location_id, count>]
    eigen_value = []
    
    is_expert = 0
    
    input_msg_buffer = []
    
    # Personal encounter log format:
    # <user_id:integer, location_id:integer, timestamp:encounter_graph>
    personal_encounter_log = []
    tags = []
    
    # Question indexed by ids
    # Format: [<question_text>]
    questions = []
    
    # list of lists. answer_folder[i] contains responses for questions[i][1]
    # Format for question[i][1]: <expert_id, ev_expert, answer>
    answer_folder = []
    
    def __init__(self, unique_id, maxUsers, maxLocations):
        self.user_id = unique_id
        self.total_number_of_users = maxUsers
        self.total_number_locations = maxLocations
        self.eigen_value = []
        self.is_expert = 0
        self.tags = []
        self.answer_folder = []
        self.questions = []
        self.personal_encounter_log = []
        self.input_msg_buffer = []
        
    def update_tag(self, some_tag):
        add = 0
        eigen_value = self.generate_ev()
        for val in eigen_value:
            if some_tag[1] == val[0]:
                add = 1
                break;
        if add == 1:
            self.tags.append(some_tag)
            self.tags = set(self.tags)
        
    def set_expert(self):
        self.is_expert = 1
        
    def generate_ev(self):
        if not self.eigen_value:
            
            locations_visited = [location[1] for location in \
                                 self.personal_encounter_log]
            unique_locations = list(set(locations_visited))
            for i in range(len(unique_locations)):
                self.eigen_value.append((unique_locations[i], \
                                         locations_visited.count(unique_locations[i])))
            return self.eigen_value
        else:
            return self.eigen_value

    def add_witness_data(self, record):
        self.personal_encounter_log.append(record)

    def has_seen(self, expert, tag, threshold):
        count = 0
        for encounter in self.personal_encounter_log:
            if tag[1] == encounter[0]:
                if expert == encounter[0]:
                    count = count + 1
                else:
                    count = count - 1
                      
        if count > 0:
            return 1
        elif count < 0:
            return -1
        else:
            return 0
    
    def add_expert_to_response(self, expert, ev_expert, some_question, some_answer):
        for i in range(len(self.questions)):
            if self.questions[i] == some_question:
                arr = (expert, ev_expert, some_answer, some_question)
                if arr not in self.answer_folder:
                    self.answer_folder.append(arr)    
        return
    
    def is_similar(self, ev_asker, threshold):
        similarity = 0
        for val in ev_asker:
            for rval in self.eigen_value:
                if rval[0] == val[0]:
                    similarity = similarity + 1
        
        if similarity > threshold:
            return 1
        else:
            return 0
    
    def add_to_buffer(self,packet):
        if packet not in self.input_msg_buffer:
            self.input_msg_buffer.append(packet)
    def remove_from_buffer(self,packet):
        if packet in self.input_msg_buffer:
            self.input_msg_buffer.remove(packet)
    def seek_input_msg_buffer(self):
        return self.input_msg_buffer