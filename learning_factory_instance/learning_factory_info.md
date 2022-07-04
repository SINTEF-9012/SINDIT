# Fischertechnik Learning Factory

## Input sources:

### Data and inputs that are not (yet) included:

#### MQTT
Available data can be introspected with a tool like "MQTT explorer".
Some description is available here: https://github.com/fischertechnik/txt_training_factory/blob/master/TxtSmartFactoryLib/doc/MqttInterface.md

Not that here, only input sources are considered. Look below for MQTT-actuators.

##### i/cam
Video input is not intended to be included due to privacy

##### i/alert
Alert messages.
Not included since this does not fit together well with timeseries data formats.

##### i/broadcast
Only documentation available: "Broadcast: internal usage"

##### fl/ssc/joy
Joysticks. Does not seem to be actually available.

##### f/i/nfc/ds
State NFC Device (VGR)

Could be interesting, but hard to generalize

Examples:

```
{
	"history" : null,
	"ts" : "2022-07-01T11:04:25.514Z",
	"workpiece" : null
}
```

```
{
	"history" : 
	[
		{
			"code" : 100,
			"ts" : "2022-06-29T10:42:45.833Z"
		},
		{
			"code" : 200,
			"ts" : "2022-06-29T10:43:13.092Z"
		},
		{
			"code" : 300,
			"ts" : "2022-06-29T10:44:07.640Z"
		},
		{
			"code" : 400,
			"ts" : "2022-07-01T10:57:26.611Z"
		},
		{
			"code" : 500,
			"ts" : "2022-07-01T10:58:13.076Z"
		},
		{
			"code" : 600,
			"ts" : "2022-07-01T10:58:39.687Z"
		},
		{
			"code" : 700,
			"ts" : "2022-07-01T10:58:51.351Z"
		},
		{
			"code" : 800,
			"ts" : "2022-07-01T10:59:09.883Z"
		}
	],
	"ts" : "2022-07-01T10:59:31.467Z",
	"workpiece" : 
	{
		"id" : "046ca942ef6c80",
		"state" : "PROCESSED",
		"type" : "BLUE"
	}
}
```

##### fl/i/nfc/ds
Seems to be a copy from f/i/nfc/ds

##### f/i/stock
Stock of the HBW

Could be interesting, but hard to generalize

Example:

```
{"ts":"2022-07-01T11:11:15.332Z","stockItems":[{"workpiece":{"id":"0","state":"","type":""},"location":"A1"},{"workpiece":{"id":"0462aa42ef6c80","state":"RAW","type":"RED"},"location":"A2"},{"workpiece":{"id":"0","state":"","type":""},"location":"A3"},{"workpiece":{"id":"04cbab42ef6c80","state":"RAW","type":"WHITE"},"location":"B1"},{"workpiece":{"id":"0457ab42ef6c80","state":"RAW","type":"WHITE"},"location":"B2"},{"workpiece":{"id":"048faa42ef6c80","state":"RAW","type":"RED"},"location":"B3"},{"workpiece":{"id":"0415ab42ef6c80","state":"RAW","type":"WHITE"},"location":"C1"},{"workpiece":{"id":"046da942ef6c80","state":"RAW","type":"BLUE"},"location":"C2"},{"workpiece":{"id":"044baa42ef6c80","state":"RAW","type":"RED"},"location":"C3"}]}
```

##### f/i/order

State of the current order (IN_PROCESS, SHIPPED)

Could be interesting, but hard to generalize

Example:

```
{"ts":"2022-07-01T10:59:45.758Z","state":"SHIPPED","type":"BLUE"}
```

##### fl/vgr/do
VGR Trigger

Does not seem to actually exist

##### f/i/state/"*\vgr" -> target
Other stations then vgr do not seem to have this property

##### f/i/state/* -> active
If the station is active

Could be integrated when supporting boolean timeseries? Or convert bool to 0 and 1?

##### f/i/state/* -> description
Seems to be empty all the time

##### f/i/state/* -> station
Redundant, as this is part of the path

#### OPC UA

#### Files

- no files are included yet

## Actuators

### Available actuators that are not (yet) included:

#### MQTT

##### c/*
Config Rate settings. Not periodically published.
E.g. for setting the fps rate of the camera or the period in which the environment sensor data shall be published.

Could be used later with a action searching for sequences where the publish rate is wrong -> automatically adjust that

##### o/ptu
Control Buttons Pan-Tilt-Unit. Control the physical positioning of the camera

##### fl/o/state/ack (description says: f/o/state/ack)
Quit Button

##### f/o/order
Order Workpiece Buttons

Example command:
> {"type":"BLUE","ts":"2022-07-01T09:32:10.741Z"}

##### f/o/nfc/ds
Action Buttons NFC Module

##### fl/o/nfc/ds
Not documented

Example command:
> {"ts":"2022-07-01T09:31:39.874Z","cmd":"read_uid"}