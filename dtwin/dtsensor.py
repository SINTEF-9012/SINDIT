# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 10:53:46 2021
Sensor class 

@author: marynaw
"""

import matplotlib.pyplot as plt
import dtwin.flux as f
import dtwin.dttypes as dtTypes
from aas import model
import uuid as id

from saas.ass_factory import AASFactory
from saas.semantic_factory import SemanticFactory


class dtSensor(object):
    def __init__(self, name=None, 
                 type=None,

                 position=False, 
                 timeseries=[], # TODO: remove?
                 description=None,
                 json_data = None):
        self.name = name
        self.description = description
        self.type = type
        self.SI = ''
        self.position = position
        self.timeseries = timeseries
        self.uuid = str(id.uuid4())

        # ass
        if self.name is None or self.name.isspace():
            self.name = "SINDIT_Default_Sensor_Name"
        if self.description is None or self.description.isspace():
            self.description = "SINDIT Sensor"
        # nameplate = AASFactory.instance().create_Nameplate(name=self.name + "_Nameplate",
        #                                                    manufacturerName="SINDIT_Default_Manufacturer_Name",
        #                                                    manufacturerProductDesignation=str(self.type) if self.type is not None else self.description,
        #                                                    serialNumber=self.uuid)
        # dictionary = AASFactory.instance().create_ConceptDictionary(name=self.name + "_ConceptDictionary",
        #                                                             concepts={SemanticFactory.instance().getNameplate(),
        #                                                                       SemanticFactory.instance().getManufacturerName(),
        #                                                                       SemanticFactory.instance().getManufacturerProductDesignation(),
        #                                                                       SemanticFactory.instance().getSerialNumber()})
        #
        # self.aas = AASFactory.instance().create_aas(name=self.name,
        #                                             description=self.description,
        #                                             submodels={nameplate},
        #                                             concept_dictionary={dictionary})

        if json_data:
            self.deserialize(json_data)

    def deserialize(self, json_data):
        self.name = json_data["name"]
        self.description = json_data["description"]
        self.type = json_data["type"]
        self.SI = json_data["SI"]
        
    def __str__(self):
        return f'Sensor: {self.name}'

    def __repr__(self):
        return f"Sensor(name='{self.name}', type={self.type}, position='{self.position}')"

    def get_data(self):
        print('// Loading Sensor Data from DB')
        c = f.DTPrototypeInfluxDbClient()
        df = c.get_any_measurement_as_dataframe(self.type, \
                                                {'sensor': self.name})
        x = df.timestamp
        y = df[self.type]
          
        return x, y
    
    def plot_timeseries(self):
        x, y = self.get_data()
        fig, ax = plt.subplots()
        ax.set_title('Measurements from Sensor ' + str(self.name))
        ax.set_xlabel('time')
        ax.set_ylabel(self.type)
        plt.plot(x,y)
        plt.show()
    
    def serialize(self):
        json_data = {
                    'name': [],
                    'description': [],
                    'type': [],
                    'SI': []
                    }
                 
        json_data["name"] = self.name
        json_data["description"] = self.description
        json_data["type"] = self.type
        json_data["SI"] = self.SI
        
        return json_data