# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 10:59:17 2021
Machine class 

@author: marynaw
"""
import matplotlib.artist as ma
import matplotlib.pyplot as plt
import random
import dtwin.dttypes as dtTypes
import simpy
import kafka
import datetime
import json
import dtwin.dtpart as dtPart
import environment.settings as stngs
from aas import model
import uuid as id

from saas.ass_factory import AASFactory

RUN_KAFKA_PRODUCER = True
PRINT_DEBUG_INFO = False
class dtMachine(object):
    
    def __init__(self, name=None,
                 sensors=list(), 
                 description=None,
                 group='NONE', 
                 type=dtTypes.dtTypes.MACHINE, 
                 env = simpy.Environment(),
                 num_parts_in=1,
                 num_parts_out=1,
                 processing_time=1,
                 json_data=None,
                 position_on_dash=list((0,0)),
                 shape_on_dash = 'round-rectangle',
                 color_on_dash = "#b19cd9",
                 size_on_dash = (30,20)):
        self.name = name
        self.sensors = sensors
        self.description = description
        self.group = group
        self.type = type
        self.uuid = str(id.uuid4())
        
        # ass
        if self.name is None or self.name.isspace():
            self.name = "SINDIT_Default_Machine_Name"
        if self.description is None or self.description.isspace():
            self.description = "SINDIT machine"
        self.aas = AASFactory.instance().create_aas(name=self.name, description=self.description)

        # visualization
        self.position_on_dash=position_on_dash
        self.shape_on_dash = shape_on_dash
        self.color_on_dash = color_on_dash
        self.size_on_dash = size_on_dash
        
        # discrete event simulation
        self.env = env
        self.num_parts_in=num_parts_in
        self.num_parts_out=num_parts_out
        self.processing_time=processing_time
        
        #kafka
        if RUN_KAFKA_PRODUCER:
            self.producer = kafka.KafkaProducer(bootstrap_servers=stngs.KAFKA_PRODUCER_URI)
        
        if json_data:
            self.deserialize(json_data)
            
    def deserialize(self, json_data):
        self.name = json_data["name"]
        self.description = json_data["description"]
        self.type = dtTypes.dtTypes[json_data["type"]]
        self.sensors = json_data["sensors"]
        self.group = json_data["group"]
        self.num_parts_in=json_data["num_parts_in"]
        self.num_parts_out=json_data["num_parts_out"]
        self.processing_time=json_data["processing_time"]
        self.position_on_dash=json_data["position_on_dash"]
        self.shape_on_dash=json_data["shape_on_dash"]
        self.color_on_dash=json_data["color_on_dash"]
        self.size_on_dash=json_data["size_on_dash"]

    def serialize(self):
        json_data = {
                    'name': [],
                    'description': [],
                    'group': [],
                    'type': [],
                    'sensors': [],
                    'num_parts_in': [],
                    'num_parts_out': [],
                    'processing_time': [],
                    'position_on_dash': [],
                    'shape_on_dash': [],
                    'color_on_dash': [],
                    'size_on_dash': []
                    }
                  
        json_data["name"] = self.name
        json_data["description"] = self.description
        json_data["group"] = self.group
        json_data["type"] = self.type.name
        json_data["sensors"] = []
        for s in self.sensors:
            json_data["sensors"].append(s.name)
        json_data["num_parts_in"] = self.num_parts_in
        json_data["num_parts_out"] = self.num_parts_out
        json_data["processing_time"] = self.processing_time
        json_data["position_on_dash"] = self.position_on_dash
        json_data["shape_on_dash"]=self.shape_on_dash
        json_data["color_on_dash"]=self.color_on_dash
        json_data["size_on_dash"]=self.size_on_dash
        
        return json_data
           
    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f"Machine(name='{self.name}', sensors='{self.sensors}')"
    
    def _print_debug(self, print_str=''):
        if PRINT_DEBUG_INFO:
            print(print_str)
        
    def run(self, queue_with_parts_in, queue_with_parts_out, use_kafka_and_neo4j = True):
        
        number_of_parts_on_queue = 0
        self._print_debug(self.type.name + ' ' + self.name + ' started production:')
        for q_in in queue_with_parts_in:
            self._print_debug('----------in queue {0} level {1}'.format(q_in.name, len(q_in.parts)))
            number_of_parts_on_queue += len(q_in.parts)
        
        for q_out in queue_with_parts_out:
            self._print_debug('----------out queue {0} level {1}'.format(q_out.name, len(q_out.parts)))

            
        
        while True:                    
            new_part = None                
            
            # fuse all parts from incoming queues in new_part
            for q_in in queue_with_parts_in:
                self._print_debug(self.type.name + ' {0} tries to get {1} parts from queue {2} that has {3} parts stored at hour {4}'.format(
                    self.name, self.num_parts_in, q_in.name, len(q_in.parts), self.env.now))
                part_from_buffer = yield q_in.store.get()
                
                q_in.parts = q_in.store.items # @todo: need to figure out how to yield in dtqueue
                q_in.monitor.append([self.env.now, len(q_in.parts)])
                #fuse all parts   
                if new_part == None:
                    new_part = dtPart.dtPart(name='Pa'+self.name, 
                     type=dtTypes.dtTypes.PROCESSED_PART)
                    if use_kafka_and_neo4j:
                        new_part.py2neo_graph=part_from_buffer.py2neo_graph             
                        new_part.createNeo4j()               
                
                new_part.fuse_parts(part=part_from_buffer, use_neo4j=use_kafka_and_neo4j)
                self._print_debug(self.type.name + ' {0} consumed {1} parts from {2} at hour {3} {4} parts left'.format(
                    self.name, self.num_parts_in, q_in.name, self.env.now, len(q_in.parts)))

                if RUN_KAFKA_PRODUCER and use_kafka_and_neo4j:
                    data_json_IN = json.dumps({ 'buffer_id': q_in.name,
                                               'machine_id': self.name,
                                                'sensor_id': self.name+'_IN', 
                                                 'timestamp_ms': int(datetime.datetime.now().timestamp()*1000), #UTC
                                                 'sim_time_h': self.env.now,
                                                 'part_name': part_from_buffer.name,
                                                 'part_uuid': part_from_buffer.uuid,
                                                 'part_type': part_from_buffer.type.name,
                                                 'part_description': part_from_buffer.description})
                    self.producer.send('aq', data_json_IN.encode('utf-8')) 
            
            # time that the machine is busy with production                          
            yield self.env.timeout(self.processing_time)
            
            if new_part != None:
                # all parts are there something can be produced
                splits = new_part.split_part(num_splits = len(queue_with_parts_out), use_neo4j=use_kafka_and_neo4j)
                for q_out in queue_with_parts_out:
                    self._print_debug(self.type.name + ' {0} tries to put {1} parts on queue {2} that has {3} parts stored at hour {4}'.format(
                    self.name, self.num_parts_out, q_out.name, len(q_out.parts), self.env.now))
                    split_part = splits.pop()
                    yield q_out.store.put(split_part)  # @todo: need to figure out how to yield in dtqueue
                    q_out.parts=q_out.store.items
                    
                    self._print_debug(self.type.name + ' {0} produced {1} parts on {2} at hour {3}'.format(
                        self.name, self.num_parts_out, q_out.name, self.env.now))
                    q_out.monitor.append([self.env.now, len(q_out.parts)])
    
                    if RUN_KAFKA_PRODUCER and use_kafka_and_neo4j:
                        data_json_OUT = json.dumps({ 'machine_id': self.name,
                                                    'buffer_id': q_out.name,
                                                    'sensor_id': self.name+'_OUT', 
                                                     'timestamp_ms': int(datetime.datetime.now().timestamp()*1000), #UTC
                                                     'sim_time_h': self.env.now,
                                                     'part_name': split_part.name,
                                                     'part_uuid': split_part.uuid,
                                                     'part_type': split_part.type.name,
                                                     'part_description': split_part.description})
                        self.producer.send('aq', data_json_OUT.encode('utf-8'))                                                 
        
    def draw_expl(self, expl, explarr, txt, ax, visiblesensors, visiblesensortext):
        ma.setp(expl, visible=True)
        ma.setp(explarr, visible=False)
        print(f'{self.name} is a {self.type.name} and takes {self.num_parts_in} to produce {self.num_parts_out} in {self.processing_time}h')
        ma.setp(txt, text = self.type.name + ' ' + str(self.name) + '\n' + 
                str(self.description) + '\n' + 
                'Sensors: ' + str(list(s.name for s in self.sensors)))
        for vs in visiblesensors:
            vs.remove()
        visiblesensors = []
        for t in visiblesensortext:
            t.remove()
        visiblesensortext = []
        for s in self.sensors:
            print(s)
            if s.position:
                x = 10 + s.position[0]
                y = -2 + s.position[1]
            else:
                a = random.uniform(0,1.9)
                b = random.uniform(0,1.9)
                x = 10 + a
                y = -2 + b
            vs = plt.Rectangle((x,y), .1, .1, color='black', picker=5, label=s.name)
            ax.add_patch(vs)
            visiblesensors.append(vs)
            t = plt.text(x-.2, y-.2, s=s.type)
            visiblesensortext.append(t)
        return visiblesensors, visiblesensortext