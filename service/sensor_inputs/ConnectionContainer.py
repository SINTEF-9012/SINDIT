from typing import List

from service.sensor_inputs.SensorConnection import SensorConnection
from service.sensor_inputs.SensorInput import SensorInput
from service.sensor_inputs.mqtt.MqttSensorConnection import MqttSensorConnection
from service.sensor_inputs.mqtt.MqttSensorInput import MqttSensorInput
from service.sensor_inputs.opcua.OpcuaSensorConnection import OpcuaSensorConnection
from service.sensor_inputs.opcua.OpcuaSensorInput import OpcuaSensorInput
from service.specialized_databases.DatabasePersistenceServiceContainer import (
    DatabasePersistenceServiceContainer,
)
from service.specialized_databases.timeseries.influx_db.InfluxDbPersistenceService import (
    InfluxDbPersistenceService,
)

OPCUA_INPUTS = [
    {
        "host": "192.168.1.81",
        "port": 4840,
        "sampling_rate": 1000,  # ms
        "inputs": [
            # HBW:
            {
                "node_id": 'ns=3;s="gtyp_HBW"."Horizontal_Axis"."di_Actual_Position"',
                "id_uri": "www.sintef.no/aas_identifiers/learning_factory/sensors/hbw_actual_pos_horizontal",
            },
            {
                "node_id": 'ns=3;s="gtyp_HBW"."Horizontal_Axis"."di_Target_Position"',
                "id_uri": "www.sintef.no/aas_identifiers/learning_factory/sensors/hbw_target_pos_horizontal",
            },
            {
                "node_id": 'ns=3;s="gtyp_HBW"."Vertical_Axis"."di_Actual_Position"',
                "id_uri": "www.sintef.no/aas_identifiers/learning_factory/sensors/hbw_actual_pos_vertical",
            },
            {
                "node_id": 'ns=3;s="gtyp_HBW"."Vertical_Axis"."di_Target_Position"',
                "id_uri": "www.sintef.no/aas_identifiers/learning_factory/sensors/hbw_target_pos_vertical",
            },
            {
                "node_id": 'ns=3;s="gtyp_HBW"."di_PosBelt_Horizontal"',
                "id_uri": "www.sintef.no/aas_identifiers/learning_factory/sensors/pos_belt_horizontal",
            },
            {
                "node_id": 'ns=3;s="gtyp_HBW"."di_PosBelt_Vertical"',
                "id_uri": "www.sintef.no/aas_identifiers/learning_factory/sensors/pos_belt_vertical",
            },
            {
                "node_id": 'ns=3;s="gtyp_HBW"."di_Offset_Pos_Rack_Vertical"',
                "id_uri": "www.sintef.no/aas_identifiers/learning_factory/sensors/offset_pos_rack_vertical",
            },
            # VGR:
            # {
            #     "node_id": 'ns=3;s="gtyp_VGR"."Horizontal_Axis"."di_Actual_Position"',
            #     "id_uri": 'www.sintef.no/aas_identifiers/learning_factory/sensors/vgr_actual_pos_horizontal'
            # },
            # {
            #     "node_id": 'ns=3;s="gtyp_VGR"."Horizontal_Axis"."di_Target_Position"',
            #     "id_uri": 'www.sintef.no/aas_identifiers/learning_factory/sensors/vgr_target_pos_horizontal'
            # },
        ],
    },
]

MQTT_INPUTS = [
    {
        "host": "192.168.1.81",
        "port": 1883,
        "inputs": [
            {
                "topic": "i/bme680",
                "json_keyword": "t",
                "id_uri": "www.sintef.no/aas_identifiers/learning_factory/sensors/factory_temperature",
            },
            {
                "topic": "i/bme680",
                "json_keyword": "rt",
                "id_uri": "www.sintef.no/aas_identifiers/learning_factory/sensors/factory_temperature_raw",
            },
        ],
    },
]


class ConnectionContainer:
    """
    Holds all current connections to live sensor input
    """

    __instance = None

    @staticmethod
    def instance():
        if ConnectionContainer.__instance is None:
            ConnectionContainer()
        return ConnectionContainer.__instance

    def __init__(self):
        if ConnectionContainer.__instance is not None:
            raise Exception("Singleton instantiated multiple times!")

        ConnectionContainer.__instance = self
        self.mqtt_connections = []
        self.opcua_connections = []

    def initialize_connections(self):

        # TODO: get available URIs etc. from the KG-DT instead of statically defined

        # MQTT
        for connection in MQTT_INPUTS:
            mqtt_inputs = [
                MqttSensorInput(
                    id_uri=input_def["id_uri"],
                    topic=input_def["topic"],
                    json_keyword=input_def["json_keyword"],
                )
                for input_def in connection["inputs"]
            ]

            self.mqtt_connections.append(
                MqttSensorConnection(
                    inputs=mqtt_inputs, host=connection["host"], port=connection["port"]
                )
            )

        # OPC UA
        for connection in OPCUA_INPUTS:
            opcua_inputs = [
                OpcuaSensorInput(
                    id_uri=input_def["id_uri"], node_id=input_def["node_id"]
                )
                for input_def in connection["inputs"]
            ]

            self.opcua_connections.append(
                OpcuaSensorConnection(
                    inputs=opcua_inputs,
                    host=connection["host"],
                    port=connection["port"],
                    sampling_rate=connection["sampling_rate"],
                    only_changes=False,
                )
            )

    def get_all_inputs(self) -> List[SensorInput]:
        """
        :return: All sensor inputs (both MQTT and OPCUA)
        """
        inputs = self.get_mqtt_inputs()
        inputs.extend(self.get_opcua_inputs())
        return inputs

    def register_persistence_handlers(self):
        """
        Registers a persistence handler for every available sensor input.
        The handlers will then write every incoming reading to the timeseries DB
        :return:
        """
        # handler = InfluxDbPersistenceService.instance().write_measurement

        # TODO: individual for inputs...
        ts_service: InfluxDbPersistenceService = DatabasePersistenceServiceContainer.instance().get_persistence_service(
            iri="www.sintef.no/aas_identifiers/learning_factory/databases/learning_factory_influx_db"
        )

        handler = ts_service.write_measurement

        sensor_input: SensorInput
        for sensor_input in self.get_all_inputs():
            sensor_input.register_handler(handler_method=handler)

    def get_opcua_inputs(self):
        inputs = []
        con: SensorConnection
        for con in self.opcua_connections:
            inputs.extend(con.sensor_inputs)

        return inputs

    def get_mqtt_inputs(self):
        inputs = []
        con: SensorConnection
        for con in self.mqtt_connections:
            inputs.extend(con.sensor_inputs)

        return inputs

    def start_connections(self):
        """
        Starts all connections
        :return:
        """
        connection: SensorConnection
        for connection in self.mqtt_connections:
            connection.start_connection()

        for connection in self.opcua_connections:
            connection.start_connection()
