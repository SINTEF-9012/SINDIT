"""
Random SINDIT demo

author: Maryna Waszak <maryna.waszak@sintef.no>

"""
import dtwin.dtmachine as dtMachine
import dtwin.dtqueue as dtQueue
import dtwin.dtsensor as dtSensor
import dtwin.dttypes as dtTypes
import dtwin.dtpart as dtPart
import networkx as nx
from dtwin.dtfactory import dtFactory
import simpy
import configparser
import py2neo
import environment.environment as env
from enum import Enum, unique
from config import global_config as cfg

# Read Config
config = configparser.ConfigParser()
config.read(cfg.PATH_TO_CONFIG)
NEO4J_URI = env.NEO4J_FACTORY
NEO4J_USER = config['factory-neo4j']['user']
NEO4J_PASS = config['factory-neo4j']['pass']
NEED_AUTH = config['factory-neo4j']['need_auth']

PARTS_NEO4J_URI = env.NEO4J_PARTS
PARTS_NEO4J_USER = config['parts-neo4j']['user']
PARTS_NEO4J_PASS = config['parts-neo4j']['pass']
PARTS_NEED_AUTH = config['parts-neo4j']['need_auth']

# these groups a factory specific,
# they can be used for grouping machines, processes, and queues when visualizing
@unique
class dtGroups(Enum):
    NONE = 0
    RED_GROUP = 1 
    BLUE_GROUP = 2

class dtRandom(dtFactory):
    def __init__(self, graph=nx.DiGraph(), file_path="", env = simpy.Environment()):

        super().__init__(self, graph=graph, file_path=file_path, env=env)


        self.graph = graph
        self.machines = []
        self.queues = []
        self.sensors = []
        self.parts = []
        self.groups = [e.name for e in dtGroups]
        self.name = 'Random factory'       
        
        # serializing 
        if file_path != "":
            self.deserialize(serial_type="json", file_path_or_uri=file_path)
        else:
            self.create_factory_graph()
        
        # discrete event simulation
        self.env = env
        self.sim_hours = 40

            
    # define the machines, processes, sensors, and queues
    def create_factory_graph(self):

        #create sensors as objects:
        S1_1 = dtSensor.dtSensor('S1_1', 'temperature')
        S1_2 = dtSensor.dtSensor('S1_2', 'vibration')
        S2_1 = dtSensor.dtSensor('S2_1', 'temperature')
        S2_2 = dtSensor.dtSensor('S2_2', 'temperature')
        self.sensors = [S1_1, S1_2, S2_1, S2_2]

        # create machines as objects:
        dt_machines = []
        
        source_machine = dtMachine.dtMachine('S1', sensors=[], description='Goods producer', 
                                            type=dtTypes.dtTypes.SOURCE,
                                            num_parts_in = 0,num_parts_out = 0,
                                            amount_out = 0,amount_in = 0,
                                            position_on_dash=(-200,70))
        dt_machines.append(source_machine)
        exit_machine = dtMachine.dtMachine('E1', sensors=[], description='Product exit', 
                                            type=dtTypes.dtTypes.EXIT,
                                            num_parts_out = 0,num_parts_in = 0,
                                            amount_out = 0,amount_in = 0,
                                            position_on_dash=(-30,160))
        dt_machines.append(exit_machine)
        
        dt_machines.append(dtMachine.dtMachine('P1', sensors=[], description='Goods distribution', type=dtTypes.dtTypes.PROCESS,position_on_dash=(-140,70)))
        dt_machines.append(dtMachine.dtMachine('P2', sensors=[], description='Some great process', type=dtTypes.dtTypes.PROCESS,position_on_dash=(-30,70)))  
        dt_machines.append(dtMachine.dtMachine('M1', sensors=[S1_1, S1_2], description='Cool machine', type=dtTypes.dtTypes.MACHINE,position_on_dash=(-90,110)))
        dt_machines.append(dtMachine.dtMachine('M2', sensors=[S2_1, S2_2], description='Awesome machine', processing_time=3, type=dtTypes.dtTypes.MACHINE,position_on_dash=(-90,40)))
  
        self.machines = dt_machines
        
        # creating queues as objects:
        dt_queues = []
        source_queue = dtQueue.dtQueue(frm=self.get_machine_by_name('S1'), to=self.get_machine_by_name('P1'), capacity=300, name='Q1', description='Goods for distribution to manufacturing',position_on_dash=(-170,70))
        dt_queues.append(source_queue)
        dt_queues.append(dtQueue.dtQueue(frm=self.get_machine_by_name('P1'), to=self.get_machine_by_name('M1'), capacity=300, name='Q2', description='Parts to do stuff',position_on_dash=(-140,110)))   
        dt_queues.append(dtQueue.dtQueue(frm=self.get_machine_by_name('P1'), to=self.get_machine_by_name('M2'), capacity=300, name='Q3', description='Some more parts',position_on_dash=(-140,40)))
        dt_queues.append(dtQueue.dtQueue(frm=self.get_machine_by_name('M1'), to=self.get_machine_by_name('P2'), capacity=300, name='Q4', description='Great parts I',position_on_dash=(-90,70)))
        dt_queues.append(dtQueue.dtQueue(frm=self.get_machine_by_name('M2'), to=self.get_machine_by_name('P2'), capacity=300, name='Q5', description='Great parts II',position_on_dash=(-30,40)))
        exit_queue = dtQueue.dtQueue(frm=self.get_machine_by_name('P2'), to=self.get_machine_by_name('E1'), capacity=300, name='Q6', description='Goods for shipping',position_on_dash=(-30,110))     
        dt_queues.append(exit_queue)
        
        self.queues = dt_queues           
            
        # make a graph
        self.populate_networkx_graph()

        # setting up the parts inventory:
        NUM_OF_PARTS = 15
        init_parts = []
        if PARTS_NEED_AUTH.lower() == 'true':
            part_g = py2neo.Graph(PARTS_NEO4J_URI, 
                     user=PARTS_NEO4J_USER, 
                     password=PARTS_NEO4J_PASS)
        else:
            part_g = py2neo.Graph(PARTS_NEO4J_URI) 

        #start fresh
        part_g.delete_all()
        # we put some parts on the entry queues
        # find all queues with SOURCES and distribute parts on them more or less equally
        source_buffers = self.get_source_queues()
        blen=len(source_buffers)
        for idx in range(NUM_OF_PARTS):
            part = dtPart.dtPart('Pa'+str(idx), type=dtTypes.dtTypes.SINGLE_PART, py2neo_graph=part_g)
            part.createNeo4j()
            self.parts.append(part)
            sb = source_buffers[idx%blen]
            self.get_queue_by_name(sb.name).parts.append(part)                            

        ret_val = self.populate_networkx_graph()  
        return True
    
if __name__ == '__main__':


    random_fac = dtRandom() 
    #random_fac = dtFactory() 

    # store in neo4j
    random_fac.serialize(serial_type="neo4j", file_path_or_uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASS,need_auth=NEED_AUTH)
    #random_fac.deserialize(serial_type="neo4j", file_path_or_uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASS,need_auth=NEED_AUTH)

    # store as aasx file
    random_fac.serialize(serial_type="aasx", file_path_or_uri="random_factory.aasx")
    random_fac.serialize(serial_type="aas", file_path_or_uri="random_factory.aas")


    # Discrete event sumulation     
    random_fac.sim_hours = 20 
    sim_results = random_fac.run(use_kafka_and_neo4j = True, is_real_time = False)
    
    print(sim_results)

