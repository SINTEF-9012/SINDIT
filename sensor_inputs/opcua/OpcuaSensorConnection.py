import threading
import asyncio
import time
from typing import List
import asyncua.sync
import asyncio.exceptions

from sensor_inputs.SensorConnection import SensorConnection
from sensor_inputs.SensorInput import SensorInput
from sensor_inputs.opcua.OpcuaSensorInput import OpcuaSensorInput

RECONNECT_DURATION = 10  # time to wait before trying to reconnect (in s)
CONNECTION_CHECK_INTERVAL = 10  # time to wait between checking the connection
KEEPALIVE_SUBSCRIPTION_SAMPLING_RATE = 1000  # sampling rate for keepalive subscriptions

class OpcuaSensorConnection(SensorConnection):
    """
    Connection to one OPCUA broker. One or several sensor inputs can be available via one connection over different
    nodes.
    """

    def __init__(self, inputs: List[SensorInput], host, port=4840, sampling_rate=500, only_changes=False):
        """
        Creates a new OPCUA connection
        :param inputs: single inputs (nodes) available over this connection. Must not be empty!
        :param host:
        :param port:
        :param sampling_rate: The rate in which all sensors from this connection are sampled (in ms)
        :param only_changes: Whether the reading handlers should be only triggered when the sensor reading has actually
        changed. Otherwise, a new value will be handled every period.
        """
        super().__init__(inputs)
        self.host = host
        self.port = port
        self.sampling_rate = sampling_rate  # could be changed later to allow individual rates for each sensor
        self.only_changes = only_changes

        self.__opcua_client = None
        self.__nodes: List[asyncua.sync.SyncNode] = []
        self.__asyncua_treadloop = asyncua.sync.ThreadLoop()

        # Separate thread, as the library does not seem to be able to start a non-blocking subscription
        if self.only_changes:
            self.opcua_connector_thread = threading.Thread(target=self.opcua_connection_thread_subscription_based)
        else:
            self.opcua_connector_thread = threading.Thread(target=self.opcua_connection_thread_polling_based)

    # Override:
    def start_connection(self):
        self.opcua_connector_thread.start()

    def opcua_connection_thread_subscription_based(self):
        """
        Main OPCUA thread based on the subscription API. Only samples data changes, not handling every period

        TODO: currently, the subscription does not work anymore when restoring after a temporary disconnect.
        Use the polling-based variant instead for a reliable connection!
        :return:
        """
        self.__asyncua_treadloop.start()

        # Try to initialize the connection
        # Once it was started once, it can be reused even after losing the connection for some period
        self.__start_connection()

        subscription = None

        # Outer loop for restoring the whole connection after a timeout
        while True:
            try:
                self.__opcua_client.connect()
                self.__load_opcua_nodes()

                # Create subscription (for all nodes):
                if subscription is None:
                    subscription = self.__opcua_client.create_subscription(self.sampling_rate, handler=self)
                    subscription.subscribe_data_change(self.__nodes)

                print("OPCUA connection active: "
                      f"Host: {self.host}, port: {self.port}.")

                # Continuously test the connection. Otherwise, lost connections do not seem to lead to an exception
                while True:
                    time.sleep(CONNECTION_CHECK_INTERVAL)
                    # 'i=84' is the root node that should always exist. Just for checking the connection
                    # self.__opcua_client.get_node('i=84')
                    self.__nodes[0].read_value()
                    # self.__nodes[0].read_data_value()

            except asyncio.exceptions.TimeoutError:
                print("OPCUA connection timeout."
                      f"Host: {self.host}, port: {self.port}. Trying to reconnect in {RECONNECT_DURATION} s ...")

                time.sleep(RECONNECT_DURATION)

    def opcua_connection_thread_polling_based(self):
        """
        Main OPCUA thread based on the subscription API. Only samples data changes, not handling every period
        :return:
        """
        self.__asyncua_treadloop.start()

        # Try to initialize the connection
        # Once it was started once, it can be reused even after losing the connection for some period
        self.__start_connection()

        # Outer loop for restoring the whole connection after a timeout
        while True:
            try:

                self.__opcua_client.connect()
                self.__load_opcua_nodes()

                # # Create subscription to avoid asyncua.sync.ThreadLoopNotRunning exceptions:
                subscription = self.__opcua_client.create_subscription(KEEPALIVE_SUBSCRIPTION_SAMPLING_RATE,
                                                                       handler=self)
                # Subscribe to one existing node.
                # This subscription keeps the connection alive, even if the actual sensor reading happens via
                # polling
                subscription.subscribe_data_change(self.__nodes[0])

                print("OPCUA connection active: "
                      f"Host: {self.host}, port: {self.port}.")

                # Continuously polling the sensor readings:
                while True:
                    node: asyncua.sync.SyncNode
                    for node in self.__nodes:
                        val = node.read_value()
                        data = node.read_data_value()

                        sensor_input: OpcuaSensorInput
                        for sensor_input in self.sensor_inputs:
                            sensor_input.handle_reading_if_belonging(
                                node_id=str(node),
                                reading_time=data.SourceTimestamp,
                                value=val
                            )

                    time.sleep(self.sampling_rate / 1000)

            except asyncio.exceptions.TimeoutError:
                print("OPCUA connection timeout."
                      f"Host: {self.host}, port: {self.port}. Trying to reconnect in {RECONNECT_DURATION} s ...")
                time.sleep(RECONNECT_DURATION)

    def __start_connection(self):
        """
        Try to initialize the OPC UA connection
        Once it was started once, it can be reused even after losing the connection for some period.
        Blocking until the connection is successfull!
        :return:
        """
        while self.__opcua_client is None:
            try:
                self.__opcua_client = asyncua.sync.Client(url=f"opc.tcp://{self.host}:{self.port}",
                                                          tloop=self.__asyncua_treadloop)
            except asyncio.exceptions.TimeoutError:
                print("OPCUA connection timeout while initializing the connection. "
                      f"Host: {self.host}, port: {self.port}. Retrying in {RECONNECT_DURATION} s ...")
                time.sleep(RECONNECT_DURATION)

    def __load_opcua_nodes(self):
        """
        Loads all specified nodes with the currently active connection
        :return:
        """
        sensor_input: OpcuaSensorInput
        for sensor_input in self.sensor_inputs:
            self.__nodes.append(self.__opcua_client.get_node(sensor_input.node_id))

        if len(self.__nodes) < 1:
            raise RuntimeError("Running OPCUA connection without nodes")

    def datachange_notification(self, node: asyncua.Node, val, data):
        """
        Callback for asyncua Subscriptions.
        This method will be called when the Client received a data change message from the Server.
        Class instance with event methods (see `SubHandler` base class for details).
        """
        # Handle, if subscriptions are actually used (datachange-mode):
        if self.only_changes:

            sensor_input: OpcuaSensorInput
            for sensor_input in self.sensor_inputs:
                sensor_input.handle_reading_if_belonging(
                    node_id=str(node),
                    reading_time=data.monitored_item.Value.SourceTimestamp,
                    value=val
                )
