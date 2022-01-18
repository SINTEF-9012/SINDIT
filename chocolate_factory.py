"""
SINDIT demo: Chocolate factory

author: Maryna Waszak <maryna.waszak@sintef.no>

"""
import dtwin.flux as flux
import dtwin.dtmachine as dtMachine
import dtwin.dtqueue as dtQueue
import dtwin.dtsensor as dtSensor
import dtwin.dttypes as dtTypes
import dtwin.dtpart as dtPart
import json
import networkx as nx
import datetime
import dateutil.parser
from dtwin.dtfactory import dtFactory
import simpy
import configparser
import py2neo
import environment.settings as stngs
from enum import Enum, unique

# Read Config
config = configparser.ConfigParser()
config.read(stngs.BASE_DIR+'/sindit.cfg')
NEO4J_URI = stngs.NEO4J_FACTORY
NEO4J_USER = config['factory-neo4j']['user']
NEO4J_PASS = config['factory-neo4j']['pass']
NEED_AUTH = config['factory-neo4j']['need_auth']

PARTS_NEO4J_URI = stngs.NEO4J_PARTS
PARTS_NEO4J_USER = config['parts-neo4j']['user']
PARTS_NEO4J_PASS = config['parts-neo4j']['pass']
PARTS_NEED_AUTH = config['parts-neo4j']['need_auth']

# these groups a factory specific,
# they can be used for grouping machines, processes, and queues when visualizing
@unique
class dtGroups(Enum):
    NONE = 0
    CONTAINER_GROUP = 1 
    BUFFER_GROUP = 2

class dtChocFac(dtFactory):
    def __init__(self, graph=nx.DiGraph(), file_path="", env = simpy.Environment()):
        self.graph = graph
        self.machines = []
        self.queues = []
        self.sensors = []
        self.parts = []
        self.groups = [e.name for e in dtGroups]
        self.name = 'SINTEF chocolate factory'       
        
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
        S1_2 = dtSensor.dtSensor('S1_2', 'temperature')
        S2_1 = dtSensor.dtSensor('S2_1', 'temperature')
        S3_1 = dtSensor.dtSensor('S3_1', 'temperature')
        S4_1 = dtSensor.dtSensor('S4_1', 'temperature')
        S5_1 = dtSensor.dtSensor('S5_1', 'vibration')
        self.sensors = [S1_1, S1_2, S2_1, S3_1, S4_1, S5_1]

        # create machines as objects:
        dt_machines = []
        
        dt_machines.append(dtMachine.dtMachine('S1', sensors=[], description='Cocoa butter', type=dtTypes.dtTypes.SOURCE,num_parts_in = 0,num_parts_out = 0,amount_out = 0,amount_in = 0,position_on_dash=(-305,35)))
        dt_machines.append(dtMachine.dtMachine('S2', sensors=[], description='Sugar', type=dtTypes.dtTypes.SOURCE,num_parts_in = 0,num_parts_out = 0,amount_out = 0,amount_in = 0,position_on_dash=(-305,100)))
        dt_machines.append(dtMachine.dtMachine('S3', sensors=[], description='Packaging', type=dtTypes.dtTypes.SOURCE,num_parts_in = 0,num_parts_out = 0,amount_out = 0,amount_in = 0,position_on_dash=(80,10)))    
        dt_machines.append(dtMachine.dtMachine('E1', sensors=[], description='Product exit', type=dtTypes.dtTypes.EXIT,num_parts_out = 0,num_parts_in = 0,amount_out = 0,amount_in = 0,position_on_dash=(80,143)))
        
        dt_machines.append(dtMachine.dtMachine('M1_1', sensors=[S1_1], description='Cocoa butter melting', processing_time=2, num_parts_out=0, num_parts_in=0, position_on_dash=(-230,35)))
        dt_machines.append(dtMachine.dtMachine('M1_2', sensors=[S1_2], description='Sugar grinding', processing_time=3, num_parts_out=0, num_parts_in=0, position_on_dash=(-230,100)))  
        dt_machines.append(dtMachine.dtMachine('M2', sensors=[S2_1], description='Conching', processing_time=2, num_parts_out=0, num_parts_in=0,position_on_dash=(-145,70)))
        dt_machines.append(dtMachine.dtMachine('M3', sensors=[S3_1], description='Chocolate paste tempering', processing_time=3, num_parts_out=0, num_parts_in=0, position_on_dash=(-73,70)))
        dt_machines.append(dtMachine.dtMachine('M4', sensors=[S4_1], description='Shell moulding', processing_time=10, amount_in = 1, num_parts_out=10, num_parts_in=0, amount_out = 0, position_on_dash=(5,70)))
        dt_machines.append(dtMachine.dtMachine('M5', sensors=[S5_1], description='Packaging', processing_time=1, num_parts_in=1, num_parts_out=1, amount_out = 0, position_on_dash=(82,70)))
  
        self.machines = dt_machines
        
        # creating queues as objects:
        dt_queues = []
        dt_queues.append(dtQueue.dtQueue(frm=self.get_machine_by_name('S1'), to=self.get_machine_by_name('M1_1'), capacity=300, amount = 100, name='Q2', qtype = dtTypes.dtTypes.CONTAINER, description='Raw cocoa butter',position_on_dash=(-305,35)))
        dt_queues.append(dtQueue.dtQueue(frm=self.get_machine_by_name('S2'), to=self.get_machine_by_name('M1_2'), capacity=300, amount = 100, name='Q1', qtype = dtTypes.dtTypes.CONTAINER, description='Raw sugar',position_on_dash=(-305,100)))   
        dt_queues.append(dtQueue.dtQueue(frm=self.get_machine_by_name('M1_1'), to=self.get_machine_by_name('M2'), capacity=300, name='Q3', qtype = dtTypes.dtTypes.CONTAINER, description='Melted cocoa butter',position_on_dash=(-184,35)))
        dt_queues.append(dtQueue.dtQueue(frm=self.get_machine_by_name('M1_2'), to=self.get_machine_by_name('M2'), capacity=300, name='Q4', qtype = dtTypes.dtTypes.CONTAINER, description='Grinded sugar',position_on_dash=(-184,100)))
        dt_queues.append(dtQueue.dtQueue(frm=self.get_machine_by_name('M2'), to=self.get_machine_by_name('M3'), capacity=300, name='Q5', qtype = dtTypes.dtTypes.CONTAINER, description='Conched chocolate paste',position_on_dash=(-109,70)))
        dt_queues.append(dtQueue.dtQueue(frm=self.get_machine_by_name('M3'), to=self.get_machine_by_name('M4'), capacity=300, name='Q6', qtype = dtTypes.dtTypes.CONTAINER, description='Tempered chocolate paste',position_on_dash=(-35,70)))     
        dt_queues.append(dtQueue.dtQueue(frm=self.get_machine_by_name('M4'), to=self.get_machine_by_name('M5'), capacity=300, name='Q7', description='Moulded chocolate bars',position_on_dash=(42,70)))
        dt_queues.append(dtQueue.dtQueue(frm=self.get_machine_by_name('S3'), to=self.get_machine_by_name('M5'), capacity=300, amount = 100, name='Q8', qtype = dtTypes.dtTypes.CONTAINER, description='Packaging material',position_on_dash=(80,40))) 
        dt_queues.append(dtQueue.dtQueue(frm=self.get_machine_by_name('M5'), to=self.get_machine_by_name('E1'), capacity=300, name='Q9', description='Packaged chocolate bars',position_on_dash=(80,105)))
        self.queues = dt_queues           
            
        # make a graph
        self.populate_networkx_graph()

        # setting up the parts inventory:
        NUM_OF_PARTS = 0
        init_parts = []
        if PARTS_NEED_AUTH.lower() == 'true':
            part_g = py2neo.Graph(PARTS_NEO4J_URI, 
                     user=PARTS_NEO4J_USER, 
                     password=PARTS_NEO4J_PASS)
        else:
            part_g = py2neo.Graph(PARTS_NEO4J_URI) 

        #start fresh
        part_g.delete_all()

        # set the parts graph db as we have a buffer there
        self.get_machine_by_name('M4').py2neo_graph = part_g
        self.get_machine_by_name('M5').py2neo_graph = part_g
                                   

        ret_val = self.populate_networkx_graph()  
        return True

def run_factory(sim_time:int, num_entry_amount:int):
    fac = dtFactory()  
    fac.deserialize(serial_type="neo4j", 
                    file_path_or_uri=NEO4J_URI,
                    user=NEO4J_USER,
                    password=NEO4J_PASS,
                    need_auth=NEED_AUTH)
    
    fac.sim_hours = sim_time 

    # setting up the inventory:
    if PARTS_NEED_AUTH.lower() == 'true':
        part_g = py2neo.Graph(PARTS_NEO4J_URI, 
                     user=PARTS_NEO4J_USER, 
                     password=PARTS_NEO4J_PASS)
    else:
        part_g = py2neo.Graph(PARTS_NEO4J_URI)
    
    # set reference to graph since this gets lost
    for part in fac.parts:
        part.py2neo_graph = part_g
        # make sure part is there
        part.createNeo4j()
    
    for machine in fac.machines:
        machine.py2neo_graph = part_g
    
    # we put some more parts on the entry queue
    # find all queues with SOURCES and distribute parts on them more or less equally
    source_queues = fac.get_source_queues()
    source_buffers = list(filter(lambda x: x.type == dtTypes.dtTypes.BUFFER, source_queues))
    source_containers = list(filter(lambda x: x.type == dtTypes.dtTypes.CONTAINER, source_queues))

    blen=len(source_buffers)
    if blen > 0:
        num_entry_parts = num_entry_amount
        num_of_existing_parts = len(fac.parts)    
        for idx in range(num_entry_parts):
            part = dtPart.dtPart('Pa'+str(idx+num_of_existing_parts), type=dtTypes.dtTypes.SINGLE_PART, py2neo_graph=part_g)
            part.createNeo4j()
            fac.parts.append(part)
            sb=source_buffers[idx%blen]
            fac.get_queue_by_name(sb.name).parts.append(part)                                      

    for q in source_containers:
        q.amount += num_entry_amount

    # after we add ingredfients on queue let's write this back to neo4j
    fac.serialize(serial_type="neo4j", file_path_or_uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASS,need_auth=NEED_AUTH)

    # Discrete event sumulation     
    sim_results = fac.run()
       
    return sim_results    
if __name__ == '__main__':


    choc_fac = dtChocFac()  

    # store in neo4j
    choc_fac.serialize(serial_type="neo4j", file_path_or_uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASS,need_auth=NEED_AUTH)

    # store as json file
    choc_fac.serialize(serial_type="json", file_path_or_uri="chocolate_factory.json")

    # Discrete event sumulation     
    #run_factory(sim_time=40, num_entry_amount=0)

    #fac = dtFactory()  
    #fac.deserialize(serial_type="neo4j", file_path_or_uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASS,need_auth=NEED_AUTH)
    #cytograph = fac.cytoscape_json_data() 

