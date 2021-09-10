# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 11:34:58 2021

@author: marynaw
"""
import dtwin.dttypes as dtTypes
import copy
import py2neo
import uuid as id

class dtPart(object):
    def __init__(self, name=None, 
                 type=None, 
                 description='na',
                 position=False,
                 json_data=None,
                 py2neo_graph=None,
                 uuid = None):
        if uuid == None:
            self.uuid = str(id.uuid4())    
        else:
            self.uuid = uuid
            
        self.name = name
        self.description = description
        self.type = type
        self.py2neo_graph = py2neo_graph        
        self.json_data = json_data
        if json_data:
            self.deserialize(json_data)

    def __str__(self):
        return f'Part: {self.name}'

    def __repr__(self):
        return f"Part(name={self.name}, type={self.type})"
    
    def process_part(self):
        self.type = dtTypes.dtTypes.PROCESSED_PART
    
    # when we fuse then we just add another node and add the name becomes the 
    # combination of the parts with an 'f' for fuse as Pa1.fuse(Pa2) = Pa1fPa2.     
    def fuse_parts(self, part, use_neo4j = True):  
        self.name += 'f'+part.name 
        self.type = dtTypes.dtTypes.PROCESSED_PART       
        if use_neo4j:
            self.updateAttrNeo4j()
            self.connectNeo4j(part)
        
        return True

    # when splitting we just add another node with the same name 
    # but append 's' for split and the index. We do this only if
    # num_splits>1. We also add adges as the original node
    # as Pa1.split(3) = [Pa1s0, Pa1s1, Pa1s2]
    def split_part(self, num_splits, use_neo4j = True):
        splits = []
        if num_splits > 1:
            for idx in range(num_splits):           
                part = copy.copy(self)
                part.name = self.name+'s'+str(idx)
                part.description = 'tbd'
                part.type = dtTypes.dtTypes.PROCESSED_PART
                part.uuid = str(id.uuid4())
                splits.append(part)
                if use_neo4j:
                    part.createNeo4j()
                    self.updateAttrNeo4j()
                    self.connectNeo4j(part)
        else:
           splits.append(self)
           
                         
        return splits
    
    def serialize(self): 
        json_data = {
                    'name': [],
                    'description': [],
                    'type': [],
                    'uuid': []
                    }
                 
        json_data["name"] = self.name
        json_data["description"] = self.description
        json_data["type"] = self.type.name
        json_data["uuid"] = self.uuid
        
        return json_data
                
    def deserialize(self, json_data):
        self.name = json_data["name"]
        self.description = json_data["description"]
        self.type = dtTypes.dtTypes[json_data["type"]]
        self.uuid = json_data["uuid"]

   
    def createNeo4j(self):
        if isinstance(self.py2neo_graph, py2neo.Graph): 
            all_part_nodes = py2neo.matching.NodeMatcher(self.py2neo_graph)
            self_part = all_part_nodes.match(self.type.name, uuid=self.uuid).first()
        
            if not isinstance(self_part, py2neo.Node):               
                tx = self.py2neo_graph.begin()               
                p = py2neo.Node(self.type.name, name=self.name,
                                    type=self.type.name,
                                    description=self.description,
                                    uuid=self.uuid)
                tx.create(p) 
                tx.commit()
                print('Created new part '+ self.uuid)
                return True
            else:
                print('Part already there '+ self.uuid)
                return False
        else:
            print('Error: no neo4j graph available')
            raise IOError
            return False
        
    def updateAttrNeo4j(self):
        if isinstance(self.py2neo_graph, py2neo.Graph):
            all_part_nodes = py2neo.matching.NodeMatcher(self.py2neo_graph)
            self_part = all_part_nodes.match(self.type.name, uuid=self.uuid).first()
            
            if not isinstance(self_part, py2neo.Node):
                print('Cannot find part '+ self_part.uuid)
                raise IOError
                return False
            
            self_part.update(name=self.name,
                             type=self.type.name,
                             description=self.description,
                             uuid=self.uuid)
            
            self.py2neo_graph.push(self_part) 
            return True
        else:
            print('Error: no neo4j graph available')
            raise IOError
            return False
    
    def connectNeo4j(self, part):
        if isinstance(self.py2neo_graph, py2neo.Graph):
            all_part_nodes = py2neo.matching.NodeMatcher(self.py2neo_graph)
            self_part_node = all_part_nodes.match(self.type.name, uuid=self.uuid).first() 
            part_node = all_part_nodes.match(part.type.name, uuid=part.uuid).first() 
                   
            if not isinstance(self_part_node, py2neo.Node):
                print('Cannot find part '+ self.uuid)
                raise IOError
                return False
            
            if not isinstance(part_node, py2neo.Node):
                print('Cannot find part '+ part.uuid)
                raise IOError
                return False
                  
                                      
            tx = self.py2neo_graph.begin()     
            tx.create(py2neo.Relationship(self_part_node, "CONSISTS_OF", part_node))
            tx.commit()    
    
            return True
        else:
            print('Error: no neo4j graph available')
            raise IOError
            return False
        
    
    
    
    