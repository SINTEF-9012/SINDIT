import threading
import asyncio
import time
from typing import List
import asyncua.sync
import asyncio.exceptions
from service.runtime_connections.RuntimeConnection import RuntimeConnection

from service.runtime_connections.TimeseriesInput import TimeseriesInput
from service.runtime_connections.opcua.OpcuaTimeseriesInput import OpcuaTimeseriesInput

RECONNECT_DURATION = 10  # time to wait before trying to reconnect (in s)
CONNECTION_CHECK_INTERVAL = 10  # time to wait between checking the connection
KEEPALIVE_SUBSCRIPTION_SAMPLING_RATE = 1000  # sampling rate for keepalive subscriptions

# The rate in which all sensors from this connection are sampled (in ms)
SAMPLING_RATE = 500  # ms
# TODO: integrate this into the timeseries nodes (or at least the connection nodes)!

# Whether the reading handlers should be only triggered when the timeseries reading has actually changed.
# Otherwise, a new value will be handled every period.
ONLY_CHANGES = False


class OpcuaRuntimeConnection(RuntimeConnection):
    """
    Connection to one OPCUA broker. One or several timeseries inputs can be available via one connection over different
    nodes.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.sampling_rate = SAMPLING_RATE

        self._opcua_client = None
        self._nodes: List[asyncua.sync.SyncNode] = []
        self._asyncua_treadloop = asyncua.sync.ThreadLoop()

        # Separate thread, as the library does not seem to be able to start a non-blocking subscription
        if ONLY_CHANGES:
            self.opcua_connector_thread = threading.Thread(
                target=self.opcua_connection_thread_subscription_based
            )
        else:
            self.opcua_connector_thread = threading.Thread(
                target=self.opcua_connection_thread_polling_based
            )

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
        self._asyncua_treadloop.start()

        # Try to initialize the connection
        # Once it was started once, it can be reused even after losing the connection for some period
        self.__start_connection()

        subscription = None

        # Outer loop for restoring the whole connection after a timeout
        while True:
            try:
                self._opcua_client.connect()
                self.__load_opcua_nodes()

                # Create subscription (for all nodes):
                if subscription is None:
                    subscription = self._opcua_client.create_subscription(
                        self.sampling_rate, handler=self
                    )
                    subscription.subscribe_data_change(self._nodes)

                print(
                    "OPCUA connection active: "
                    f"Host: {self.host}, port: {self.port}. Subscribing to nodes..."
                )

                # Continuously test the connection. Otherwise, lost connections do not seem to lead to an exception
                while True:
                    time.sleep(CONNECTION_CHECK_INTERVAL)
                    # 'i=84' is the root node that should always exist. Just for checking the connection
                    # self.__opcua_client.get_node('i=84')
                    self._nodes[0].read_value()
                    # self.__nodes[0].read_data_value()

            except asyncio.exceptions.TimeoutError:
                print(
                    "OPCUA connection timeout."
                    f"Host: {self.host}, port: {self.port}. Trying to reconnect in {RECONNECT_DURATION} s ..."
                )

                time.sleep(RECONNECT_DURATION)

    def opcua_connection_thread_polling_based(self):
        """
        Main OPCUA thread based on the subscription API. Only samples data changes, not handling every period
        :return:
        """
        self._asyncua_treadloop.start()

        # Try to initialize the connection
        # Once it was started once, it can be reused even after losing the connection for some period
        self.__start_connection()

        # Outer loop for restoring the whole connection after a timeout
        while True:
            try:

                self._opcua_client.connect()
                self.__load_opcua_nodes()

                # # Create subscription to avoid asyncua.sync.ThreadLoopNotRunning exceptions:
                subscription = self._opcua_client.create_subscription(
                    KEEPALIVE_SUBSCRIPTION_SAMPLING_RATE, handler=self
                )
                # Subscribe to one existing node.
                # This subscription keeps the connection alive, even if the actual sensor reading happens via
                # polling
                subscription.subscribe_data_change(self._nodes[0])

                print(
                    "OPCUA connection active: " f"Host: {self.host}, port: {self.port}."
                )

                # Continuously polling the sensor readings:
                while True:
                    node: asyncua.sync.SyncNode
                    for node in self._nodes:
                        val = node.read_value()
                        data = node.read_data_value()

                        timeseries_input: OpcuaTimeseriesInput
                        for timeseries_input in self.timeseries_inputs:
                            timeseries_input.handle_reading_if_belonging(
                                node_id=str(node),
                                reading_time=data.SourceTimestamp,
                                value=val,
                            )

                    time.sleep(self.sampling_rate / 1000)

            except asyncio.exceptions.TimeoutError:
                print(
                    "OPCUA connection timeout."
                    f"Host: {self.host}, port: {self.port}. Trying to reconnect in {RECONNECT_DURATION} s ..."
                )
                time.sleep(RECONNECT_DURATION)
            except OSError:
                print(
                    "OPCUA connection: OSError. "
                    f"Host: {self.host}, port: {self.port}. Trying to reconnect in {RECONNECT_DURATION} s ..."
                )
                time.sleep(RECONNECT_DURATION)

    def __start_connection(self):
        """
        Try to initialize the OPC UA connection
        Once it was started once, it can be reused even after losing the connection for some period.
        Blocking until the connection is successfull!
        :return:
        """
        while self._opcua_client is None:
            try:
                self._opcua_client = asyncua.sync.Client(
                    url=f"opc.tcp://{self.host}:{self.port}",
                    tloop=self._asyncua_treadloop,
                )
            except asyncio.exceptions.TimeoutError:
                print(
                    "OPCUA connection timeout while initializing the connection. "
                    f"Host: {self.host}, port: {self.port}. Retrying in {RECONNECT_DURATION} s ..."
                )
                time.sleep(RECONNECT_DURATION)

    def __load_opcua_nodes(self):
        """
        Loads all specified nodes with the currently active connection
        :return:
        """
        timeseries_input: OpcuaTimeseriesInput
        for timeseries_input in self.timeseries_inputs:
            self._nodes.append(
                self._opcua_client.get_node(timeseries_input.connection_topic)
            )

        if len(self._nodes) < 1:
            raise RuntimeError("Running OPCUA connection without nodes")

    def datachange_notification(self, node: asyncua.Node, val, data):
        """
        Callback for asyncua Subscriptions.
        This method will be called when the Client received a data change message from the Server.
        Class instance with event methods (see `SubHandler` base class for details).
        """
        # Handle, if subscriptions are actually used (datachange-mode):
        if ONLY_CHANGES:

            timeseries_input: OpcuaTimeseriesInput
            for timeseries_input in self.timeseries_inputs:
                timeseries_input.handle_reading_if_belonging(
                    node_id=str(node),
                    reading_time=data.monitored_item.Value.SourceTimestamp,
                    value=val,
                )
