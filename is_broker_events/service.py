import sys
import time
from urllib.parse import urljoin

import requests
from google.protobuf.json_format import Parse, ParseError
from is_msgs.common_pb2 import ConsumerList
from is_wire.core import Channel, Message, Subscription
from requests.exceptions import ConnectionError as HTTPConnectionError
from requests.exceptions import HTTPError, JSONDecodeError, Timeout

from is_broker_events.conf.options_pb2 import BrokerEventsOptions
from is_broker_events.logger import Logger


class BrokerEvents(object):
    def __init__(self, options: BrokerEventsOptions) -> None:
        self.log = Logger(name="BrokerEvents")
        self.log.debug("Connecting to RabbitMQ broker at: '{}'", options.broker_uri)

        self.channel = Channel(uri=options.broker_uri, exchange="is")
        self.subscription = Subscription(channel=self.channel, name="BrokerEvents")
        self.subscription.subscribe(topic="binding.*")

        self.consumers = self.query_consumers_http(
            management_uri=options.management_uri
        )
        self.log.debug("Got list of consumers at: '{}'", options.management_uri)

    def run(self) -> None:
        while True:
            msg = self.channel.consume()
            self.log.debug("topic='{}' metadata={}", msg.topic, msg.metadata)

            if (
                msg.metadata["destination_kind"] != "queue"
                or msg.metadata["source_name"] != "is"
            ):
                continue

            event = msg.topic.split(".")[-1]
            topic = msg.metadata["routing_key"]
            queue = msg.metadata["destination_name"]

            if event == "created":
                self.consumers.info[topic].consumers.append(queue)
            elif event == "deleted":
                self.consumers.info[topic].consumers.remove(queue)
                if len(self.consumers.info[topic].consumers) == 0:
                    del self.consumers.info[topic]

            self.log.info("event='{}' topic='{}' queue='{}'", event, topic, queue)

            self.channel.publish(
                Message(content=self.consumers),
                topic="BrokerEvents.Consumers",
            )

    def query_consumers_http(
        self, management_uri: str, max_retries: int = 5, timeout: int = 5
    ) -> ConsumerList:
        url = urljoin(management_uri, "/api/bindings")
        success = False
        for _ in range(max_retries):
            try:
                response = requests.get(url=url, timeout=timeout)
                # raise expection if failed to get list of bindings
                # in management API at RabbitMQ Broker
                response.raise_for_status()
                bindings = response.json()
                success = True
            except (HTTPConnectionError, HTTPError, JSONDecodeError, Timeout) as ex:
                self.log.warn("Could not fetch list of binding, why='{}'", ex)
                time.sleep(5)
        if not success:
            self.log.critical(
                "Could not fetch list of binding, reached max_retries={}", max_retries
            )
        bindings = [
            b
            for b in bindings
            if b["destination_type"] == "queue" and b["source"] == "is"
        ]
        consumers = ConsumerList()
        for binding in bindings:
            consumers.info[binding["routing_key"]].consumers.append(
                binding["destination"]
            )
        return consumers


def load_json(  # type: ignore[return]
    logger: Logger,
    path: str = "/etc/is-broker-events/options.json",
) -> BrokerEventsOptions:
    try:
        with open(file=path, mode="r", encoding="utf-8") as file:
            try:
                options = Parse(file.read(), BrokerEventsOptions())
                logger.info("BrokerEventsOptions: \n{}", options)
                return options
            except ParseError as ex:
                logger.critical("Unable to load options from '{}'. \n{}", path, ex)
    except FileNotFoundError:
        logger.critical("Unable to open file '{}'", path)


def main() -> None:
    if len(sys.argv) > 1:
        options_filename = sys.argv[1]
    else:
        options_filename = "/etc/is-broker-events/options.json"
    logger = Logger(name="BrokerEvents")
    options = load_json(
        logger=logger,
        path=options_filename,
    )
    service = BrokerEvents(options=options)
    service.run()


if __name__ == "__main__":
    main()
