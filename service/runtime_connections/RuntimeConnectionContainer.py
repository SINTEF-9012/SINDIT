from typing import Dict, List
from graph_domain.RuntimeConnectionNode import (
    RuntimeConnectionNode,
    RuntimeConnectionTypes,
)
from graph_domain.TimeseriesNode import TimeseriesNodeDeep, TimeseriesNodeFlat
from service.runtime_connections.RuntimeConnection import RuntimeConnection

from service.runtime_connections.SensorConnection import SensorConnection
from service.runtime_connections.TimeseriesInput import TimeseriesInput
from service.runtime_connections.mqtt.MqttRuntimeConnection import (
    MqttRuntimeConnection,
)
from service.runtime_connections.mqtt.MqttTimeseriesInput import MqttTimeseriesInput
from service.runtime_connections.opcua.OpcuaRuntimeConnection import (
    OpcuaRuntimeConnection,
)
from service.runtime_connections.opcua.OpcuaTimeseriesInput import OpcuaTimeseriesInput
from service.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)
from service.specialized_databases.timeseries.influx_db.InfluxDbPersistenceService import (
    InfluxDbPersistenceService,
)

# Maps node-types to the connection / input classes
RT_CONNECTION_MAPPING = {
    RuntimeConnectionTypes.MQTT.value: MqttRuntimeConnection,
    RuntimeConnectionTypes.OPC_UA.value: OpcuaRuntimeConnection,
}
RT_INPUT_MAPPING = {
    RuntimeConnectionTypes.MQTT.value: MqttTimeseriesInput,
    RuntimeConnectionTypes.OPC_UA.value: OpcuaTimeseriesInput,
}


class RuntimeConnectionContainer:
    """
    Holds and manages all current runtime connection services
    """

    __instance = None

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls()
        return cls.__instance

    def __init__(self):
        if self.__instance is not None:
            raise Exception("Singleton instantiated multiple times!")

        RuntimeConnectionContainer.__instance = self

        self.connections: Dict[str, RuntimeConnection] = {}

    def get_runtime_connection(self, iri: str):
        return self.connections.get(iri)

    def register_runtime_connection(self, iri: str, connection: RuntimeConnection):
        self.connections[iri] = connection

    def initialize_connections_inputs_and_handlers(
        self, timeseries_nodes: List[TimeseriesNodeDeep]
    ):
        # Prepare nodes to avoid redundand connections:

        # Get connection nodes
        # Dict to remove duplicate connections (multiple inputs for one connection each having a different child...)
        connection_nodes: Dict[str, RuntimeConnectionNode] = {}
        ts_inputs_for_connection_iri: Dict[str, List[TimeseriesInput]] = {}
        # db_con_iri_for_input: Dict[str, str] = {}

        ts_node: TimeseriesNodeDeep
        for ts_node in timeseries_nodes:
            # Add the connection node, if new
            connection_nodes[
                ts_node.runtime_connection.iri
            ] = ts_node.runtime_connection

            # Create the timeseries input
            input_class: TimeseriesInput = RT_INPUT_MAPPING.get(
                ts_node.runtime_connection.type
            )

            ts_input: TimeseriesInput = input_class.from_timeseries_node(ts_node)

            # Add the input to the list of its connection
            ts_inputs_list = ts_inputs_for_connection_iri.get(
                ts_node.runtime_connection.iri
            )

            if ts_inputs_list is None:
                ts_inputs_list = []

            ts_inputs_list.append(ts_input)

            ts_inputs_for_connection_iri[
                ts_node.runtime_connection.iri
            ] = ts_inputs_list

            # Get the persistence handler method and activate it
            ts_service: InfluxDbPersistenceService = (
                DatabasePersistenceServiceContainer.instance().get_persistence_service(
                    iri=ts_node.db_connection.iri
                )
            )

            ts_input.register_handler(handler_method=ts_service.write_measurement)

        rt_con_node: RuntimeConnectionNode
        for rt_con_node in connection_nodes.values():

            # Create actual connections:
            input_class = RT_CONNECTION_MAPPING.get(rt_con_node.type)

            rt_connection: RuntimeConnection = input_class.from_runtime_connection_node(
                rt_con_node
            )

            self.connections[rt_con_node.iri] = rt_connection

            # Link the inputs to its connections:
            rt_connection.timeseries_inputs = ts_inputs_for_connection_iri.get(
                rt_con_node.iri
            )

    def start_connections(self):
        """
        Starts all connections
        :return:
        """
        connection: RuntimeConnection
        for connection in self.connections.values():
            connection.start_connection()

    def get_all_inputs(self) -> List[TimeseriesInput]:
        """
        :return: All sensor inputs (both MQTT and OPCUA)
        """
        inputs = []
        con: RuntimeConnection
        for con in self.connections.values:
            inputs.extend(con.timeseries_inputs)

        return inputs
