import re
from is_msgs.common_pb2 import ConsumerList
from is_wire.core import Subscription, Channel
import json

RE_CAMERA_GATEWAY_CONSUMER = re.compile("CameraGateway\\.(\\d+)\\.GetConfig")

if __name__ == "__main__":

    broker_uri = json.load(open("../etc/conf/options.json"))["broker_uri"]
    channel = Channel(broker_uri)
    subscription = Subscription(channel)
    subscription.subscribe("BrokerEvents.Consumers")
    available_cameras = []
    message = channel.consume()
    consumers = message.unpack(ConsumerList)

    for key, _ in consumers.info.items():
        match = RE_CAMERA_GATEWAY_CONSUMER.match(key)
        if match is None:
            continue
        available_cameras.append(int(match.group(1)))
        available_cameras.sort()

        new_cameras = list(set(available_cameras))
        cameras = list(available_cameras)

    print(f'Avalible Cameras {cameras}')
