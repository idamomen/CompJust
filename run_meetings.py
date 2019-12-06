import numpy as np
import institution as environment
#import environment_new as environment
import workerAgentObjects as workerAgent
import meeting as meeting


def run_meetings(gender_ratio, n_meetings, *args):

    # 1 MAKE ENV with said gender ratio         

    if len(args)>0: # sexism probabilities from a past envrionment are passed
        
        env=environment.environment(gender_ratio,args[0],args[1])
    else:
        env=environment.environment(gender_ratio)
        
    # 2 STORE sexism distributions before convos
    env.sexf_bef=env.sexp_f
    env.sexm_bef=env.sexp_m
        
    # 3 RUN 1000 CONVERSATIONS in this ENV
    env.max_convos=n_meetings
        
    for i in range(1,env.max_convos): # e.g. 500, 1000
        # create conversation in environment
        meet_sim=meeting.meeting(env)
        # get the conversation outcome
        env=meet_sim.convo_outcome(env)

    env.gettotalcost()    
        
    return env