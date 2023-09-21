# Broker Events Service

[![Docker image tag](https://img.shields.io/docker/v/labvisio/is-broker-events?sort=semver&style=flat-square)](https://hub.docker.com/r/labvisio/is-broker-events/tags)
[![Docker image size](https://img.shields.io/docker/image-size/labvisio/is-broker-events?sort=semver&style=flat-square)](https://hub.docker.com/r/labvisio/is-broker-events)
[![Docker pulls](https://img.shields.io/docker/pulls/labvisio/is-broker-events?style=flat-square)](https://hub.docker.com/r/labvisio/is-broker-events)

This service queries the broker management API to get an initial list of all bindings. If the binding is made to a queue and has the source in exchange ``is``, then it means that it is a consumer binding. The bindings are filtered in this way and a consumer list is made using a map between the routing key (topic) and destination. So, we have an initial list of consumers for each topic. After this, it subscribes in the topic `binding.*`, which means that when events of bindings happen (created or deleted), this service receives a message, updates the consumer list and sends a message with topic the `BrokerEvents.Consumers`.

If you want to receive a consumer list for each topic, you can simply subscribe to receive messages with the topic `BrokerEvents.Consumers` and everytime the list is updated, you are going to receive a new message. This is really usefull for some applications as [is-robot-controller](https://github.com/labviros/is-robot-controller), that uses this service to monitor available cameras in the IS architeture. The message with the consumer list is structured as:

```protobuf
message ConsumerInfo {
  // List of consumers.
  repeated string consumers = 2;
}

message ConsumerList {
  // Consumer Information for each topic.
  map<string, ConsumerInfo> info = 1;
}
```

Below is an example of what this message looks like:

```python
>>> from is_msgs.common_pb2 import ConsumerList
>>> from is_wire.core import Channel, Subscription
>>> channel = Channel("amqp://guest:guest@localhost:5672")
>>> subscription = Subscription(channel)
>>> subscription.subscribe(topic="BrokerEvents.Consumers")
>>> message = channel.consume()
>>> message.unpack(ConsumerList)
info {
  key: "#.FrameTransformations"
  value {
    consumers: "is-frame-transformation-759cb6f7fb-46lcl/3D386B9FE96DC3FC"
  }
}
info {
  key: "ArUco.Localization"
  value {
    consumers: "ArUco.Localization"
  }
}
info {
  key: "BrokerEvents"
  value {
    consumers: "BrokerEvents"
  }
}
info {
  key: "BrokerEvents.Consumers"
  value {
    consumers: "is-frame-transformation-759cb6f7fb-46lcl/3D386B9FE96DC3FC"
    consumers: "luke/18EA747B084E4210"
  }
}
info {
  key: "CameraGateway.*.Frame"
  value {
    consumers: "ArUco.Localization"
  }
}
info {
  key: "CameraGateway.0.GetConfig"
  value {
    consumers: "CameraGateway.0.GetConfig"
  }
}
info {
  key: "CameraGateway.0.SetConfig"
  value {
    consumers: "CameraGateway.0.SetConfig"
  }
}
info {
  key: "FrameTransformation.GetCalibration"
  value {
    consumers: "FrameTransformation.GetCalibration"
  }
}
info {
  key: "binding.*"
  value {
    consumers: "BrokerEvents"
  }
}
```

## Configuration

The behavior of the service can be customized by passing a JSON configuration file as the first argument, e.g: `is-broker-events etc/conf/options.json`. The schema for this file can be found in [`is_broker_events/conf/options.proto`](https://github.com/labvisio/is-broker-events/blob/master/is_broker_events/conf/options.proto). An example configuration file can be found in [`etc/conf/options.json`](https://github.com/labvisio/is-broker-events/blob/master/etc/conf/options.json).

## RabbitMQ Event Exchange

The broker is deployed using a plugin known as the [RabbitMQ Event Exchange](https://github.com/rabbitmq/rabbitmq-server/tree/main/deps/rabbitmq_event_exchange). This plugin serves as an interface to the internal event system of RabbitMQ, allowing clients to consume these events as messages. It's useful when you need to monitor specific events, such as the creation and deletion of queues, exchanges, bindings, users, connections, and channels.

This plugin declares a topic exchange named `amq.rabbitmq.event` within the default virtual host. All events are dispatched to this exchange with routing keys like `exchange.created`, `binding.deleted` and so on. Consequently, you can selectively subscribe to only the events that are of interest to you.

In the context of deploying the broker within the IS architecture, certain configurations are put in place. One of these configurations involves establishing a binding between the `amq.rabbitmq.event` exchange and the `is` exchange. Consequently, any event that occurs within the broker becomes available as a message that can be consumed by any client. Below you can see an example of how such a definition is defined.

```json
{
    "vhosts": [
    {
        "name": "/"
    }
    ],
    "exchanges": [
    {
        "name": "is",
        "vhost": "/",
        "type": "topic",
        "durable": false,
        "auto_delete": false,
        "internal": false,
        "arguments": {}
    },
    {
        "name": "amq.rabbitmq.event",
        "vhost": "/",
        "type": "topic",
        "durable": true,
        "auto_delete": false,
        "internal": true,
        "arguments": {}
    }
    ],
    "bindings": [
    {
        "source": "amq.rabbitmq.event",
        "destination": "is",
        "destination_type": "exchange",
        "routing_key": "#",
        "vhost": "/",
        "arguments": {}
    }
    ]
}
```

This setup offers great flexibility and utility within the IS architecture, as clients can subscribe to specific event types of interest to them, enabling real-time monitoring, analysis, and response to critical events within the broker's operation. It serves as a vital component for maintaining visibility and control over the behavior and state of the broker, supporting various use cases and applications within the IS environment.
