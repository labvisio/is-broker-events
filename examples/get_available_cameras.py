import json
import re
import socket

from is_msgs.common_pb2 import ConsumerList
from is_wire.core import Subscription, Channel

RE_CAMERA_GATEWAY_CONSUMER = re.compile("CameraGateway\\.(\\d+)\\.GetConfig")

if __name__ == "__main__":

    broker_uri = json.load(open("../etc/conf/options.json"))["broker_uri"]
    channel = Channel(broker_uri)
    subscription = Subscription(channel)
    subscription.subscribe("BrokerEvents.Consumers")
    available_cameras = []
    try:
        message = channel.consume(timeout=5)
        consumers = message.unpack(ConsumerList)
        for key, _ in consumers.info.items():
            match = RE_CAMERA_GATEWAY_CONSUMER.match(key)
            if match is None:
                continue
            available_cameras.append(int(match.group(1)))

        print(f'Available Cameras {available_cameras}')
    except socket.timeout:
        print('No reply :(')
   