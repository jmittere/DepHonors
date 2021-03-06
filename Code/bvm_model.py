#bvm_model.py
import warnings
from mesa import Model
from mesa import agent
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import networkx as nx
import pandas as pd
import numpy as np
import scipy
import matplotlib.pyplot as plt
import matplotlib.colors as clr
from matplotlib.cm import get_cmap
import math
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score
from graspologic.cluster.autogmm import AutoGMMCluster
import ipdb

from model_functions import *
from cross_issue_agent import CrossIssueAgent
from same_issue_agent import SameIssueAgent


class bvmModel(Model):

    # l_steps: max # of simulation iterations 
    # n_agents: # of agents
    # p: prob of edge for Erdos-renyi
    # issues: # of issues for each agent
    # o: openness threshold for agents
    # d: disgust threshold for agents
    def __init__(self, l_steps, n_agents, p, issues, o, d, CI2=True, seed=None):
        super().__init__()
        self.l_steps = l_steps
        self.num_agents = n_agents
        self.num_issues = issues
        self.openness_threshold = o
        self.disgust_threshold = d
        self.schedule = RandomActivation(self)
        self.steps = 0
        self.repulsions = 0
        self.persuasions = 0
        self.influencesLastStep = 0
        self.equilibriumCounter= 0
        self.running = True
        self.clusterTracking = {} #key:(unique_id, issue) 
        self.buckets = {} #key: tuple of mean opinions for the bucket, value: list of agents in that bucket
        self.CI2 = CI2
        if(self.disgust_threshold<=self.openness_threshold):
            self.running=False
        self.autogmm = AutoGMMCluster(affinity='euclidean', 
                linkage='ward', covariance_type='full')

        # generate ER graph with n_agents nodes and prob of edge of p
        self.G = nx.erdos_renyi_graph(n_agents, p)
        while not nx.is_connected(self.G):
            self.G = nx.erdos_renyi_graph(n_agents, p)

        # instantiate and add agents
        for i in range(self.num_agents):
            #CI2 or just I2
            if(self.CI2):
                agent = CrossIssueAgent(i, self)
            else:
                agent = SameIssueAgent(i, self)

            self.G.nodes[i]["agent"] = agent
            self.schedule.add(agent)


        # create all the mesa "reporters" to gather stats 
        reporters = {"Buckets":updateBuckets, "Steps":getSteps, "assortativity":get_avg_assort, 
                "numClonePairs":getNumClonePairs, "numAnticlonePairs":getNumAnticlonePairs, "PercentPolarized":getPercentPolarized}
        
        #reporters = {} #uncomment this line if doing param sweep/suite
        self.datacollector = DataCollector(
                model_reporters=reporters,
                agent_reporters={}
                )

        #comment this out if doing param sweep/suite
        for numAgreements in range(1,self.num_issues):
            self.datacollector._new_model_reporter(
                    f"num{numAgreements}AgreementPairs",
                    globals()[f"getNumAgentPairsWith{numAgreements}Agreements"])
        self.datacollector.collect(self)

    def step(self):
        self.influencesLastStep = 0
        self.schedule.step()
        self.buckets = {} #TODO: fix buckets to persist through steps
        '''If this line is removed, the buckets do not get overwritten and there will be too many buckets due to the different bucket labels'''

        if self.influencesLastStep == 0:
            self.equilibriumCounter += 1
        else:
            # Reset equilibrium counter if there are persuasions or repulsions
            # still happening.
            self.equilibriumCounter = 0

        self.datacollector.collect(self)

        # Stop if exceeds step limit
        if self.l_steps == self.steps + 1:
            self.running = False

        # Stop if there have been no persuasions/replusion for longer than
        # threshold.
        if self.equilibriumCounter > EQUILIBRIUM_THRESHOLD:
            self.running = False

        self.steps += 1

    def printBucketInfo(self):
        print("Buckets: ", self.buckets)
        print("Number of buckets: ", len(self.buckets)) 
        for b,cnt in self.buckets.items():
            x = ()
            for i in b:
                num = round(i,2)
                x = x + (num,)
            print("{} agents in Bucket: {}".format(len(cnt), x))

if __name__ == "__main__":

    #lsteps, agents, p, issues, othresh, dthresh, CI2?
    test = bvmModel(1000, 100, 0.20, 3, 0.15, .55, True)

    for i in range(test.l_steps):
        test.step()
        if(test.running == False):
            break

    df = test.datacollector.get_model_vars_dataframe()
    df.to_csv("singleRun.csv")
    print(df)

    getPercentPolarized(test)
    
    test.printBucketInfo()
    
    plotAgreementCensus(test)
    
    plotPolarizationMeasures(test)
