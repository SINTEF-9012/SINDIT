from aas import model
from aas.model import *

import saas.ass_factory  as factory
import saas.semantic_factory as semantic


class NameplateSubmodel(Submodel):
    def __init__(self,
                 identification: Identifier,
                 manufacturerName: str,
                 manufacturerProductDesignation: str,
                 serialNumber: str = None,
                 parent: Namespace = None):

        super().__init__(identification)
        self.identification: Identifier = identification

        manufacturerNameElement = factory.AASFactory.instance().create_MultiLanguageProperty(name="ManufacturerName",
                                                                                     value=manufacturerName,
                                                                                     category="PARAMETER",
                                                                                     description=semantic.SemanticFactory.ManufacturerNameID["description"],
                                                                                     parent=self,
                                                                                     semantic_id=semantic.SemanticFactory.instance().getManufacturerName())

        manufacturerProductDesignationElement = factory.AASFactory.instance().create_MultiLanguageProperty(name="ManufacturerProductDesignation",
                                                                                     value=manufacturerProductDesignation,
                                                                                     category="PARAMETER",
                                                                                     description=semantic.SemanticFactory.ManufacturerProductDesignationID["description"],
                                                                                     parent=self,
                                                                                     semantic_id=semantic.SemanticFactory.instance().getManufacturerProductDesignation())

        self.submodel_element.add(manufacturerNameElement)
        self.submodel_element.add(manufacturerProductDesignationElement)



        if serialNumber is not None:
            serialNumberElement = factory.AASFactory.instance().create_MultiLanguageProperty(name="SerialNumber",
                                                                                     value=serialNumber,
                                                                                     category="PARAMETER",
                                                                                     description=semantic.SemanticFactory.SerialNumberID["description"],
                                                                                     parent=self,
                                                                                     semantic_id=semantic.SemanticFactory.instance().getSerialNumber())
            self.submodel_element.add(serialNumberElement)

        self.id_short = "Nameplate"
        self.description = {"en": semantic.SemanticFactory.NameplateID["description"]}
        self.parent = parent
        self.semantic_id=model.AASReference.from_referable(semantic.SemanticFactory.instance().getNameplate())
