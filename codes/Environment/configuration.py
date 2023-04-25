
#networks --->>>>

Network = {
# 'network' : "Networks\\network\\network.sumocfg",
'network' : "Networks\\4-way intersection\\4-way intersection.sumocfg",
# 'network' : 'Networks\\multi intersections\\cross intersection.sumocfg',
'number_cars_mean_std': {'loc':10 , 'scale':60},
'time' : 15001,
'period_of_generation_mean' : 50
    }


# vehicles --->>>>
Vehicle_characteristics = {
    'length' :4.7,
    'min_cap':1.3

}

# Drones -->>>>
Drones_chare = {
    'count': 5,
    'Ids': ['J6_drone','J7_drone', 'J8_drone', 'J2_drone', 'J5_drone'],
    'Positions': ['J6','J7', 'J8', 'J2', 'J5'],
    'radius': 200
}

RL_control = {
    'traffic_contorl': [('id','action'),('id2' , 'action2')]

}



 

