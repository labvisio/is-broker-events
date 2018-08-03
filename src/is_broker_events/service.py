from is_wire.core import Channel, Subscription, Logger, Message
from is_msgs.common_pb2 import ConsumerList
import requests
import json
import argparse
import logging


class BrokerEvents(object):
    def __init__(self, broker_uri, management_uri, log_level):
        self.log = Logger(name="BrokerEvents", level=log_level)

        self.log.debug("broker_uri='{}'", broker_uri)
        self.channel = Channel(broker_uri)
        self.subscription = Subscription(self.channel)
        self.subscription.subscribe(topic="binding.*")

        self.log.debug("management_uri='{}'", management_uri)
        self.consumers = self.query_consumers_http(management_uri)

    def run(self):
        while True:
            msg = self.channel.consume()
            self.log.debug("topic='{}' metadata={}", msg.topic, msg.metadata)

            if msg.metadata["destination_kind"] != "queue" or \
               msg.metadata["source_name"] != "is":
                continue

            event = msg.topic.split('.')[-1]
            topic = msg.metadata["routing_key"]
            queue = msg.metadata["destination_name"]

            if event == "created":
                self.consumers.info[topic].consumers.append(queue)
            elif event == "deleted":
                self.consumers.info[topic].consumers.remove(queue)

            self.log.info("event='{}' topic='{}' queue='{}'", event, topic,
                          queue)

            self.channel.publish(
                Message(content=self.consumers),
                topic="BrokerEvents.Consumers",
            )

    @staticmethod
    def query_consumers_http(management_uri):
        reply = requests.get(management_uri + "/api/bindings")
        if reply.status_code != 200:
            why = "Failed to query management API, code={}".format(
                reply.status_code)
            raise RuntimeError(why)

        bindings = reply.json()
        bindings = [
            b for b in bindings
            if b["destination_type"] == "queue" and b["source"] == "is"
        ]

        consumers = ConsumerList()
        for b in bindings:
            consumers.info[b["routing_key"]].consumers.append(b["destination"])
        return consumers


def main():
    log = Logger(name="Parser")
    parser = argparse.ArgumentParser(description='Broker events service')
    parser.add_argument(
        '--config',
        dest='config',
        type=str,
        default="config.json",
        help='path to configuration file')

    args = parser.parse_args()
    with open(args.config) as f:
        config = json.load(f)
        log.info("{}", config)

    service = BrokerEvents(
        broker_uri=config["broker_uri"],
        management_uri=config["management_uri"],
        log_level=logging.getLevelName(config["log_level"]),
    )

    service.run()


if __name__ == '__main__':
    main()
