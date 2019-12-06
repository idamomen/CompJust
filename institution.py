import random
import numpy as np
#import workerAgent
import workerAgentObjects
#import networkx as nx



class environment():
    def __init__(self, gender_ratio, *args): #, *n_agents, **kwargs
        """ Environment: n agents, n convos, distribution of sexism, rewards, etc """
        # each environment is initialized with a number of agents
        # e.g. 100 agents are the same for each 500 meetings
        # in each conversation 2-8 agents are randomly selected for interaction
        # their interactions depend on: 
        # 1 ratio and % sexism
        # 2 prob objection for self
        # 3 prob objection for other
        # future: initial social network that changes with time
        # FINAL: parameters below should be passed to class env. here for simplicity

        self.verbose=0
        
        ## MAIN PARAMS for initiating agents from scratch 
        ## APRIL 9, 2019: When the env inherits agents from the past, these params can change

        self.gender_ratio=gender_ratio
        self.n_agents=100

        # distribution of sexism probabilities
        self.prob_sexism = [0, 0, 0, 0, 0, .2, .4, .6, .8, 1]

        # prob objection on bealf of self or for agent of same gender
        # parameters from social psychology studiesnon women's responses to sexism
        self.prob_objection = [1, .66, .33, .33, 0, 0, 0, 0, 0, 0]
        #[1, .66, .33, .33, 1, 1, 0, 0, 0, 0] #5
        # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        #[1, .66, .33, .33, 0, 0, 0, 0, 0, 0]
        # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # 4:: NO OBJECTION
        #
        # [1, 1, 1, 1, 1, 1, 1, 1, 1, 1] #22
        # [1, .66, .33, .33, 1, .66, .33, .33, 0, 0] #2
        # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # 1111
        # [1, .66, .33, .33, 0, 0, 0, 0, 0, 0]

        # prob objection for other gender ==> based on men perceiving .57 of the times
        # we don't have direct data, so we set it based on women's findings
        # multiplied by .57
        # .57 * .41
        self.prob_ally      = [.66, .33, 0, 0, 0, 0, 0, 0, 0, 0]
        # [.66, .33, 1, 1, 0, 0, 0, 0, 0, 0] #5
        # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # 4:: NO OBJECTION
        # 
        #[0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # 4:: NO OBJECTION
        # [1, 1, 1, 1, 1, 1, 1, 1, 1, 1] # 3
        # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # 1111
        # [.66, .33, 1, 0, 0, 0, 0, 0, 0, 0] 111
        # [.66, .33, 1, .33, 0, 0, 0, 0, 0, 0] 11 EQUAL OBJECTION AS WOMEN
        # [.66, .33, 0, 0, 0, 0, 0, 0, 0, 0] ==> original is this. Changing it to test equality.
        # [0, 0, 0, 0, 0, .33, .33, .33, .66, 1]
        
        # mixed-gender meetings will be used later
        environment.mixedgendermeetings = 0


        self.convos_sofar=0 # used for convo ID
        self.total_sexism=0

        # start each env with a clean slate
        self.anti_f_sexism=0 
        self.anti_m_sexism=0
        self.agent_list=[]

        self.victims=[[]] # a matrix for victims. 
        self.perpetuators=[[]] 

        self.convo_sexism=[] # initialize where to save future convos for this env
        self.conv_no_sexism=0 # count how many convos with no sexism in all 500
        
        self.sexp_f=[]
        self.sexp_m=[]

        self.wealth_f=[]
        self.wealth_m=[]

        self.total_cost_f=[]
        self.total_cost_m=[]

        self.mixedgendermeetings=0

        if self.verbose:
            print("Initializing %s agents." % self.n_agents)
        
        # TODO from this mat: 
        # a directed graph of who's been sexist to whom
        # a directed graph of objections
        # self.sexism_graph=nx.DiGraph()
        #self.sexism_graph.out_degree(1, weight='weight')


        # how many women in 100 agents
        self.fem_count=int(self.gender_ratio*10)   #fem_count=int(.5*10)

        # set genders in gens
        gens= ["Male" for x in range(10)]
        for i in range(self.fem_count):
            gens[i]= "Female"
        
        id=0
        self.gen_ind=[]
        gen_prob_dist=[]
        obj_prob_dist=[]
        ally_prob_dist=[]

        nfem=int(self.n_agents*self.gender_ratio)
        nmen=self.n_agents-nfem

        nreps= [int(nmen/10) , int(nfem/10)] #
        genderx=['Male','Female']

        self.idx=0  
        
        for i, (g,nrep) in enumerate(zip(genderx,nreps)):
        #for i in range(0,2):
            #nrep=nreps[i]
            #g=genderx[i]

            # *args: This checks if the sexism_probabilities are passed to env
            # in a world where we want to pass sexism prob from another 
            # env to a new env, use this. Otherwise, don't!
            # args[0]: male_sexism_prob
            # args[1]: female_sexism_prob
            if len(args)>0:
                self.prob_sexism = args[i]
            
            # let's make some agents    
            self.make_agents_from_dist(nrep, g)    
        
        # get indices to male and female, e.g. self.female_ind
        self.get_gender_ind()

        # save prob dist of sexism & wealth for m / f
        # these methods are called before and after meetings for comparison
        
        self.getsexprob()

        self.getwealth()

    def make_agents_from_dist(self, nrep, g):            
        sex_prob_dist=self.prob_sexism*nrep
        obj_prob_dist=self.prob_objection*nrep
        ally_prob_dist=self.prob_ally*nrep

            
        # Here is where we create agents based on distributions
        for j in range(len(sex_prob_dist)):
            self.agent_list.append(workerAgentObjects.workerAgent(g, sex_prob_dist[j],obj_prob_dist[j], ally_prob_dist[j], self.idx))
            self.gen_ind.append(g)
            self.idx+=1   

    def getsexprob(self):
        # last version: just sexp, this version: added objp & allyp

        self.sexp_f=[self.agent_list[i].sexism for i in self.female_ind]
        self.objp_f=[self.agent_list[i].objp for i in self.female_ind]
        self.allyp_f=[self.agent_list[i].allyp for i in self.female_ind]

        self.sexp_m=[self.agent_list[i].sexism for i in self.male_ind]
        self.objp_m=[self.agent_list[i].objp for i in self.male_ind]
        self.allyp_m=[self.agent_list[i].allyp for i in self.male_ind]
    

    def getcostgiven(self):

        self.cost_given_f=[self.agent_list[i].cost_given for i in self.female_ind]
        self.cost_given_m=[self.agent_list[j].cost_given for j in self.male_ind]

    
    def gettotalcost(self):
        
        self.total_cost_f=[self.agent_list[i].total_cost for i in self.female_ind]
        self.total_cost_m=[self.agent_list[i].total_cost for i in self.male_ind]


    def get_gender_ind(self):
        # store gender indices for convos
        # ENUMERATE: IN THIS CASE i is INDEX, x is "female" or "male"
        # so it's correct to get i, as the index to female and male 
        self.female_ind=[i for i,x in enumerate(self.gen_ind) if x=="Female"]
        self.male_ind=[i for i,x in enumerate(self.gen_ind) if x=="Male"]

    def getwealth(self):
        # not used in current version realy

        self.wealth_f=[self.agent_list[i].wealth for i in self.female_ind]
        self.wealth_m=[self.agent_list[i].wealth for i in self.male_ind]
    

    def describe(self):

        # XXXX FUTURE: FULL DESCRIPTION
        print("Environment with %s agents loaded." % self.n_agents)
        print("Indices for female agents:")
        print(self.female_ind)
        print("Indices for male agents:")
        print(self.male_ind)

    