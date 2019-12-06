import random
import numpy as np

class workerAgent():
    """Each agent has a gender, wealth (Health), sexism received, objection made"""
    #wealth depends on the agent's position in network structure
    # sexism received and objection made subtract from wealth
    # future: they change the social network structure of the environment
    # work increases wealth

    def __init__(self, gender_mf, sexism, obj_prob, ally_prob,  *id):
        self.id=id
        self.gender=gender_mf #'male'
        self.color='white' # multidimensional agent array is for future
        self.wealth=1
        self.convno=0

        #self.cost_received=0 # mayeb redundant with next line
        self.trial_cost=[]
        self.cost_given=0
        self.total_cost=0
        self.sexism=sexism
        self.objp=obj_prob
        self.allyp=ally_prob
        self.verbose=0

    def describe(self):
        desc_str = "#%s: agent, %s : allyp = %s, sexism = %s." % (self.id,
                 self.gender, self.allyp, self.sexism)
        return desc_str

    def update_cost_received(self, cost):
        # April 9, 2019: added cost here, previously it was always 1
        # but now cost is lower for men who object
        # future: cost for receiving sexist comment is also lower for men
        
        self.trial_cost.append(-1)
        self.total_cost+=cost #1

    def update_cost_given(self):
        self.cost_given += 1
        self.trial_cost.append(0)
        # conversation functions of an agent


    def update_sexism(self, step_size):

        # OLD version: increase_or as input can be .01 or -.01
        
        # NEW version: 10% of the initial sexism
        if self.sexism==0:
            increase_or = .005*step_size
        else:    
            increase_or = self.sexism*step_size

        # when decrease due to objection:
        #   it's  .1  * self.sexism  when NO ONE objects 
        #   it's -.1  * self.sexism  when same gender objects
        #   or   -.05 * self.sexism  when other gender objects

        #print('agent {0} : sexism {1}'.format(self.id, self.sexism))
        if self.sexism<1:
            self.sexism=self.sexism+increase_or
            #if increase_or<0:        # if we wanted to add a cost to being objected to         
                #self.total_cost+=1
            if self.verbose:
                print('added sexism for {0} -> {1}'.format(self.id, self.sexism))
        
        # this line ensures increments don't go above 1
        if self.sexism>1:
            self.sexism=1

        if self.sexism<0:
            self.sexism=0        


    def step(self, *had_convo):
        self.wealth+=1
        if had_convo and len(self.trial_cost)==self.convno+1:
            #conversation determines wealth gained in that day's work
            self.wealth-=self.trial_cost[self.convno]
        else:
            self.trial_cost.append(0)

        # increase convo count    
        self.convno+=1    
        if self.verbose:
            print("All agents step to next round.")