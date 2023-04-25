from codes.InformationProvider.Single_agent_information import Infromation
from math import exp,log

class SingleAgentReward:

    def __init__(self,id):
        self.id=id
        self.infromation = Infromation(self.id)
    def reward(self):
        T = exp(self.infromation.throughput())
        t1 = self.infromation.adaptive_weighting_factory()*self.infromation.standard_deviation_queue_length() # type: ignore
        t2 = (1-self.infromation.adaptive_weighting_factory())*T
        f = t1+t2
        return log(f,0.5)
