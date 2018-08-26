#!/usr/bin/env python

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

# kafkaloghandler - logging handler that sends to Kafka

import json
import kafka
import logging
import sys
import time


class KafkaLogHandler(logging.Handler):

    def __init__(self,
                 bootstrap_servers=["localhost:9092"],
                 key="kh",  # kafka key
                 topic="kafkaloghandler",  # kafka topic
                 timeout=10.0,  # kafka connection timeout
                 flatten=3,  # maximum depth of dict flattening
                 blacklist=["_logger"],  # keys excluded from messages
                 ):

        logging.Handler.__init__(self)

        try:
            self.producer = kafka.KafkaProducer(
                bootstrap_servers=bootstrap_servers,

                # Replace unserializable items with repr version.
                # Otherwise, the entire log message is discarded if
                # it contains any unserializable fields
                value_serializer=lambda val: json.dumps(
                    val,
                    separators=(',', ':'),
                    default=lambda o: repr(o),
                    )
                )

        except kafka.errors.KafkaError, e:
            print "Kafka Error: %s" % e
            # die if there's an error
            sys.exit(1)

        self.topic = topic
        self.key = key
        self.flatten = flatten
        self.blacklist = blacklist
        self.timeout = timeout

    def _flatten(self, ns, toflatten, maxdepth):
        """ flatten dicts creating a key_subkey_subsubkey_... hierarchy """

        # avoid recursivly flattening forever
        if maxdepth < 1:
            return toflatten

        flattened = {}

        for k, v in toflatten.iteritems():

            prefix = "%s_%s" % (ns, k)

            if isinstance(v, dict):
                flattened.update(self._flatten(prefix, v, maxdepth-1))
            else:
                flattened[prefix] = v

        return flattened

    def emit(self, record):

        recvars = {}

        for k, v in vars(record).iteritems():
            # skip items in blacklist
            if k in self.blacklist:
                continue

            # flatten any sub-dicts down
            if self.flatten and isinstance(v, dict):
                recvars.update(self._flatten(k, v, self.flatten))
                continue

            recvars[k] = v

        self.producer.send(self.topic, key=self.key, value=recvars)

    def flush(self):
        self.producer.flush(self.timeout)

    def close(self):
        self.producer.close(self.timeout)


if __name__ == '__main__':

    logger = logging.getLogger(__name__)
    logger.handlers = []

    logger.setLevel(logging.INFO)

    kh = KafkaLogHandler(
            bootstrap_servers=["test-kafka:9092"],
            topic="testtopic",
            )

    logger.addHandler(kh)

    logger.error('Error message')

    extra_data = {
      "key1": "value1",
      "key2": "value2",
    }

    logger.info('Info message with extra data', extra=extra_data)

    index = 0
    while True:
        logger.info('Info message - loop count: %s' % index)
        index += 1
        time.sleep(10)
