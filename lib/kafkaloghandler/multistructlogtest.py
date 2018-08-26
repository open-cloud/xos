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

import multistructlog
import time

# config of logging
logconfig = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler"
            },
        "kafka": {
            "class": "kafkaloghandler.kafkaloghandler.KafkaLogHandler",
            "bootstrap_servers": ["test-kafka:9092"],
            "topic": "testtopic"
            },
        },

    "loggers": {
        "multistructlog": {
            "handlers": ["console", "kafka"],
            "level": "DEBUG"
        }
    },
}

logger = multistructlog.create_logger(logconfig)

logger.error('Test error message')

extra_data = {
  "key1": "value1",
  "key2": "value2",
}

logger.info('Test info message with extra data', extra=extra_data)

index = 0
while True:
    logger.info('Info message - loop count: %s' % index)
    index += 1
    time.sleep(10)
