from __future__ import annotations

from aas import model
import re

from aas.model import DictObjectStore
from aas.util.identification import NamespaceIRIGenerator

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
        if AASFactory.__instance == None:
            AASFactory()
        return AASFactory.__instance


    def __init__(self):
        if AASFactory.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            AASFactory.__instance = self
            namespace = "https://sindit.no/#"
            provider = DictObjectStore()
            self.iriGenerator = NamespaceIRIGenerator(namespace=namespace, provider=provider)
            self.assetStore = DictObjectStore()

    def create_asset(self,
                     name:str,
                     category:str = None,
                     description:str = None) -> model.Asset:
        id_short = Util.convert_name_to_id_short(name)
        identification = self.iriGenerator.generate_id(proposal=id_short)
        asset = model.Asset(kind=model.AssetKind.INSTANCE,
                            identification=identification,
                            id_short=id_short,
                            category=category,
                            description={"en" : description})

        self.assetStore.add(asset)

        return asset

    def create_aas(self, name,
                   asset:model.Asset = None,
                   category:str = None,
                   description:str = None) -> model.AssetAdministrationShell:

        id_short = Util.convert_name_to_id_short(name)
        identification = self.iriGenerator.generate_id(proposal=id_short)

        if asset is None: asset = self.create_asset(id_short + "_Asset")

        aas = model.AssetAdministrationShell(identification=identification,
                                             asset=model.AASReference.from_referable(asset),
                                             id_short=id_short,
                                             category=category,
                                             description={"en" : description})

        self.assetStore.add(aas)

        return aas





