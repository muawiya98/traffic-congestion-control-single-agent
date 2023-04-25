from codes.Environment.configuration import Vehicle_characteristics
from traci import trafficlight as t
from traci import vehicle as v
from traci import lane as l
from statistics import mean,stdev
import statistics 
import sumolib
import time

class Infromation:
    def __init__(self,id):
        self.id=id
        self.lanes = t.getControlledLanes(self.id)
        self.dic_lane2number,self.dic_number2lane = self.lanes_as_dic(self.lanes)

        
    def lanes_as_dic(self,lanes):
        test_values = [i for i in range(len(lanes))]
        dic_lane2number = {lanes[i]: test_values[i] for i in range(len(lanes))}
        dic_number2lane = {test_values[i]: lanes[i] for i in range(len(lanes))}
        return dic_lane2number,dic_number2lane

    
    def queue_length(self):
        """
        queuq length refers to the number of vehicles waiting on one side of the road 
        """
        AQL = []
        for lane_id in self.lanes:
            count_veh = l.getLastStepHaltingNumber(lane_id)
            length_lane = l.getLength(lane_id)
            AQL.append(count_veh*7.5 / length_lane)
        return AQL
    
    def number_of_vehicle(self,lane_id):
        return l.getLastStepHaltingNumber(lane_id)
    
    def avg_queue_length(self):
        return mean(self.queue_length())
    
    def standard_deviation_queue_length(self):
        return stdev(self.queue_length())
    
    def throughput(self):
        return 20
    
    def adaptive_weighting_factory(self): # depends on the arrival of vehicles per hour.
        return 0.5
    
    def get_current_time(self):
        """
        This function returns the current time in seconds.
        :return: The current time in seconds.
        """
        start_time = time.time()
        return start_time
    
    def get_number_of_places_available_in_lane(self,lane_id):
        """
        This function calculates the number of available places in a lane based on the mean length of
        vehicles and the number of halted vehicles.
        
        :param lane_id: The ID of the lane for which we want to get the number of available places
        :return: the number of places available in a lane, which is calculated based on the length of
        the lane, the mean length of vehicles in the lane, and the number of halted vehicles in the
        lane.
        """
        mean_length_veh = l.getLastStepLength(lane_id)
        count_veh = l.getLastStepHaltingNumber(lane_id)
        return (l.getLength(lane_id)-(count_veh*(mean_length_veh+Vehicle_characteristics['min_cap'])))//(mean_length_veh+Vehicle_characteristics['min_cap'])
    
    def get_list_of_waiting_vehicles(self,vehicles): # call in Single_agent_information
        """
        It takes a list of vehicles and returns a list of waiting times for each vehicle in the list
        
        :param vehicles: list of vehicles
        :return: The waiting time of the vehicles in the list.
        """
        # apply a function to all values in the list using map and lambda
        waiting_time_vehicles = list(map(lambda veh: v.getWaitingTime(veh), vehicles))
        return waiting_time_vehicles
    
    def get_average_waiting_time(self,vehicles): # call in Single_agent_information
        """
        It returns the average waiting time of all vehicles in the simulation
        
        :param vehicles: list of vehicles
        :return: The average waiting time of all vehicles in the simulation.
        """
        if len(vehicles)>0:
            waiting_time_vehicles = self.get_list_of_waiting_vehicles(vehicles)
            average = sum(waiting_time_vehicles) / len(waiting_time_vehicles)
            return average
        else:
            return -1
        
    def get_std_waiting_time(self,vehicles): # call in Single_agent_information
        """
        It takes a list of vehicles and returns the standard deviation of the waiting time of all
        vehicles in the list
        
        :param vehicles: list of vehicles
        :return: The standard deviation of the waiting time of all vehicles in the simulation.
        """
        if len(vehicles)>0:
            waiting_time_vehicles = self.get_list_of_waiting_vehicles(vehicles)
            std_dev = statistics.stdev(waiting_time_vehicles)
            return std_dev
        else:
            return -99999

    

    # self.State_transition_table={
    # 0:{0:[2, 3, 4, 5, 6, 7],1:[0],2:[1, 2, 3, 5, 6,7]},
    # 1:{0:[2, 3, 4, 5, 6, 7],1:[0, 2, 3, 4, 6, 7],2:[1]},
    
    # 2:{0:[0, 1, 4, 5, 6, 7],1:[2],2:[0, 1, 3, 4, 5, 7]},
    # 3:{0:[0, 1, 4, 5, 6, 7],1:[0, 1, 2, 4, 5, 6],2:[3]},
    
    # 4:{0:[0, 1, 2, 3, 6, 7],1:[4],2:[1, 2, 3, 5, 6, 7]},
    # 5:{0:[0, 1, 2, 3, 6, 7],1:[0, 2, 3, 4, 6, 7],2:[5]},
    
    # 6:{0:[0, 1, 2, 3, 4, 5],1:[6],2:[0, 1, 3, 4, 5, 7]},
    # 7:{0:[0, 1, 2, 3, 4, 5],1:[0, 1, 2, 4, 5, 6],2:[7]}}