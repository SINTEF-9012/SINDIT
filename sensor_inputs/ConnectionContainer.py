from sensor_inputs.SensorConnection import SensorConnection
from sensor_inputs.mqtt.MqttSensorConnection import MqttSensorConnection
from sensor_inputs.mqtt.MqttSensorInput import MqttSensorInput
from sensor_inputs.opcua.OpcuaSensorConnection import OpcuaSensorConnection
from sensor_inputs.opcua.OpcuaSensorInput import OpcuaSensorInput

OPCUA_INPUTS = [
    {
        "host": "192.168.1.81",
        "port": 4840,
        "sampling_rate": 1000,  # ms
        "inputs": [
            {
                "node_id": 'ns=3;s="gtyp_HBW"."Horizontal_Axis"."di_Actual_Position"',
                "id_uri": 'www.sintef.no/asset_identifiers/fischertechnik_learning_factory/sensor_inputs/'
                       'HBW/Horizontal_Axis/di_Actual_Position'
            },
            {
                "node_id": 'ns=3;s="gtyp_HBW"."Horizontal_Axis"."di_Target_Position"',
                "id_uri": 'www.sintef.no/asset_identifiers/fischertechnik_learning_factory/sensor_inputs/'
                       'HBW/Horizontal_Axis/di_Target_Position'
            },
            {
                "node_id": 'ns=3;s="gtyp_HBW"."Vertical_Axis"."di_Actual_Position"',
                "id_uri": 'www.sintef.no/asset_identifiers/fischertechnik_learning_factory/sensor_inputs/'
                       'HBW/Vertical_Axis/di_Actual_Position'
            },
            {
                "node_id": 'ns=3;s="gtyp_HBW"."Vertical_Axis"."di_Target_Position"',
                "id_uri": 'www.sintef.no/asset_identifiers/fischertechnik_learning_factory/sensor_inputs/'
                       'HBW/Vertical_Axis/di_Target_Position'
            },
            {
                "node_id": 'ns=3;s="gtyp_HBW"."di_PosBelt_Horizontal"',
                "id_uri": 'www.sintef.no/asset_identifiers/fischertechnik_learning_factory/sensor_inputs/'
                       'HBW/di_PosBelt_Horizontal'
            },
            {
                "node_id": 'ns=3;s="gtyp_HBW"."di_PosBelt_Vertical"',
                "id_uri": 'www.sintef.no/asset_identifiers/fischertechnik_learning_factory/sensor_inputs/'
                       'HBW/di_PosBelt_Vertical'
            },
            {
                "node_id": 'ns=3;s="gtyp_HBW"."di_Offset_Pos_Rack_Vertical"',
                "id_uri": 'www.sintef.no/asset_identifiers/fischertechnik_learning_factory/sensor_inputs/'
                       'HBW/di_Offset_Pos_Rack_Vertical'
            }
        ]
    },
]

MQTT_INPUTS = [
    {
        "host": "192.168.1.81",
        "port": 1883,
        "inputs": [
            {
                "topic": 'i/bme680',
                "json_keyword": 't',
                "id_uri": 'www.sintef.no/asset_identifiers/fischertechnik_learning_factory/sensor_inputs/'
                       'BME680/temperature'
            },
            {
                "topic": 'i/bme680',
                "json_keyword": 'rt',
                "id_uri": 'www.sintef.no/asset_identifiers/fischertechnik_learning_factory/sensor_inputs/'
                       'BME680/temperature_raw'
            },
        ]
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
        pass

        # MQTT
        for connection in MQTT_INPUTS:
            mqtt_inputs = [MqttSensorInput(id_uri=input_def["id_uri"],
                                           topic=input_def["topic"],
                                           json_keyword=input_def["json_keyword"])
                           for input_def in connection["inputs"]]

            self.mqtt_connections.append(
                MqttSensorConnection(
                    inputs=mqtt_inputs,
                    host=connection["host"],
                    port=connection["port"]
                )
            )

        # OPC UA
        for connection in OPCUA_INPUTS:
            opcua_inputs = [OpcuaSensorInput(id_uri=input_def["id_uri"],
                                             node_id=input_def["node_id"])
                            for input_def in connection["inputs"]]

            self.opcua_connections.append(
                OpcuaSensorConnection(
                    inputs=opcua_inputs,
                    host=connection["host"],
                    port=connection["port"],
                    sampling_rate=connection["sampling_rate"],
                    only_changes=False
                )
            )

    def get_all_inputs(self):
        """
        :return: All sensor inputs (both MQTT and OPCUA)
        """
        return self.get_opcua_inputs().extend(self.get_mqtt_inputs())

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
