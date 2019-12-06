import random
import numpy as np
import institution as environment # in the past we used class environment
import workerAgentObjects as workerAgent
#import networkx as nx

''' The class "meeting"s" implements the class "instituion". There,
parameters from empirical studies, in colab with Mina Cikara @Harvard. 

Every meeting happens among 2-8 agents sampled randomly from the total 
agents in the institution.

The main parameters are:

1) self objection (probability of objecting if there's sexism towards own group)

2) objection for other gender (probability of being an ally)

3) cost of objection for own gender is: 1, 
    cost of ally objection, i.e. objection for sexism against other gender: .9
    (based on empirical results)

4) change in behavior:

    increase in sexism: if a sexist comment happens in a meeting and no one objects,
    everyone from the perpetrator's gender increases their probabilty of sexism
    by 10% of the original probability (based on empirical studies)

    decrease in sexism: 10% or 5% of initial sexism decrease 
    if someone from same, or other, gender objects to sexism in the meeting.
    (based on empirical studies)

IM April 2019
'''

########################
class meeting(): 
    """ Define conversations: pick 2-8 random agents for convo
        apply rules for interactions and updating agents """

    # a random pick up of 2-8agents from all agents (100, or more when injecting women)
    def __init__(self, environment ):  
        self.verbose=0

        self.convo_id=environment.convos_sofar         # how many-th convo in the env is this?

        # 1- who's in the meeting?
        # 1.a randomly draw  2-8 agents from environment in meeting
        self.n_convo_agents=random.randint(2,8)

        # 1.b sample n_agents from the 100, determines gender dist         
        self.convo_agents = random.sample(range(environment.n_agents), 
                            self.n_convo_agents)

        if self.verbose:
            print("Environment with %s agents loaded." % environment.n_agents)
            print("Conversation %s started." % self.convo_id)
            print("Conversation has %s agents." % len(self.convo_agents))
        
        # 3 raise the num of meetings/convos so far in the institution/env 
        environment.convos_sofar+=1


    # 2 #############
    def gendering(self, environment):
        """ Get indices for male and female convo members """
        c_alist=self.convo_agents

        # BE CAREFUL ABOUT ENUMERATE! 
        # i: index, j: CONTENT.  Jan 25, 2019, IM
        self.males=[j for i, j in enumerate(c_alist) if environment.agent_list[j].gender is 'Male']

        if self.verbose:
            print('Men in convo: %s' % self.males)

        self.females=[j for i, j in enumerate(c_alist) if environment.agent_list[j].gender is 'Female']

        if len(self.females)*len(self.males)>0: 
            # counting number of meetings that include women at all
            environment.mixedgendermeetings+=1

        if self.verbose:
            print('Women in convo: %s' % self.females)    

    # 3 #############
    def convo_outcome(self, environment):

        """ Check if sexism occurs, againts men or women, update """

        self.gendering(environment)
        
        # if convo has 1 gender, well nothing
        # FUTURE: Locker room talk, and effect of objection when women are not around

        if len(self.females)==0 or len(self.males)==0: # unisex convo. no sexism
            if self.verbose:
                print('Only one gender in convo')
            self.no_sexism_happened(environment)

        # if both genders, depends
        else:                                   
            # one gender more: sexism contra other. equal: both can
            gender_diff = len(self.females)-len(self.males) 

            # MALEs OUTNUMBER
            if gender_diff<0: # or gender_diff==0:  
                self.check_male_sexism(environment)

            # FEMALEs OUTNUMBER
            elif gender_diff>0:   
                self.check_female_sexism(environment)

            # equal numbers of M & F in CONVO   
            elif gender_diff==0:
                self.check_male_sexism(environment)
                self.check_female_sexism(environment)    

        self.step(environment) # everyone steps forward
        return environment

    # 4 #############    
    def no_sexism_happened(self, environment):
        ''' Updates environment when no sexim happens during conversation '''

        environment.convo_sexism.append(0)
        environment.conv_no_sexism+=1
        return environment 

    # 5 #############
    def check_female_sexism(self, environment):
        ''' Check if FEMALE sexism probability leads to anti-MALE sexist behavior'''
        sexism=0
        for woman in self.females:
                    rand=random.random()
                    if environment.agent_list[woman].sexism >= rand:
                    #    print('sexism: {0}, rnd: {1}'.format(environment.agent_list[woman].sexism, rand))
                        self.anti_m_sexism(environment, woman)
                        sexism+=1

        if sexism==0:
            self.no_sexism_happened(environment)
        return environment

    # 6 #############
    def check_male_sexism(self, environment):
        ''' Check if MALE sexism probability leads to anti-FEMALE sexist behavior'''
        sexism=0
        for man in self.males:
                    rand=random.random()
                    if environment.agent_list[man].sexism >= rand:
                        #print('sexism: {0}, rnd: {1}, man: {2}'.format(environment.agent_list[man].sexism, rand, man))
                        self.anti_f_sexism(environment, man)
                        sexism+=1
        if sexism==0:
            self.no_sexism_happened(environment)
        return environment

    # 7 #############
    def check_for_objections(self, environment, victims, perpetrators):
        ''' This is called when sexism takes place, to check if anyone objects.
            Objections will depend on the probability of objection and allyship 
            in the agents present in the conversation.'''

        objection_occured = 0
        # in the new version, agents have prob objection

        # would victims object for self? check all target group agents
        targets_who_obj, victim_objects=[], 0
        for i in victims: 
            if environment.agent_list[i].objp>=random.random():
                victim_objects=1
                targets_who_obj.append(i) # these folks get a cost                


        # would allies object for victims? check all non-target agents     
        allies_who_obj, ally_objects=[], 0
        for j in perpetrators:
            if environment.agent_list[j].allyp>=random.random():
                ally_objects=1
                allies_who_obj.append(j)
                
        # then the learning should change depending on wehther objection happened or not


        if victim_objects:
            # all target_group who objected get cost. simple version
            cost=1
            self.sexism_step_size = -.05
            self.cost_to_objector(targets_who_obj, environment, cost)
            if self.verbose:
                print('Objection by Targets')
        else:
            self.sexism_step_size=.1 #no one objected, unless changed below, sexism increases

        if ally_objects:
            allycost=.8 # alternative: cummulative for number of perp_gender present
            self.sexism_step_size = -.1
            self.cost_to_objector(allies_who_obj, environment, allycost)                   
            if self.verbose:
                print('Objection by Allies')
        else:
            self.sexism_step_size=.1 #no one objected, sexism increases

        if victim_objects+ally_objects==0: #no one objected, sexism increases
            # no objections happened, probability of sexism in perpetrators goes higher
            self.sexism_step_size=.1
            # self.update_perpetuators(perpetuators, environment)  

        return environment

    # 8 #############    
    def anti_f_sexism(self, environment, perp_id):

        ''' Update environment & convo when anti_FEMALE sexism happens'''

        environment.convo_sexism.append(1)


        # parameter below is about anti_f events, not costs per se
        environment.anti_f_sexism += 1            
        
        # 1 UPDATE COSTS, not change sexism prob until OBJECTIONS are checked
        self.cost_to_victims(self.females, environment)  
        
        # 2 CHECK FOR OBJECTIONS: victims, perpetuators, determines: self.sexism_step_size
        self.check_for_objections( environment, self.females, self.males)

        # 3 UPDATE perpetrators, their sexism_step_size for sexism change, which determines if they get a cost or not
        self.update_perpetrators(self.males, environment, perp_id) 
                  
        # 4 SAVE INTERACTION in matrix/ later averaged across convos->graph
        len_f=len(environment.female_ind)
        vict_ind=[i for i,j in enumerate(environment.female_ind) if j in self.females]
        perp_ind=[i for i,j in enumerate(environment.male_ind) if j in self.males]


        
        #for perp in perp_ind:
        #    for vict in vict_ind:                
        #        environment.sexism_mat[perp+len_f][vict]+=1
                #if self.sexism_graph.has_edge(perp, vict):
                #    self.sexism_graph.edges[perp, vict]['weight'] +=1                
                #else:
                #    self.sexism_graph.add_weighted_edges_from([(perp, vict, 1)])

        return environment 

    # 9 #############    
    def anti_m_sexism(self, environment, perp_id):

        ''' Update environment & convo when anti_MALE sexism happens'''
        if self.verbose:
            print('anti male sexism')
        environment.convo_sexism.append(-1)
        environment.anti_m_sexism += 1 

        # 1 UPDATE VICTIM COSTS 
        self.cost_to_victims(self.males, environment)

        # 2 check for objections: victims, perpetuators, determines self.sexism_step_size
        self.check_for_objections( environment, self.males, self.females)

        # 3 UPDATE PERPETRATORS
        self.update_perpetrators(self.females, environment, perp_id)
        
        # 4 SAVE interaction in matrix/ later averaged across convos->graph
        len_f=len(environment.female_ind)

        vict_ind=[i for i,j in enumerate(environment.male_ind) if j in self.males]
        perp_ind=[i for i,j in enumerate(environment.female_ind) if j in self.females]

        #for perp in perp_ind:
        #    for vict in vict_ind:
        #        environment.sexism_mat[perp][vict+len_f]+=1
                
        return environment

    # 10 #############    
    def cost_to_victims(self, victims, environment):
        cost = 1
        for i in victims:            
            environment.agent_list[i].update_cost_received(cost)
        return environment 

    def cost_to_objector(self, objectors, environment, cost):
        for i in objectors:            
            environment.agent_list[i].update_cost_received(cost)
        return environment 

    # 11 #############    
    def update_perpetrators(self, perpetrators, environment, perp_id):
        
        # 1 update perpetrator 
        environment.agent_list[perp_id].update_cost_given()

        # 2 If there was an objection, perpetrator takes a cost
        if self.sexism_step_size<0:
            environment.agent_list[perp_id].update_cost_received(1)
        
        # 3 IF NO OBJECTION: increase sexism in all perpetrators present
        if self.sexism_step_size>0:
            for i in perpetrators:            
                environment.agent_list[i].update_sexism(self.sexism_step_size)

        return environment   

    # 12 #############
    def step(self, environment):
        # This is for updating wealth, subtracting costs
        # after every conversation everyone gets paid & subtraced: 
        # TODO FUTURE: NETWORK CENTRALITY DETERMIENES WEALTH
        if self.verbose:
                print('Updating environment & agents after round.')

        for i in range(len(environment.agent_list)):
            had_convo= i in self.convo_agents # true if had, false if not
            environment.agent_list[i].step(self.convo_id, had_convo)
            #XXX where does convo_id start? 0 or 1?
        return environment 