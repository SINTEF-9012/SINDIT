from __future__ import annotations
from aas.model import *

#from saas.ass_factory import AASFactory
import saas.ass_factory as factory

class SemanticFactory:
    __instance = None

    NameplateID = {"name":"Nameplate","id_type": IdentifierType.IRI, "id": "https://admin-shell.io/zvei/nameplate/1/0/Nameplate", "description" : "Contains the nameplate information attached to the product" }
    ManufacturerNameID = {"name":"ManufacturerName", "id_type": IdentifierType.IRDI, "id": "0173-1#02-AAO677#002", "description": "Legally valid designation of the natural or judicial person which is directly responsible for the design, production, packaging and labeling of a product in respect to its being brought into circulation"}
    ManufacturerProductDesignationID = {"name":"ManufacturerProductDesignation", "id_type": IdentifierType.IRDI, "id": "0173-1#02-AAW338#001", "description": "Short description of the product (short text)"}
    SerialNumberID = {"name":"SerialNumber", "id_type": IdentifierType.IRDI, "id": "0173-1#02-AAM556#002", "description":"Unique combination of numbers and letters used to identify the device once it has been manufactured"}

    @staticmethod
    def instance() -> SemanticFactory:
        if SemanticFactory.__instance == None:
            SemanticFactory()
        return SemanticFactory.__instance

    def __init__(self):
        if SemanticFactory.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            SemanticFactory.__instance = self
            self.Nameplate = None
            self.ManufacturerName = None
            self.ManufacturerProductDesignation = None
            self.SerialNumber = None

    @staticmethod
    def create_ConceptDescription(data):
        return factory.AASFactory.instance().create_ConceptDescription(name=data["name"],
                                                               identification=Identifier(id_=data["id"], id_type=data["id_type"]),
                                                               description=data["description"])
    def getNameplate(self)->ConceptDescription:
        if self.Nameplate is None:
            self.Nameplate = SemanticFactory.create_ConceptDescription(SemanticFactory.NameplateID)
        return self.Nameplate

    def getManufacturerName(self)->ConceptDescription:
        if self.ManufacturerName is None:
            self.ManufacturerName = SemanticFactory.create_ConceptDescription(SemanticFactory.ManufacturerNameID)
        return self.ManufacturerName

    def getManufacturerProductDesignation(self)->ConceptDescription:
        if self.ManufacturerProductDesignation is None:
            self.ManufacturerProductDesignation = SemanticFactory.create_ConceptDescription(SemanticFactory.ManufacturerProductDesignationID)
        return self.ManufacturerProductDesignation

    def getSerialNumber(self)->ConceptDescription:
        if self.SerialNumber is None:
            self.SerialNumber = SemanticFactory.create_ConceptDescription(SemanticFactory.SerialNumberID)
        return self.SerialNumber






