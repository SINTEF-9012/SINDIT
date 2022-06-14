import json

from graph_domain.Machine import MachineFlat, MachineDeep
from service.knowledge_graph.KnowledgeGraphPersistenceService import KnowledgeGraphPersistenceService


class MachinesDao(object):
    """
    Data Access Object for Machines
    """
    __instance = None

    @staticmethod
    def instance():
        if MachinesDao.__instance is None:
            MachinesDao()
        return MachinesDao.__instance

    def __init__(self):
        if MachinesDao.__instance is not None:
            raise Exception("Singleton instantiated multiple times!")

        MachinesDao.__instance = self

        self.ps: KnowledgeGraphPersistenceService = KnowledgeGraphPersistenceService.instance()

    def get_machines_flat(self):
        """
        Queries all machine nodes. Does not follow any relationships
        :param self:
        :return:
        """
        machines_flat_matches = self.ps.repo.match(model=MachineFlat)

        return [m for m in machines_flat_matches]

    def get_machines_deep(self):
        """
        Queries all machine nodes. Follows relationships to build nested objects for related nodes (e.g. sensors)
        :param self:
        :return:
        """
        machines_deep_matches = self.ps.repo.match(model=MachineDeep)

        # Get rid of the 'Match' and 'RelatedObject' types in favor of normal lists automatically
        # by using the auto-generated json serializer
        return [MachineDeep.from_json(m.to_json()) for m in machines_deep_matches]

    def get_machines_deep_json(self):
        """
        Queries all machine nodes. Follows relationships to build nested objects for related nodes (e.g. sensors)
        Directly returns the serialized json instead of nested objects. This is faster than using the nested-object
        getter and serializing afterwards, as it does not require an intermediate step.
        :param self:
        :return:
        """
        machines_deep_matches = self.ps.repo.match(model=MachineDeep)

        return json.dumps([m.to_json() for m in machines_deep_matches])

    # def get_machines(self):
    #
    #     timeseries = self.__repo.match(model=Timeseries)
    #
    #     print(timeseries)
    #
    #     m1 = MachineFlat(id_short="test")
    #     print(m1)
    #
    #     machines_flat = self.__repo.match(model=MachineFlat)
    #
    #     print(machines_flat)
    #
    #     #machines = py2neo.matching.NodeMatcher(self.__graph).match("MACHINE")
    #     machines = self.__repo.match(model=MachineDeep)
    #
    #     print(machines)
    #     print("END machines")

    # def write_measurement(self,
    #                       id_uri: str,
    #                       value,
    #                       reading_time: datetime = None
    #                       ):
    #     """
    #     Writes the given value to the standard bucket into the measurement according to the id_uri into a field
    #     called 'reading'.
    #     When no reading time is given, the current database time is being used.
    #     :param id_uri:
    #     :param value:
    #     :param reading_time:
    #     :return:
    #     """
    #
    #     record = Point(measurement_name=id_uri) \
    #         .field(field=READING_FIELD_NAME, value=value)
    #     if reading_time is not None:
    #         record.time(reading_time)
    #     self.__write_api.write(bucket=self.bucket, record=record)
    #
    # def read_period_to_dataframe(self,
    #                              id_uri: str,
    #                              begin_time: datetime,
    #                              end_time: datetime
    #                              ) -> pd.DataFrame:
    #     """
    #     Reads all measurements from the sensor with the given ID in the time period
    #     :param id_uri:
    #     :param begin_time:
    #     :param end_time:
    #     :return: Dataframe containing all measurements in that period
    #     :raise IdNotFoundException: if the id_uri is not found
    #     """
    #     query = f'from(bucket: "{self.bucket}")\n' \
    #             f'|> range(start: {begin_time.astimezone().isoformat()}, stop: {end_time.astimezone().isoformat()})\n' \
    #             f'|> filter(fn: (r) => r["_measurement"] == "{id_uri}")' \
    #             f'|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")\n' \
    #             f'|> keep(columns: ["_time", "{READING_FIELD_NAME}"])'
    #
    #     try:
    #         df = self.__query_api.query_data_frame(query=query)
    #
    #         # Dataframe cleanup
    #         df.drop(columns=["result", "table"], axis=1, inplace=True)
    #         df.rename(columns={"_time": "time", READING_FIELD_NAME: "value"}, inplace=True)
    #
    #         return df
    #
    #     except KeyError:
    #         # id_uri not found
    #         raise IdNotFoundException
