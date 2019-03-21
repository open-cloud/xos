# Copyright 2018-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" XOSKafkaProducer """

import confluent_kafka

from xosconfig import Config
from multistructlog import create_logger

log = None
kafka_producer = None


class XOSKafkaProducer:
    """ XOSKafkaProducer
        Wrapper to share Kafka Producer connection
    """

    @staticmethod
    def init():

        global log
        global kafka_producer

        if not log:
            log = create_logger(Config().get("logging"))

        if kafka_producer:
            raise Exception("XOSKafkaProducer already initialized")

        else:
            log.info(
                "Connecting to Kafka with bootstrap servers: %s"
                % Config.get("kafka_bootstrap_servers")
            )

            try:
                producer_config = {
                    "bootstrap.servers": ",".join(Config.get("kafka_bootstrap_servers"))
                }

                kafka_producer = confluent_kafka.Producer(**producer_config)

                log.info("Connected to Kafka: %s" % kafka_producer)

            except confluent_kafka.KafkaError as e:
                log.exception("Kafka Error: %s" % e)

    @classmethod
    def produce(cls, topic, key, value):

        try:
            kafka_producer.produce(
                topic, value, key, callback=cls._kafka_delivery_callback
            )

            # see https://github.com/confluentinc/confluent-kafka-python/issues/16
            kafka_producer.poll(0)

        except confluent_kafka.KafkaError as err:
            log.exception("Kafka Error", err)

    def __del__(self):
        if kafka_producer is not None:
            kafka_producer.flush()

    @staticmethod
    def _kafka_delivery_callback(err, msg):
        if err:
            log.error("Message failed delivery: %s" % err)
        else:
            pass
