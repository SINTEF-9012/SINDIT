# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 10:59:35 2021

Queue class

@author: marynaw
"""
import matplotlib.artist as ma
import dtwin.dttypes as dtTypes
import dtwin.dtpart as dtPart
import simpy
from aas import model
import uuid as id

from saas.ass_factory import AASFactory
from saas.semantic_factory import SemanticFactory


class dtQueue(object):
    def __init__(self, frm=None, to=None, 
                 capacity=1000, 
                 name = None,
                 description=None,
                 env = simpy.Environment(), 
                 group='NONE',
                 json_data=None,
                 position_on_dash=list((0,0)),
                 shape_on_dash = 'round-rectangle',
                 color_on_dash = "#efcc61",
                 size_on_dash = (10,5)):

        self.name = name
        self.frm = frm
        self.to = to
        self.type = dtTypes.dtTypes.BUFFER
        self.group = group
        self.sensors = []
        self.capacity = capacity        
        self.description = description
        self.parts = list()
        self.uuid = str(id.uuid4())
        
        # ass
        # ass
        if self.name is None or self.name.isspace():
            self.name = "SINDIT_Default_Queue_Name"
        if self.description is None or self.description.isspace():
            self.description = "SINDIT queue"
        nameplate = AASFactory.instance().create_Nameplate(name=self.name + "_Nameplate",
                                                           manufacturerName="SINDIT_Default_Manufacturer_Name",
                                                           manufacturerProductDesignation=self.description,
                                                           serialNumber=self.uuid)
        dictionary = AASFactory.instance().create_ConceptDictionary(name=self.name + "_ConceptDictionary",
                                                                    concepts={SemanticFactory.instance().getNameplate(),
                                                                              SemanticFactory.instance().getManufacturerName(),
                                                                              SemanticFactory.instance().getManufacturerProductDesignation(),
                                                                              SemanticFactory.instance().getSerialNumber()})

        self.aas = AASFactory.instance().create_aas(name=self.name,
                                                    description=self.description,
                                                    submodels={nameplate},
                                                    concept_dictionary={dictionary})
        
        # visualization
        self.position_on_dash = position_on_dash
        self.shape_on_dash = shape_on_dash
        self.color_on_dash = color_on_dash
        self.size_on_dash = size_on_dash
                
        if json_data:
            self.deserialize(json_data)
        
        # in case there is still no name or description
        if self.name == '':
            self.name = f"{self.frm.name}-{self.to.name}"
        if self.description == '':
            self.description = f"This is the queue from {self.frm.name} to {self.to.name}"
        
        # discrete event simulation
        self.env = env
        self.store = simpy.Store(env, capacity = self.capacity)
        self.store.items = list(self.parts) #we need a copy here as python works with mutable references
        self.monitor = [[0,len(self.parts)]] 
                   
        
    def deserialize(self, json_data):
        self.name = json_data["name"]
        self.frm = json_data["frm"]
        self.to = json_data["to"]
        self.description = json_data["description"]
        self.sensors = json_data["sensors"]
        self.group = json_data["group"]
        self.capacity=json_data["capacity"]
        self.parts=json_data["parts"] #this is a list with uuids that need to be transformed in dtParts
        self.position_on_dash=json_data["position_on_dash"]
        self.shape_on_dash=json_data["shape_on_dash"]
        self.color_on_dash=json_data["color_on_dash"]
        self.size_on_dash=json_data["size_on_dash"]
        
    def __str__(self):
        return f'Queue from: {self.frm} to: {self.to}'

    def __repr__(self):
        return f"Queue(frm={self.frm}, to={self.to})"
    
    def create_store(self):
        self.store = simpy.Store(self.env, capacity = self.capacity)
        self.store.items = list(self.parts) #we need a copy here as python works with mutable references
        
    def draw_explarr(self, expl, explarr, txt, visiblesensors, visiblesensortext):
        ma.setp(expl, visible=False)
        ma.setp(explarr, visible=True)
        parts_string = ''
        for p in self.store.items:
            parts_string += str(p.name)+ '-'
            
        ma.setp(txt, text = 'Queue              ' + str(self.frm.name) + ' --> ' + str(self.to.name) +
                     '\n' + 'capacity:          ' + str(self.capacity) +
                     '\n' + 'parts:             ' + str(len(self.parts)) +
                     '\n' + str(self.description))       
        for vs in visiblesensors:
            vs.remove()
        visiblesensors = []
        for t in visiblesensortext:
            t.remove()
        visiblesensortext = []
        return visiblesensors, visiblesensortext
    
    def serialize(self):
        json_data = {
                    'name': [],
                    'description': [],
                    'frm': [],
                    'to': [],
                    'group': [],
                    'capacity': [],
                    'parts': [],
                    'position_on_dash': [],
                    'shape_on_dash': [],
                    'color_on_dash': [],
                    'size_on_dash': []
                    }
                 
        json_data["name"] = self.name
        json_data["description"] = self.description
        json_data["frm"] = self.frm.name
        json_data["to"] = self.to.name
        json_data["group"] = self.group
        json_data["capacity"] = self.capacity
        json_data["sensors"] = self.sensors
        json_data["position_on_dash"] = self.position_on_dash
        json_data["shape_on_dash"]=self.shape_on_dash
        json_data["color_on_dash"]=self.color_on_dash
        json_data["size_on_dash"]=self.size_on_dash
        json_data["parts"] = []
        for p in self.store.items:
            json_data["parts"].append(p.uuid)
        
        return json_data