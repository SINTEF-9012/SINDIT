from typing import List

import paho.mqtt.client as mqtt
from service.runtime_connections.RuntimeConnection import RuntimeConnection

from service.runtime_connections.TimeseriesInput import TimeseriesInput
from service.runtime_connections.mqtt.MqttTimeseriesInput import MqttTimeseriesInput


class MqttRuntimeConnection(RuntimeConnection):
    """
    Connection to one MQTT broker. One or several timeseries inputs can be available via one connection over different
    topics.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mqtt_client = mqtt.Client()

    # Override:
    def start_connection(self):

        self.mqtt_client.on_connect_fail = self.__on_connect_fail
        self.mqtt_client.on_message = self.__on_message
        self.mqtt_client.on_disconnect = self.__on_disconnect
        self.mqtt_client.on_connect = self.__on_connect

        # Async variant so that the library handles reconnecting on its own (even at startup)
        self.mqtt_client.connect_async(host=self.host, port=self.port, keepalive=60)

        self.mqtt_client.loop_start()

    def __on_connect(self, client, userdata, flags, reason_code):
        """
        Called when the connection is established.
        Subscribe to topics here, so that they will be re-subscribed after a reconnect also.
        :param client:
        :param userdata:
        :param flags:
        :param reason_code:
        :return:
        """
        print(
            "MQTT connected. "
            f"Host: {self.host}, port: {self.port}. Subscribing to topics..."
        )

        timeseries_input: MqttTimeseriesInput
        for timeseries_input in self.timeseries_inputs:
            self.mqtt_client.subscribe(timeseries_input.connection_topic, 0)

    def __on_connect_fail(self, client, userdata):
        print(
            f"MQTT connection could not be established: "
            f"Host: {self.host}, port: {self.port}"
        )

    def __on_disconnect(self, client, userdata, reason_code):
        if reason_code != 0:
            print(
                f"Unexpected MQTT disconnection. "
                f"Host: {self.host}, port: {self.port}. Will auto-reconnect"
            )

    def __on_message(self, client, userdata, msg):
        """
        Called whenever a MQTT message is being received (all subscribed topics)
        :param client:
        :param userdata:
        :param msg:
        :return:
        """
        # print(msg.topic + " " + str(msg.payload))
        timeseries_input: MqttTimeseriesInput
        for timeseries_input in self.timeseries_inputs:
            if msg.topic == timeseries_input.connection_topic:
                timeseries_input.handle_raw_reading(msg.payload)
