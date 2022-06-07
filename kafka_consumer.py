# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 11:51:59 2021

@author: marynaw
"""

import kafka
import dtwin.flux as flux
import json
import py2neo
import configparser
import dtwin.dttypes as dtTypes
import environment.environment as stngs
import os

from config import global_config as cfg

# Read Config
config = configparser.ConfigParser()
path_to_config = os.path.join(cfg.PATH_TO_CONFIG)
config.read(path_to_config)
NEO4J_URI = stngs.NEO4J_FACTORY
NEO4J_USER = config['factory-neo4j']['user']
NEO4J_PASS = config['factory-neo4j']['pass']
NEED_AUTH = config['factory-neo4j']['need_auth']


consumer = kafka.KafkaConsumer('aq', bootstrap_servers=stngs.KAFKA_PRODUCER_URI,value_deserializer=lambda m: json.loads(m.decode('utf-8')))

c = flux.DTPrototypeInfluxDbClient(path_to_config)

def get_machine_type_from_name(name):
    if name[0]=='P': 
        return dtTypes.dtTypes.PROCESS.name
    if name[0]=='M': 
        return dtTypes.dtTypes.MACHINE.name
    else:
        return dtTypes.dtTypes.UNKNOWM.name

def get_sensor_type_from_name(name):
    if name[-1]=='N': 
        return 'IN'
    if name[-1]=='T': 
        return 'OUT'
    else:
        return dtTypes.dtTypes.UNKNOWM.name
        
def serialize_part(part):
    if NEED_AUTH.lower() == 'true':
        g = py2neo.Graph(NEO4J_URI, 
                     user=NEO4J_USER, 
                     password=NEO4J_PASS)
    else:
        g = py2neo.Graph(NEO4J_URI)
  
    nodes = py2neo.matching.NodeMatcher(g)       
    sensor_type = get_sensor_type_from_name(part['sensor_ID'])    
    
    b = nodes.match(dtTypes.dtTypes.BUFFER.name, name=part['buffer_ID']).first() 
    p = nodes.match(part['type'], uuid=part['uuid']).first() 

    b.update(amount=part['amount'])          
    g.push(b) 
    print("%s amount: %s"% (amount['sensor_ID'], amount['amount']))

    tx = g.begin()
    
    if isinstance(p, py2neo.Node) and sensor_type=='IN':        
        tx.delete(p)
        print("deleted %s part: %s "% (part['sensor_ID'], part['uuid']))
    elif sensor_type=='OUT':           
        p = py2neo.Node(part['type'], name=part['name'],uuid=part['uuid'],type=part['type'],description=part['description'])
        print("created %s part: %s"% (part['sensor_ID'], part['uuid']))
        tx.create(p)
        tx.create(py2neo.Relationship(b, "HAS_PART", p))
                        
    tx.commit()

def serialize_value(amount):
    if NEED_AUTH.lower() == 'true':
        g = py2neo.Graph(NEO4J_URI, 
                     user=NEO4J_USER, 
                     password=NEO4J_PASS)
    else:
        g = py2neo.Graph(NEO4J_URI)
  
    nodes = py2neo.matching.NodeMatcher(g)        
    
    b = nodes.match(dtTypes.dtTypes.CONTAINER.name, name=amount['buffer_ID']).first() 
    b.update(amount=amount['amount'])
            
    g.push(b) 

    print("%s amount: %s"% (amount['sensor_ID'], amount['amount']))
                        

# part = {
#           "machine_ID": 'P1',
#           "sensor_ID": 'P1_IN',
#           "time_ms": 123345564567,
#           "sim_time": 1,
#           "name": 'Pa0',
#           "uuid": 'fbd204a7-318e-4dd3-86e0-e6d524fc3f98'
#         }   
# serialize(part)

for msg in consumer:
    if msg.value['queue_type'] == 'BUFFER':
        part = {
            "machine_ID": msg.value['machine_id'],
            "buffer_ID": msg.value['buffer_id'],
            "sensor_ID": msg.value['sensor_id'],
            "time_ms": msg.value['timestamp_ms'],
            "sim_time": msg.value['sim_time_h'],
            "name": msg.value['part_name'],
            "amount": msg.value['amount'],
            "uuid": msg.value['part_uuid'],
            "type": msg.value['part_type'],
            "description": msg.value['part_description'],
            }
        print("machine=%s %s, sensor=%s buffer=%s part: %s" % (get_machine_type_from_name(part['machine_ID']), part['machine_ID'], part['sensor_ID'], part['buffer_ID'], part['uuid']))
        tags = {'machine': part['machine_ID'], 'sensor': part['sensor_ID']}
        c.store_any_measurement('RFID', tags, 1, part['time_ms'])
        
        serialize_part(part)
    elif msg.value['queue_type'] == 'CONTAINER':
        amount = {
          "machine_ID": msg.value['machine_id'],
          "buffer_ID": msg.value['buffer_id'],
          "sensor_ID": msg.value['sensor_id'],
          "time_ms": msg.value['timestamp_ms'],
          "sim_time": msg.value['sim_time_h'],
          "amount": msg.value['amount'],
        }
        print("machine=%s %s, sensor=%s buffer=%s amount: %s" % (get_machine_type_from_name(amount['machine_ID']), amount['machine_ID'], amount['sensor_ID'], amount['buffer_ID'], amount['amount']))
        tags = {'machine': amount['machine_ID'], 'sensor': amount['sensor_ID']}
        c.store_any_measurement('AMOUNT', tags, amount['amount'], amount['time_ms'])
        
        serialize_value(amount)
    

    