# Copyright 2017-present Open Networking Foundation
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

import confluent_kafka
import functools
import unittest

from mock import patch, PropertyMock, ANY

import os
import sys
import time

log = None

test_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
sync_lib_dir = os.path.join(test_path, "..", "xossynchronizer")
xos_dir = os.path.join(test_path, "..", "..", "..", "xos")

print os.getcwd()

def config_get_mock(orig, overrides, key):
    if key in overrides:
        return overrides[key]
    else:
        return orig(key)


class FakeKafkaConsumer:
    def __init__(self, values=[]):
        self.values = values

    def subscribe(self, topics):
        pass

    def poll(self, timeout=1.0):
        if self.values:
            return FakeKafkaMessage(self.values.pop())
        # block forever
        time.sleep(1000)


class FakeKafkaMessage:
    """ Works like Message in confluent_kafka
        https://docs.confluent.io/current/clients/confluent-kafka-python/#message
    """

    def __init__(
        self,
        timestamp=None,
        topic="faketopic",
        key="fakekey",
        value="fakevalue",
        error=False,
    ):

        if timestamp is None:
            self.fake_ts_type = confluent_kafka.TIMESTAMP_NOT_AVAILABLE
            self.fake_timestamp = None
        else:
            self.fake_ts_type = confluent_kafka.TIMESTAMP_CREATE_TIME
            self.fake_timestamp = timestamp

        self.fake_topic = topic
        self.fake_key = key
        self.fake_value = value
        self.fake_error = error

    def error(self):
        return self.fake_error

    def timestamp(self):
        return (self.fake_ts_type, self.fake_timestamp)

    def topic(self):
        return self.fake_topic

    def key(self):
        return self.fake_key

    def value(self):
        return self.fake_value


class TestEventEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        global log

        config = os.path.join(test_path, "test_config.yaml")
        from xosconfig import Config

        Config.clear()
        Config.init(config, "synchronizer-config-schema.yaml")

        if not log:
            from multistructlog import create_logger

            log = create_logger(Config().get("logging"))

    def setUp(self):
        global XOSKafkaThread, Config, log

        self.sys_path_save = sys.path
        self.cwd_save = os.getcwd()

        config = os.path.join(test_path, "test_config.yaml")
        from xosconfig import Config

        Config.clear()
        Config.init(config, "synchronizer-config-schema.yaml")

        from xossynchronizer.mock_modelaccessor_build import (
            build_mock_modelaccessor,
        )

        build_mock_modelaccessor(sync_lib_dir, xos_dir, services_dir=None, service_xprotos=[])

        from xossynchronizer.modelaccessor import model_accessor

        # The test config.yaml references files in `test/` so make sure we're in the parent directory of the
        # test directory.
        os.chdir(os.path.join(test_path, ".."))

        from xossynchronizer.event_engine import XOSKafkaThread, XOSEventEngine

        self.event_steps_dir = Config.get("event_steps_dir")
        self.event_engine = XOSEventEngine(model_accessor=model_accessor, log=log)

    def tearDown(self):
        sys.path = self.sys_path_save
        os.chdir(self.cwd_save)

    def test_load_event_step_modules(self):
        self.event_engine.load_event_step_modules(self.event_steps_dir)
        self.assertEqual(len(self.event_engine.event_steps), 1)

    def test_start(self):
        self.event_engine.load_event_step_modules(self.event_steps_dir)

        with patch.object(
            XOSKafkaThread, "create_kafka_consumer"
        ) as create_kafka_consumer, patch.object(
            FakeKafkaConsumer, "subscribe"
        ) as fake_subscribe, patch.object(
            self.event_engine.event_steps[0], "process_event"
        ) as process_event:

            create_kafka_consumer.return_value = FakeKafkaConsumer(
                values=["sampleevent"]
            )
            self.event_engine.start()

            self.assertEqual(len(self.event_engine.threads), 1)

            # Since event_engine.start() launches threads, give them a hundred milliseconds to do something...
            time.sleep(0.1)

            # We should have subscribed to the fake consumer
            fake_subscribe.assert_called_once()

            # The fake consumer will have returned one event
            process_event.assert_called_once()

    def test_start_with_pattern(self):
        self.event_engine.load_event_step_modules(self.event_steps_dir)

        with patch.object(
            XOSKafkaThread, "create_kafka_consumer"
        ) as create_kafka_consumer, patch.object(
            FakeKafkaConsumer, "subscribe"
        ) as fake_subscribe, patch.object(
            self.event_engine.event_steps[0], "process_event"
        ) as process_event, patch.object(
            self.event_engine.event_steps[0], "pattern", new_callable=PropertyMock
        ) as pattern, patch.object(
            self.event_engine.event_steps[0], "topics", new_callable=PropertyMock
        ) as topics:

            pattern.return_value = "somepattern"
            topics.return_value = []

            create_kafka_consumer.return_value = FakeKafkaConsumer(
                values=["sampleevent"]
            )
            self.event_engine.start()

            self.assertEqual(len(self.event_engine.threads), 1)

            # Since event_engine.start() launches threads, give them a hundred milliseconds to do something...
            time.sleep(0.1)

            # We should have subscribed to the fake consumer
            fake_subscribe.assert_called_with("somepattern")

            # The fake consumer will have returned one event
            process_event.assert_called_once()

    def test_start_bad_tech(self):
        """ Set an unknown Technology in the event_step. XOSEventEngine.start() should print an error message and
            not create any threads.
        """

        self.event_engine.load_event_step_modules(self.event_steps_dir)

        with patch.object(
            XOSKafkaThread, "create_kafka_consumer"
        ) as create_kafka_consumer, patch.object(
            log, "error"
        ) as log_error, patch.object(
            self.event_engine.event_steps[0], "technology"
        ) as technology:
            technology.return_value = "not_kafka"
            create_kafka_consumer.return_value = FakeKafkaConsumer()
            self.event_engine.start()

            self.assertEqual(len(self.event_engine.threads), 0)

            log_error.assert_called_with(
                "Unknown technology. Skipping step",
                step="TestEventStep",
                technology=ANY,
            )

    def test_start_bad_no_topics(self):
        """ Set no topics in the event_step. XOSEventEngine.start() will launch a thread, but the thread will fail
            with an exception before calling subscribe.
        """

        self.event_engine.load_event_step_modules(self.event_steps_dir)

        with patch.object(
            XOSKafkaThread, "create_kafka_consumer"
        ) as create_kafka_consumer, patch.object(
            FakeKafkaConsumer, "subscribe"
        ) as fake_subscribe, patch.object(
            self.event_engine.event_steps[0], "topics", new_callable=PropertyMock
        ) as topics:
            topics.return_value = []
            create_kafka_consumer.return_value = FakeKafkaConsumer()
            self.event_engine.start()

            # the thread does get launched, but it will fail with an exception
            self.assertEqual(len(self.event_engine.threads), 1)

            time.sleep(0.1)

            fake_subscribe.assert_not_called()

    def test_start_bad_topics_and_pattern(self):
        """ Set no topics in the event_step. XOSEventEngine.start() will launch a thread, but the thread will fail
            with an exception before calling subscribe.
        """

        self.event_engine.load_event_step_modules(self.event_steps_dir)

        with patch.object(
            XOSKafkaThread, "create_kafka_consumer"
        ) as create_kafka_consumer, patch.object(
            FakeKafkaConsumer, "subscribe"
        ) as fake_subscribe, patch.object(
            self.event_engine.event_steps[0], "pattern", new_callable=PropertyMock
        ) as pattern:
            pattern.return_value = "foo"
            create_kafka_consumer.return_value = FakeKafkaConsumer()
            self.event_engine.start()

            # the thread does get launched, but it will fail with an exception
            self.assertEqual(len(self.event_engine.threads), 1)

            time.sleep(0.1)

            fake_subscribe.assert_not_called()

    def test_start_config_no_eventbus_kind(self):
        """ Set a blank event_bus.kind in Config. XOSEventEngine.start() should print an error message and
            not create any threads.
        """

        self.event_engine.load_event_step_modules(self.event_steps_dir)

        config_get_orig = Config.get
        with patch.object(
            XOSKafkaThread, "create_kafka_consumer"
        ) as create_kafka_consumer, patch.object(
            log, "error"
        ) as log_error, patch.object(
            Config,
            "get",
            new=functools.partial(
                config_get_mock, config_get_orig, {"event_bus.kind": None}
            ),
        ):

            create_kafka_consumer.return_value = FakeKafkaConsumer()
            self.event_engine.start()

            self.assertEqual(len(self.event_engine.threads), 0)

            log_error.assert_called_with(
                "Eventbus kind is not configured in synchronizer config file."
            )

    def test_start_config_bad_eventbus_kind(self):
        """ Set an unknown event_bus.kind in Config. XOSEventEngine.start() should print an error message and
            not create any threads.
        """

        self.event_engine.load_event_step_modules(self.event_steps_dir)

        config_get_orig = Config.get
        with patch.object(
            XOSKafkaThread, "create_kafka_consumer"
        ) as create_kafka_consumer, patch.object(
            log, "error"
        ) as log_error, patch.object(
            Config,
            "get",
            new=functools.partial(
                config_get_mock, config_get_orig, {"event_bus.kind": "not_kafka"}
            ),
        ):
            create_kafka_consumer.return_value = FakeKafkaConsumer()
            self.event_engine.start()

            self.assertEqual(len(self.event_engine.threads), 0)

            log_error.assert_called_with(
                "Eventbus kind is set to a technology we do not implement.",
                eventbus_kind="not_kafka",
            )


if __name__ == "__main__":
    unittest.main()
