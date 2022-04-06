"""
Random SINDIT demo

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
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from colormap import rgb2hex
from scipy.stats import norm

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
    RED_GROUP = 1 
    BLUE_GROUP = 2

class dtGilje(dtFactory):
    def __init__(self, graph=nx.DiGraph(), file_path="", env = simpy.Environment()):

        super().__init__(self, graph=graph, file_path=file_path, env=env)


        self.graph = graph
        self.machines = []
        self.queues = []
        self.sensors = []
        self.parts = []
        self.groups = [e.name for e in dtGroups]
        self.name = 'Gilje windows factory'       
        
        # serializing 
        if file_path != "":
            self.deserialize(serial_type="json", file_path_or_uri=file_path)
        else:
            a=0
            self.create_factory_graph()
        
        # discrete event simulation
        self.env = env
        self.sim_hours = 40

    def create_interesting_plots(self):
        # read RFID sample and derive the product flow structure
        rfid_data = pd.read_csv(stngs.DATA_DIR+'G20821.csv',delimiter=";")  
        rfid_data['Tidspunkt lest']= pd.to_datetime(rfid_data['Tidspunkt lest'], format='%d.%m.%Y %H:%M:%S') #11.02.2022 07:35:21       
    
        reader_dict_names = dict(zip(rfid_data['Lesepkt id'], rfid_data['Lesepkt navn']))
        reader_dict_sequence= dict(zip(rfid_data['Lesepkt id'], rfid_data['Lesepkt rekkefølge']))
        sequence_unique_ids = rfid_data['Lesepkt rekkefølge'].unique()
        sequence_ids = {} 
        parts_time_dict = {}
        machine_time_dict = {}
        for index, row in rfid_data.iterrows():
            if row['Lesepkt rekkefølge'] not in sequence_ids.keys():
               sequence_ids[row['Lesepkt rekkefølge']] = [] 
            sequence_ids[row['Lesepkt rekkefølge']].append(row['Lesepkt id'])

            if row['Unik Id'] not in parts_time_dict.keys():
                parts_time_dict[row['Unik Id']] = {}
            parts_time_dict[row['Unik Id']][row['Tidspunkt lest']] = row['Lesepkt rekkefølge']

            day = row['Tidspunkt lest'].date()
            if row['Lesepkt id'] not in machine_time_dict.keys():
                machine_time_dict[row['Lesepkt id']] = {}
                machine_time_dict[row['Lesepkt id']][day] = []
            elif day not in machine_time_dict[row['Lesepkt id']].keys():
                machine_time_dict[row['Lesepkt id']][day] = []
            machine_time_dict[row['Lesepkt id']][day].append(row['Tidspunkt lest'])
       
        # Start / end time for a series
        processing_time_data = []
        for key, value in parts_time_dict.items():
            first_time = list(value.items())[1][0]
            last_time = list(value.items())[-1][0]

            duration = (last_time-first_time).total_seconds()
            if duration == 24766.0:
                print('Check!'+str(key))
                continue
            processing_time_data.append(duration)
        
        fig, ax = plt.subplots()
        proc_time_mean = np.mean(processing_time_data)
        proc_time_std = np.std(processing_time_data)
        proc_time_distri = norm(proc_time_mean, proc_time_std)
        proc_values = [value for value in np.linspace(0, max(processing_time_data),100)]
        proc_time_prob = [proc_time_distri.pdf(value) for value in proc_values]
        #plt.plot(proc_values, proc_time_prob, color='k', alpha=0.6)
        ax.hist(processing_time_data, bins=100, color='g', alpha = 0.5, density=True)
        plt.xlabel("processing duration [sec]") 
        plt.ylabel("probability")


        #- Smooth / uneven flow - series
        processing_time_parts = dict()
        for k, v in parts_time_dict.items():
            rel_time = []
            ret_val = np.nan
            rel_time = (v-v[0]).astype('timedelta64[ms]')

            if key not in processing_time_parts.keys():
                processing_time_parts[key] = [] 
            processing_time_parts[key] = [rel_time]
       
        fig0, ax0 = plt.subplots()
        ax0.set_title('series processing times')
        ax0.yaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))
        COLORS = np.random.randint(0, 255, size=(max(reader_dict_names.keys())+1, 3),dtype="uint8")
        for k,v in processing_time_parts.items():
            v_delta = mdates.date2num(v[1])
            ax0.plot(v[0], v_delta, '.', color = rgb2hex(COLORS[k][0],COLORS[k][1],COLORS[k][2]))
            ax0.vlines(v[0], [0], v_delta)

        plt.xlabel("time of the day") 
        plt.ylabel("processing duration") 
        plt.legend()

        #- Smooth / uneven flow - machines
        processing_time_machines = dict()
        for key, value in machine_time_dict.items():
            avg = []
            time_ax = []
            ret_val = np.nan
            for k, v in value.items():
                #avg.extend(np.diff(v).astype('timedelta64[ms]').astype(int)/1000)
                avg.extend(np.diff(v).astype('timedelta64[ms]'))
                time_ax.extend(v[0:-1])

            if key not in processing_time_machines.keys():
                processing_time_machines[key] = [[],[]] 
            processing_time_machines[key] = [time_ax,avg]
       
        fig1, ax = plt.subplots()
        ax.set_title('Machine processing times')
        ax.yaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))
        for k,v in processing_time_machines.items():
            v_delta = mdates.date2num(v[1])
            ax.plot(v[0], v_delta, '^', color = rgb2hex(COLORS[k][0],COLORS[k][1],COLORS[k][2]), label=reader_dict_names[k])
            ax.vlines(v[0], [0], v_delta)

        plt.xlabel("time of the day") 
        plt.ylabel("processing duration") 
        plt.legend()

        # Start / end time for a series
        #- Smooth / uneven flow,
        #- Stop that can / will occur
        #- Bottlenecks - where / when
        #- Combination of products that create challenges
        #- Maybe give more accurate occupancy planning than the scoreboard we use today:
        #(simply put: one point = one window)
        


    # define the machines, processes, sensors, and queues
    def create_factory_graph(self):

        # read RFID sample and derive the product flow structure
        rfid_data = pd.read_csv(stngs.DATA_DIR+'G20821.csv',delimiter=";")  
        rfid_data['Tidspunkt lest']= pd.to_datetime(rfid_data['Tidspunkt lest'])
        
        #self.store_from_file_to_influx(machine_ids=rfid_data['Lesepkt id'],  
        #                                times=rfid_data['Tidspunkt lest'])
    
        reader_dict_names = dict(zip(rfid_data['Lesepkt id'], rfid_data['Lesepkt navn']))
        reader_dict_sequence= dict(zip(rfid_data['Lesepkt id'], rfid_data['Lesepkt rekkefølge']))
        sequence_unique_ids = rfid_data['Lesepkt rekkefølge'].unique()
        sequence_ids = {} 
        parts_time_dict = {}
        machine_time_dict = {}
        for index, row in rfid_data.iterrows():
            if row['Lesepkt rekkefølge'] not in sequence_ids.keys():
               sequence_ids[row['Lesepkt rekkefølge']] = [] 
            sequence_ids[row['Lesepkt rekkefølge']].append(row['Lesepkt id'])

            if row['Unik Id'] not in parts_time_dict.keys():
                parts_time_dict[row['Unik Id']] = [] 
            parts_time_dict[row['Unik Id']].append(row['Tidspunkt lest'])

            day = row['Tidspunkt lest'].date()
            if row['Lesepkt id'] not in machine_time_dict.keys():
                machine_time_dict[row['Lesepkt id']] = {}
                machine_time_dict[row['Lesepkt id']][day] = []
            elif day not in machine_time_dict[row['Lesepkt id']].keys():
                machine_time_dict[row['Lesepkt id']][day] = []
            machine_time_dict[row['Lesepkt id']][day].append(row['Tidspunkt lest'])


        def get_avg_proc_time(time_dict):
            avg = []
            ret_val = datetime.timedelta(seconds = 1)
            for key, value in time_dict.items():
                if len(value)>1:
                    avg.append(np.mean(np.diff(value)))
            if len(avg)>0:
                ret_val = np.median(avg)
            
            return ret_val

        # create sensors and machines as objects:
        self.machines = []
        self.sensors = []
        entry_parts_ids = list(rfid_data.loc[rfid_data['Lesepkt navn'] == "Gilje", "Unik Id"])
        for key, value in reader_dict_names.items():
            sensor = dtSensor.dtSensor(name='S'+str(key), type='RFID', description=value)  
  
            machine = dtMachine.dtMachine('M'+str(key), sensors=[sensor], description=value, 
                                            type=dtTypes.dtTypes.MACHINE,
                                            num_parts_in = 1,num_parts_out = 1,
                                            amount_out = 0,amount_in = 0)
            machine.processing_time = 1#int(get_avg_proc_time(machine_time_dict[key]).total_seconds())
            if  value == "Gilje":   
                machine = dtMachine.dtMachine('S1', sensors=[sensor], description=value, 
                                            type=dtTypes.dtTypes.SOURCE,
                                            num_parts_in = 0,num_parts_out = 0,
                                            amount_out = 0,amount_in = 0)  

            self.machines.append(machine)
            self.sensors.append(sensor)
            
        

        self.machines.append(dtMachine.dtMachine('E1', sensors=[], description='Product exit', 
                                            type=dtTypes.dtTypes.EXIT,
                                            num_parts_out = 0,num_parts_in = 0,
                                            amount_out = 0,amount_in = 0))

        file_path_to_gilje_json = stngs.DATA_DIR+'Gilje.json'
        with open(file_path_to_gilje_json, 'r+') as _file:
            json_data=json.load(_file)
        
        arrows_app_posis = {}
        arrow_app_nodes = {}
        for node in json_data['nodes']:
            arrows_app_posis[node['caption']] = (node['position']['x']/5, node['position']['y']/5)
            arrow_app_nodes[node['id']] = {'name': node['caption'], 
                                            'type': node['properties']['type']}

        # creating queues as objects:
        arrow_app_buffers = {}
        for rel in json_data['relationships']:
            from_node = rel['fromId']
            to_node = rel['toId']
            if arrow_app_nodes[to_node]['type'] == 'BUFFER':
                if to_node not in arrow_app_buffers.keys():
                    arrow_app_buffers[to_node] = {}
                arrow_app_buffers[to_node]['from'] = arrow_app_nodes[from_node]['name']

            if arrow_app_nodes[from_node]['type'] == 'BUFFER':
                if from_node not in arrow_app_buffers.keys():
                    arrow_app_buffers[from_node] = {}
                arrow_app_buffers[from_node]['to'] = arrow_app_nodes[to_node]['name']

        self.queues = []
        for key, value in arrow_app_buffers.items():
            q_name = arrow_app_nodes[key]['name']
            q_from =  value['from']
            q_to = value['to']
            q = dtQueue.dtQueue(
                frm=self.get_machine_by_name(q_from), 
                to=self.get_machine_by_name(q_to), 
                capacity=300, 
                name=q_name, 
                description='')
            self.queues.append(q)

        # make a graph
        self.populate_networkx_graph()

        # setting up the parts inventory:
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
        # take 15 parts
        for idx in entry_parts_ids[:15]:
            part = dtPart.dtPart('Pa'+str(idx), type=dtTypes.dtTypes.SINGLE_PART, py2neo_graph=part_g)
            part.createNeo4j()
            self.parts.append(part)
            sb = source_buffers[idx%blen]
            self.get_queue_by_name(sb.name).parts.append(part)                            

        ret_val = self.populate_networkx_graph()  

        for q in self.queues:
            q.position_on_dash = arrows_app_posis[q.name]
        
        for m in self.machines:
            m.position_on_dash = arrows_app_posis[m.name]

        ret_val = self.populate_networkx_graph()  
        return ret_val
    
if __name__ == '__main__':

    gilje_fac = dtGilje() 
    #gilje_fac.create_interesting_plots()
    
    # store as json file
    gilje_fac.serialize(serial_type="json", file_path_or_uri="gilje_factory.json")

    # store in neo4j
    gilje_fac.serialize(serial_type="neo4j", file_path_or_uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASS,need_auth=NEED_AUTH)
    #random_fac.deserialize(serial_type="neo4j", file_path_or_uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASS,need_auth=NEED_AUTH)

    # store as aasx file
    #random_fac.serialize(serial_type="aasx", file_path_or_uri="random_factory.aasx")
    #random_fac.serialize(serial_type="aas", file_path_or_uri="random_factory.aas")


    # Discrete event sumulation     
    #gilje_fac.sim_hours = 20 
    #sim_results = gilje_fac.run(use_kafka_and_neo4j = True, is_real_time = False)
    
    #print(sim_results)

