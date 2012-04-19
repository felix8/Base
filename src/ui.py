# import random

def display_user(user, required_tags, question):
    # response: {yes/no, {{tag, location}...}, answer, ev_thisNode}
    if user.is_expert == 1:
        ev = user.generate_ev()
        # location = ev[random.randint(0,len(ev))][0]
        location = 1
        return (1,[("movies",location)],"next movie: Hugo",ev)
    else:
        return (0,[],0)
    return