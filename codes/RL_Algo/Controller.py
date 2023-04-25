# from plistlib import UID
from codes.Environment.traffic_lights_controler import traffic_lights_controler
from codes.Environment.configuration import Vehicle_characteristics,Network
from codes.Environment.traffic_light_signal import traffic_light
from codes.RL_Algo.Agent import Agent
from codes.RL_Algo.Q_Learning import Qlearning
import matplotlib.pyplot as plt # type: ignore
from traci import vehicle as v
from numpy import concatenate
from traci import lane as l
from statistics import mean
import statistics
import numpy as np
from numpy import random # type: ignore 
from uuid import uuid4
import traci
import os




class Controller():
    def __init__(self,intersection,time,number_cars_mean_std,period_of_generation_mean,is_random_routes,max_len_queue=1000):
        self.period_of_generation_mean = period_of_generation_mean
        self.number_cars_mean_std = number_cars_mean_std
        self.is_random_routes = is_random_routes
        self.number_of_agent = len(intersection)
        self.Agent_ids = intersection
        self.Agents = []
        self.averag_queue_length = []
        self.average_waiting_time = []
        self.std_waiting_time = []
        self.time = time
        self.num_of_vehicle = 200
    
    def get_all_edges(self):
        """
        It returns a list of all the edges in the network
        :return: A list of all the edges in the network.
        """
        opjects,all_edges = traci.edge.getIDList(),[]
        for obj in opjects:
            if 'E' in(obj):
                all_edges.append(obj)
        return all_edges
    
    def get_edges_ignored(self):
        """
        It takes all the edges in the network and compares them to the edges controlled by the traffic
        lights. 
        
        The edges controlled by the traffic lights are the ones that are returned. 
        
        The edges that are not controlled by the traffic lights are ignored. 
        
        The edges that are ignored are the ones that are returned. 
        
        The edges that are controlled by the traffic lights are ignored. 
        
        The edges that are ignored are the ones that are returned. 
        
        The edges that are controlled by the traffic lights are ignored. 
        
        The edges that are ignored are the ones that are returned. 
        
        The edges that are controlled by the traffic lights are ignored. 
        
        The edges that are ignored are the ones that are returned. 
        
        The edges that are controlled by the traffic lights are ignored. 
        
        The edges that are ignored are the ones that are returned. 
        
        The edges that are controlled by
        :return: Edges_controlled is a list of edges that are controlled by the traffic light.
        Edges_non_controlled is a list of edges that are not controlled by the traffic light.
        """
        all_edges = self.get_all_edges()
        lanes_controlled = []
        for id_tl in self.Agent_ids:lanes_controlled.extend(traci.trafficlight.getControlledLanes(id_tl)) # type: ignore
        Edges_controlled = []
        Edges_non_controlled = []
        for Ei in all_edges:
            for Li in lanes_controlled:
                if Ei in Li:
                    if Ei == 'E18' or Ei == 'E22': pass
                    else:Edges_controlled.append(Ei)
                # else:Edges_non_controlled.append(Ei)
        set1 = set(all_edges)
        set2 = set(Edges_controlled)
        non_controlled = set1.difference(set2).union(set2.difference(set1))

        Edges_controlled = list(set(Edges_controlled))
        # Edges_non_controlled = list(set(Edges_non_controlled))
        Edges_non_controlled = list(non_controlled)
        return Edges_controlled , Edges_non_controlled
    
    
    def generate_vehicles_(self,number_vehicles,all_edges,step):
        """
        It generates vehicles with random routes and adds them to the simulation
        
        :param number_vehicles: number of vehicles to be generated
        :param all_edges: list of all edges in the network
        :param step: the current step of the simulation
        """
        for i in range(number_vehicles):
            routes = traci.route.getIDList()
            if (self.is_random_routes):
                v.add(vehID = 'Veh'+str(step)+str(i), routeID = random.choice(routes))
            else:
                edge1,edge2,uid = random.choice(all_edges),random.choice(all_edges),str(uuid4())
                traci.route.add(routeID= uid , edges= [edge1,edge2] )
                v.add(vehID = 'Veh'+uid, routeID = uid)
            v.setLength('Veh'+uid , Vehicle_characteristics['length'])  # type: ignore
            v.setMinGap('Veh'+uid , Vehicle_characteristics['min_cap'])  # type: ignore

    def generate_vehicles(self,number_vehicles,edge_non_contlled,Edges_controlled):
        """
        It generates a random route for each vehicle and adds it to the simulation
        
        :param number_vehicles: number of vehicles to be generated
        :param all_edges: list of all edges in the network
        """
        for i in range(number_vehicles):     
            routes = traci.route.getIDList()
            edge1 = random.choice(Edges_controlled)
            edge2 = random.choice(edge_non_contlled)
            
            uid = str(uuid4())
            traci.route.add(routeID= uid , edges= [edge1,edge2] )
            
            traci.vehicle.add(vehID = 'Veh'+uid, routeID = uid)
            traci.vehicle.setLength('Veh'+uid , Vehicle_characteristics['length'])
            traci.vehicle.setMinGap('Veh'+uid , Vehicle_characteristics['min_cap'])

    def set_vehicle_info(self,step,all_edges,period_of_generation,is_generate,edge_non_contlled,Edges_controlled):
        """
        > The function generates a number of vehicles according to a normal distribution with mean and
        standard deviation specified in the `number_cars_mean_std` dictionary. The number of vehicles is
        generated every `period_of_generation_mean` seconds
        
        :param step: the current step of the simulation
        :param all_edges: a list of all the edges in the network
        :param period_of_generation: This is the period of time between the generation of vehicles
        :param is_generate: a boolean that tells us whether we should generate vehicles or not
        :return: period_of_generation,is_generate
        """
        if period_of_generation == 0:
            is_generate,period_of_generation = True,int(random.exponential(scale = self.period_of_generation_mean))
        period_of_generation-=1 if period_of_generation>0 else 0
        if is_generate:
            is_generate = False 
            number_vehicles = int(random.normal(loc=self.number_cars_mean_std['loc'] , scale= self.number_cars_mean_std['scale']))
            self.generate_vehicles(number_vehicles,edge_non_contlled,Edges_controlled)
        return period_of_generation,is_generate

    def creator(self):
        """
        It creates a list of agents, each with a unique ID, and appends them to the Agents list.
        """
        for i in range(self.number_of_agent):
            self.Agents.append(Qlearning(self.Agent_ids[i]))
        
    def save_strat_state(self):
        """
        The function saves the current simulation state to a file called 'start_state.xml' in the same
        directory as the network file
        """
        path_start_state =  Network['network']
        path_0 = path_start_state.split('.')[0]
        path_start_state = path_0+'_start_state.xml'
        traci.simulation.saveState(path_start_state)

    def load_strat_state(self):
        """
        It loads a saved simulation state
        """
        ###  get path of 'start state' #### 
        path_start_state =  Network['network']
        path_0 = path_start_state.split('.')[0]
        path_start_state = path_0+'_start_state.xml'
        # load a saved simulation state
        traci.simulation.loadState(path_start_state)

    def check_vehicles_to_remove(self, edges):
        """
        It removes all vehicles from the given edges
        
        :param edges: list of edges to remove vehicles from
        """
        for id_Edge in edges:
            vehicle_ids = traci.edge.getLastStepVehicleIDs(id_Edge)
            for id_vehicle in vehicle_ids:
                traci.vehicle.remove(id_vehicle)
    
    def rest_sumo(self):
        """
        The function is called by the main function, and it calls the plot_reward function of each agent

        :param number_of_senareo: number of episodes
        """
        self.load_strat_state()
    
    def maping_btween_agents_intersections(self):
        """
        It creates a traffic light object for each agent, and then creates a traffic lights controller
        object
        :return: a tuple of three objects.
        """
        t_obejct,Actions = [],{}
        for id in self.Agent_ids:
            t_obejct.append(traffic_light(id))
            Actions[id] = (0,1)
        tls_controler = traffic_lights_controler(t_obejct)
        return t_obejct,Actions,tls_controler
    
    def apply_action(self,with_agents,tls_controler,t_obejct,actions): # note for taher
        """
        It takes in a list of agents, a traffic light controller, a list of traffic light objects, and a
        dictionary of actions. 
        
        If the with_agents flag is set to true, it sends the actions to the traffic light controller. 
        
        If the with_agents flag is set to false, it randomly generates actions for each agent and sends
        them to the traffic light controller. 
        
        Then, it checks the commands to execute for each agent.
        
        :param with_agents: whether to use the agent or not
        :param tls_controler: the traffic light controller
        :param t_obejct: a list of traci objects
        :param actions: a dictionary of actions for each agent
        """
        if with_agents:
            tls_controler.send_Actions(actions)
        else:
            actions=[]
            for i,_ in enumerate(self.Agent_ids):
                actions.append(random.choice([0, 1, 2, 3]))
            tls_controler.send_Actions(actions)
        for i,_ in enumerate(self.Agent_ids):
            t_obejct[i].check_cmds_to_execute()
    
    def functionality_agents(self,state):
        return list(map(lambda agent: agent.fit(state), self.Agents))            
    
    def run_agents(self,Random,with_agents):
        self.creator()
        state,step_generation,step,period_of_generation,is_generate = state=random.choice([0,1,2,3]),0,0,0,False
        t_obejct,Actions,tls_controler = self.maping_btween_agents_intersections()
        Edges_controlled,edge_non_contlled = self.get_edges_ignored()
        while step < self.time:
            self.check_vehicles_to_remove(edge_non_contlled)
            traci.simulationStep()
            if step == 0:self.save_strat_state()
            if step_generation == 0:self.generate_vehicles(self.num_of_vehicle+self.num_of_vehicle//3,edge_non_contlled,Edges_controlled)  
            if step % 30 == 0:
                vehicles = v.getIDList()
                if with_agents:
                    Actions = self.functionality_agents(state)
                    self.apply_action(with_agents,tls_controler,t_obejct,Actions)
                elif Random:
                    self.apply_action(with_agents,tls_controler,t_obejct,Actions)
                
                if step % 3000 != 0 and step!=0 :
                    for agent in self.Agents:
                        self.averag_queue_length.append(agent.reward_calculater.infromation.avg_queue_length())
                        self.average_waiting_time.append(agent.reward_calculater.infromation.get_average_waiting_time_overall(vehicles))
                        self.std_waiting_time.append(agent.reward_calculater.infromation.get_std_waiting_time_overall(vehicles))

            if step_generation> 30 and len(v.getIDList())<self.num_of_vehicle:
                number_cars = self.num_of_vehicle - len(v.getIDList())
                self.generate_vehicles(number_cars,edge_non_contlled,Edges_controlled) 
            step_generation +=1
            if step % 3000 == 0 and step != 0:
                state = state=random.choice([0,1,2,3])
                self.rest_sumo()
                step_generation = 0 
            step += 1
        self.polt_all_results(Random,with_agents)

    def polt_all_results(self,Random,with_agents):
        """
        It plots the results of the simulation
        
        :param Random: If True, the agents will be randomly placed in the environment. If False, the
        agents will be placed in a grid
        :param with_agents: If True, the plot will show the agents' positions
        :param with_predicted_position: If True, the agent will use the predicted position of the other
        agents to make its decision. If False, the agent will use the actual position of the other
        agents to make its decision
        :param without_restart: If you want to plot the results of the simulation without restarting the
        simulation, set this parameter to True
        """
        for i in range(self.number_of_agent,):
            self.Agents[i].plot_reward(with_agents,Random)
        
        self.plot_result(self.averag_queue_length,"Averag_Queue_Length",Random,with_agents) 
        self.plot_result(self.average_waiting_time,"Average_Waiting_Time",Random,with_agents)
        self.plot_result(self.std_waiting_time,"STD_Waiting_Time",Random,with_agents)
        

    
    def plot_result(self,List_of_value,title,Random,with_agents,step=5):
        """
        It takes a list of values, a title, a boolean for whether or not the results are random, a
        boolean for whether or not the results are with agents, a boolean for whether or not the results
        are with predicted positions, a boolean for whether or not the results are without restart, and
        a step value. 
        
        It then plots the list of values, with the title, and saves the plot to a file. 
        
        The file is saved to a folder called "results" in the current directory, and the folder name is
        determined by the booleans. 
        
        The step value is used to determine how many values to plot. 
        
        The function also plots vertical lines at every 100th step. 
        
        The function also prints the path to the file that it saves the plot to. 
        
        The function also has a commented out line that shows the plot.
        
        :param List_of_value: the list of values you want to plot
        :param title: The title of the graph
        :param Random: If True, the agents will be randomly placed on the grid. If False, the agents
        will be placed in a circle
        :param with_agents: whether or not to use the agents
        :param with_predicted_position: If True, the agents will use the predicted position of the other
        agents to make their decisions. If False, they will use the actual position of the other agents
        :param without_restart: if True, the agent will not restart when it reaches the goal
        :param step: the number of steps between each point plotted, defaults to 5 (optional)
        """
        plt.figure(figsize=(6, 4))
        plt.title(title)
        plt.plot([i for i, x in enumerate(List_of_value) if i%step==0],
                 [x for i, x in enumerate(List_of_value) if i%step==0], color='g')
        n = len(List_of_value)
        plt.vlines(x=[i for i in range(n) if i%100==0], ymin=[min(List_of_value) for i in range(n) if i%100==0], ymax=[max(List_of_value) for i in range(n) if i%100==0], colors=['r' for i in range(n) if i%100==0], ls='--', lw=2)
        
        plt.xlabel('Steps')
        plt.ylabel(title)
        folder_name = ""
        if with_agents:folder_name = "Results_with_predicted_position"
        elif not with_agents:folder_name = "Results_without_agents"
        if Random:folder_name = "Results_Random"
        print(os.path.join(os.path.join(os.path.join(os.path.abspath("."),'resultes'),folder_name),folder_name+"_"+title+".png"))
        plt.savefig(os.path.join(os.path.join(os.path.join(os.path.abspath("."),'resultes'),folder_name),title+".png"))
        # plt.show()
        
        

    