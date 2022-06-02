# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 11:51:59 2021

@author: marynaw
"""

import fastapi
import os.path
import json
import py2neo
import configparser
import pandas as pd
import uvicorn

from dtwin.dtfactory import dtFactory
import dtwin.dtpart as dtPart
import dtwin.dttypes as dtTypes
import dtwin.flux as flux
import environment.settings as stngs

app = fastapi.FastAPI()

# Read Config
config = configparser.ConfigParser()
config.read(stngs.BASE_DIR+'/sindit.cfg')
FAC_NEO4J_URI = stngs.NEO4J_FACTORY
FAC_NEO4J_USER = config['factory-neo4j']['user']
FAC_NEO4J_PASS = config['factory-neo4j']['pass']
FAC_NEED_AUTH = config['factory-neo4j']['need_auth']

PARTS_NEO4J_URI = stngs.NEO4J_PARTS
PARTS_NEO4J_USER = config['parts-neo4j']['user']
PARTS_NEO4J_PASS = config['parts-neo4j']['pass']
PARTS_NEED_AUTH = config['parts-neo4j']['need_auth']

c = flux.DTPrototypeInfluxDbClient(stngs.BASE_DIR+'/sindit.cfg')

@app.get("/get_avg_arrival_freq_from_influxDB/{machine_name}")
def get_avg_arrival_freq_from_influxDB(machine_name:str):
    df = c.get_any_measurement_as_dataframe(measurement_type='RFID', \
                                        tags={ 'machine': machine_name, \
                                               'sensor': machine_name+'_OUT' } )
                                             
    avg_arr_frequency_ms = df['timestamp'].diff().mean()
    
    return avg_arr_frequency_ms

@app.get("/get_last_prod_arrival_time_from_influxDB/{machine_name}")
def get_last_prod_arrival_time_from_influxDB(machine_name:str):
    df = c.get_any_measurement_as_dataframe(measurement_type='RFID', \
                                        tags={ 'machine': machine_name, \
                                               'sensor': machine_name+'_OUT' } )
    # times are in UTC, we are converting to naive
    date_time_last_arr = df['timestamp'].tail(1)
    # we are converting to naive
    date_time_last_arr = date_time_last_arr.apply(lambda x:x.tz_convert('Europe/Brussels'))
    # and to string
    date_time_last_arr = date_time_last_arr.dt.strftime('%H:%M').to_string(index=False)
    
    return date_time_last_arr

@app.get("/get_part_cytoscape_from_neo4j/{part_uuid}")
def get_part_cytoscape_from_neo4j(part_uuid:str):
    """Returns data in Cytoscape JSON format (cyjs).
            
        Returns
        -------
        data: list
        A list with cyjs formatted data.
            
        """
    if PARTS_NEED_AUTH.lower() == 'true':
        part_g = py2neo.Graph(PARTS_NEO4J_URI, 
                     user=PARTS_NEO4J_USER, 
                     password=PARTS_NEO4J_PASS)
    else:
        part_g = py2neo.Graph(PARTS_NEO4J_URI)

    query = """MATCH p=(n { uuid: '%s' })-[r*0..]-(m) WITH NODES(p) AS nodes UNWIND nodes AS node RETURN DISTINCT node"""
    query = query % (part_uuid) 
    
    nodes = part_g.run(query)
    
    query = """MATCH p=(n { uuid: '%s' })-[r*0..]-(m)
                WITH Relationships(p) AS rels
                UNWIND rels AS rel
                RETURN DISTINCT rel"""
                
    query = query % (part_uuid) 
    
    relationships = part_g.run(query)
    
    # Define dictionary of empty network
    jsondata = []
    for part_node in nodes:
        p = part_node[0]
        n = {
                 'data': {'id': [],'label': [], 'type': []},
                 'group': [],
                 'classes': [], 
                 }
            
        n["data"]["id"] = p['uuid']
        n["data"]["name"] = p['name']
        n["data"]["label"] = p['description']
        n["data"]["type"] = p['type']
        n["group"] = 'nodes'
        n["classes"] = p['type']
    
        jsondata.append(n)
    
    for rel in relationships:   
        e = rel[0]        
        n = {
            'data': {'source': [],'target': []},
            'classes': []
              }
        n["data"]["source"] = e.__nodes[0]['uuid']
        n["data"]["target"] = e.__nodes[1]['uuid']
        n["group"] = 'edges'
        n["classes"] = 'part_part_edge'
        jsondata.append(n)
            
    return jsondata

@app.post("/push_json_factory_and_parts_to_neo4j/{json_file}")
def push_json_factory_and_parts_to_neo4j(json_file:str):
    print(json_file)
    fac = dtFactory(flushAAS=True)
    fac.deserialize(serial_type="json", file_path_or_uri=json_file)
    fac.serialize(serial_type="neo4j", 
                    file_path_or_uri=FAC_NEO4J_URI, 
                    user=FAC_NEO4J_USER,
                    password=FAC_NEO4J_PASS,
                    need_auth=FAC_NEED_AUTH)
    fac.set_parts_uri(uri=PARTS_NEO4J_URI)
    if len(fac.parts) > 0:
        fac.parts[0].py2neo_graph.delete_all()
        for p in fac.parts:   
            p.createNeo4j()
            
    cytograph = fac.cytoscape_json_data()
    return cytograph

@app.get("/get_factory_cytoscape_from_neo4j")
def get_factory_cytoscape_from_neo4j():
    fac = dtFactory(flushAAS=True)
    fac.deserialize(serial_type="neo4j", 
                    file_path_or_uri=FAC_NEO4J_URI, 
                    user=FAC_NEO4J_USER,
                    password=FAC_NEO4J_PASS,
                    need_auth=FAC_NEED_AUTH)
    cytograph = fac.cytoscape_json_data() 
    return cytograph

@app.post("/get_factory_cytoscape/{factory}")
def get_factory_cytoscape(factory:str):
    fac = dtFactory(flushAAS=True)
    json_data = ''
    if os.path.isfile(factory):
        # seems to be a file we try to open
        _file = open(factory)
        json_data=json.load(_file)
    else:
        json_data=json.loads(factory)
    fac.populate_factory_from_json(json_data)
    cytograph = fac.cytoscape_json_data() 
    return cytograph

@app.get("/get_exit_parts")
def get_exit_parts():
    if FAC_NEED_AUTH.lower() == 'true':
        g = py2neo.Graph(FAC_NEO4J_URI, 
                     user=FAC_NEO4J_USER, 
                     password=FAC_NEO4J_PASS)

    else:
        g = py2neo.Graph(FAC_NEO4J_URI)
    
    exit_nodes = py2neo.matching.NodeMatcher(g).match("EXIT") 
    parts = []
    for node in exit_nodes:
        outlet = py2neo.matching.RelationshipMatch(g, nodes = {node,node},r_type="DELIVERS_TO").where(type='OUTLET').first()
        exit_buffer = outlet.__nodes[0]
        for rel in g.match((exit_buffer,), r_type="HAS_PART"):
            parts.append(rel.end_node["uuid"])
           
    return parts

@app.get("/get_parts_for_buffer/{buffer_name}")
def get_parts_for_buffer(buffer_name:str):
    if FAC_NEED_AUTH.lower() == 'true':
        g = py2neo.Graph(FAC_NEO4J_URI, 
                     user=FAC_NEO4J_USER, 
                     password=FAC_NEO4J_PASS)

    else:
        g = py2neo.Graph(FAC_NEO4J_URI)
    
    buffer_node = py2neo.matching.NodeMatcher(g).match(name=buffer_name).first()
    parts = []
    for rel in g.match((buffer_node,), r_type="HAS_PART"):
        parts.append(rel.end_node["uuid"])
           
    return parts

@app.get("/get_amount_on_queue/{queue_name}")
def get_amount_on_queue(queue_name:str):
    if FAC_NEED_AUTH.lower() == 'true':
        g = py2neo.Graph(FAC_NEO4J_URI, 
                     user=FAC_NEO4J_USER, 
                     password=FAC_NEO4J_PASS)

    else:
        g = py2neo.Graph(FAC_NEO4J_URI)
    
    queue_node = py2neo.matching.NodeMatcher(g).match(name=queue_name).first()
    amount = queue_node['amount']
    return amount

@app.get("/get_factory_name")
def get_factory_name():
    if FAC_NEED_AUTH.lower() == 'true':
        g = py2neo.Graph(FAC_NEO4J_URI, 
                     user=FAC_NEO4J_USER, 
                     password=FAC_NEO4J_PASS)
    else:
        g = py2neo.Graph(FAC_NEO4J_URI)

    graph_property_node = py2neo.matching.NodeMatcher(g).match('GRAPH_PROP_NODE').first() 
    name = graph_property_node['name']
           
    return name

@app.get("/get_sensor_info/{sensor_name}")
def get_sensor_info(sensor_name:str):
    if FAC_NEED_AUTH.lower() == 'true':
        g = py2neo.Graph(FAC_NEO4J_URI, 
                     user=FAC_NEO4J_USER, 
                     password=FAC_NEO4J_PASS)
    else:
        g = py2neo.Graph(FAC_NEO4J_URI)
    sensor_node = py2neo.matching.NodeMatcher(g).match(name=sensor_name).first() 
    
    data={"name": sensor_node['name'],
            "description": sensor_node['description'],
            "type": sensor_node['type']}
           
    return data

@app.post("/get_sim_prediction/{factory}")
def get_sim_prediction(factory:str):
    fac = dtFactory(flushAAS=True)
    json_data = ''
    if os.path.isfile(factory):
        # seems to be a file we try to open
        _file = open(factory)
        json_data=json.load(_file)
    else:
        json_data=json.loads(factory)
    fac.populate_factory_from_json(json_data)
    # Discrete event sumulation     
    sim_results = fac.run()
       
    return sim_results

@app.get("/get_sim_prediction_from_neo4j/{sim_time}")
def get_sim_prediction_from_neo4j(sim_time:int):
    fac_sim = dtFactory(flushAAS=True)
    fac_sim.deserialize(serial_type="neo4j", 
                    file_path_or_uri=FAC_NEO4J_URI,
                    user=FAC_NEO4J_USER,
                    password=FAC_NEO4J_PASS,
                    need_auth=FAC_NEED_AUTH)

    fac_sim.sim_hours = sim_time

    # Discrete event sumulation     
    sim_results = fac_sim.run(use_kafka_and_neo4j = False, is_real_time = False)
       
    return sim_results

@app.get("/run_factory/{sim_time}/{num_entry_amount}")
def run_factory(sim_time:int, num_entry_amount:int):
    fac = dtFactory(flushAAS=True)
    fac.deserialize(serial_type="neo4j", 
                    file_path_or_uri=FAC_NEO4J_URI,
                    user=FAC_NEO4J_USER,
                    password=FAC_NEO4J_PASS,
                    need_auth=FAC_NEED_AUTH)
    
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
    fac.serialize(serial_type="neo4j", 
                file_path_or_uri=FAC_NEO4J_URI, 
                user=FAC_NEO4J_USER, 
                password=FAC_NEO4J_PASS,
                need_auth=FAC_NEED_AUTH)

    # Discrete event sumulation     
    sim_results = fac.run()
       
    return sim_results


# Launch App
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)