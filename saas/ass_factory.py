from __future__ import annotations

import random
import re
from datetime import datetime

import interchange.math
from aas.model import *
from aas.util.identification import *

from saas.NameplateSubmodel import NameplateSubmodel


class Util:
    @staticmethod
    def convert_name_to_id_short(name):
        # Remove all non-word characters (everything except numbers and letters)
        s = re.sub(r"[^\w\s]", '', name)

        # Replace all runs of whitespace with a single dash
        s = re.sub(r"\s+", '_', s)

        # Add A_ if the name does not start with a letter
        if not re.match("^([a-zA-Z].*|)$", s):
            s = "A_" + s;
        return s


class AASFactory:
    __instance = None

    @staticmethod
    def instance() -> AASFactory:
        if AASFactory.__instance is None:
            AASFactory()
        return AASFactory.__instance

    def __init__(self):
        if AASFactory.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            AASFactory.__instance = self
            namespace = "https://sindit.no/#"
            self.provider = DictObjectStore()
            self.iriGenerator = NamespaceIRIGenerator(namespace=namespace, provider=self.provider)
            self.assetStore = DictObjectStore()

    def create_asset(self,
                     name: str,
                     category: str = None,
                     description: str = None) -> model.Asset:
        id_short = Util.convert_name_to_id_short(name)
        identification = self.iriGenerator.generate_id(proposal=id_short)
        asset = model.Asset(kind=model.AssetKind.INSTANCE,
                            identification=identification,
                            id_short=id_short,
                            category=category,
                            description={"en": description} if description is not None else None, )

        self.assetStore.add(asset)

        return asset

    def create_aas(self,
                   name,
                   asset: model.Asset = None,
                   category: str = None,
                   description: str = None,
                   submodels: Set[Submodel] = None,
                   concept_dictionary: Iterable[concept.ConceptDictionary] = ()
                   ) -> model.AssetAdministrationShell:

        id_short = Util.convert_name_to_id_short(name)
        identification = self.iriGenerator.generate_id(proposal=id_short)

        if asset is None: asset = self.create_asset(id_short + "_Asset")

        submodel = ()
        if submodels is not None:
            submodel = set()
            for m in submodels:
                submodel.add(model.AASReference.from_referable(m))

        aas = model.AssetAdministrationShell(identification=identification,
                                             asset=model.AASReference.from_referable(asset),
                                             id_short=id_short,
                                             category=category,
                                             description={"en": description} if description is not None else None,
                                             submodel=submodel,
                                             concept_dictionary=concept_dictionary)

        if submodels is not None:
            for m in submodels:
                m.parent = aas

        if concept_dictionary is not None:
            for d in concept_dictionary:
                d.parent = aas

        self.assetStore.add(aas)

        return aas

    def create_ConceptDescription(self,
                                  name: str,
                                  identification: Identifier = None,
                                  description: str = None,
                                  parent: Namespace = None,
                                  ) -> ConceptDescription:

        id_short = Util.convert_name_to_id_short(name)
        if identification is None:
            identification = self.iriGenerator.generate_id(proposal=id_short)
        concept = ConceptDescription(identification=identification,
                                     id_short=id_short,
                                     description={"en": description} if description is not None else None,
                                     parent=parent)

        self.assetStore.add(concept)

        return concept

    def create_ConceptDictionary(self,
                                 name: str,
                                 parent: Namespace = None,
                                 concepts: Set[ConceptDescription] = None) -> ConceptDictionary:

        id_short = Util.convert_name_to_id_short(name)

        concept_description = None
        if concepts is not None:
            concept_description = set()
            for concept in concepts:
                concept_description.add(model.AASReference.from_referable(concept))

        dictionary = ConceptDictionary(id_short=id_short,
                                       description={
                                           "en": "Unordered list of concept descriptions of elements used within submodels of the AAS"},
                                       parent=parent,
                                       concept_description=concept_description)
        # self.assetStore.add(dictionary)
        return dictionary

    def create_MultiLanguageProperty(self,
                                     name: str,
                                     value: str,
                                     category: str = None,
                                     description: str = None,
                                     parent: Namespace = None,
                                     semantic_id: ConceptDescription = None
                                     ) -> MultiLanguageProperty:

        id_short = Util.convert_name_to_id_short(name)

        property = MultiLanguageProperty(id_short=id_short,
                                         description={"en": description} if description is not None else None,
                                         parent=parent,
                                         value={"en": value},
                                         category=category,
                                         semantic_id=model.AASReference.from_referable(
                                             semantic_id) if semantic_id is not None else None
                                         )
        # self.assetStore.add(property)
        return property

    def create_Nameplate(self,
                         name: str,
                         manufacturerName: str,
                         manufacturerProductDesignation: str,
                         serialNumber: str = None,
                         parent: Namespace = None
                         ) -> NameplateSubmodel:

        id_short = Util.convert_name_to_id_short(name)
        proposal = id_short + str(datetime.now())
        identification = self.iriGenerator.generate_id(proposal=proposal)

        nameplate = NameplateSubmodel(identification=identification,
                                      manufacturerName=manufacturerName,
                                      manufacturerProductDesignation=manufacturerProductDesignation,
                                      serialNumber=serialNumber,
                                      parent=parent)

        self.assetStore.add(nameplate)

        return nameplate

    def flush(self):
        self.assetStore.clear()
        self.provider.clear()
