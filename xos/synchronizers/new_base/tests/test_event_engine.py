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

import functools
import unittest
from mock import patch, PropertyMock, ANY
from kafka.errors import NoBrokersAvailable

import os, sys
import time

test_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
xos_dir = os.path.join(test_path, '..', '..', '..')

def config_get_mock(orig, overrides, key):
    if key in overrides:
        return overrides[key]
    else:
        return orig(key)

class FakeKafkaConsumer():
    def __init__(self, values=["sampleevent"]):
        self.values = values

    def subscribe(self, topics=None, pattern=None):
        pass

    def __iter__(self):
        for x in self.values:
            yield x
        # block forever
        time.sleep(1000)

class MockKafkaError:
    NoBrokersAvailable = Exception

class MockKafka:
    error = MockKafkaError

class TestEventEngine(unittest.TestCase):
    def setUp(self):
        global XOSKafkaThread, Config, event_engine_log

        self.sys_path_save = sys.path
        self.cwd_save = os.getcwd()
        sys.path.append(xos_dir)
        sys.path.append(os.path.join(xos_dir, 'synchronizers', 'new_base'))
        sys.path.append(os.path.join(xos_dir, 'synchronizers', 'new_base', 'tests', 'event_steps'))

        config =     os.path.join(test_path, "test_config.yaml")
        from xosconfig import Config
        Config.clear()
        Config.init(config, 'synchronizer-config-schema.yaml')

        from synchronizers.new_base.mock_modelaccessor_build import build_mock_modelaccessor
        build_mock_modelaccessor(xos_dir, services_dir=None, service_xprotos=[])

        os.chdir(os.path.join(test_path, '..'))  # config references tests/model-deps

        from event_engine import XOSKafkaThread, XOSEventEngine
        from event_engine import log as event_engine_log

        self.event_steps_dir = Config.get("event_steps_dir")
        self.event_engine = XOSEventEngine()

    def tearDown(self):
        sys.path = self.sys_path_save
        os.chdir(self.cwd_save)

    def test_load_event_step_modules(self):
        self.event_engine.load_event_step_modules(self.event_steps_dir)
        self.assertEqual(len(self.event_engine.event_steps), 1)

    def test_start(self):
        self.event_engine.load_event_step_modules(self.event_steps_dir)

        with patch.object(XOSKafkaThread, "create_kafka_consumer") as create_kafka_consumer, \
             patch.object(FakeKafkaConsumer, "subscribe") as fake_subscribe, \
             patch.object(self.event_engine.event_steps[0], "process_event") as process_event:
            create_kafka_consumer.return_value = FakeKafkaConsumer()
            self.event_engine.start()

            self.assertEqual(len(self.event_engine.threads), 1)

            # Since event_engine.start() launches threads, give them a hundred milliseconds to do something...
            time.sleep(0.1)

            # We should have subscribed to the fake consumer
            fake_subscribe.assert_called_with(topics=["sometopic"])

            # The fake consumer will have returned one event, and that event will have been passed to our step
            process_event.assert_called_with("sampleevent")

    def test_start_with_pattern(self):
        self.event_engine.load_event_step_modules(self.event_steps_dir)

        with patch.object(XOSKafkaThread, "create_kafka_consumer") as create_kafka_consumer, \
             patch.object(FakeKafkaConsumer, "subscribe") as fake_subscribe, \
             patch.object(self.event_engine.event_steps[0], "process_event") as process_event, \
             patch.object(self.event_engine.event_steps[0], "pattern", new_callable=PropertyMock) as pattern, \
             patch.object(self.event_engine.event_steps[0], "topics", new_callable=PropertyMock) as topics:

            pattern.return_value = "somepattern"
            topics.return_value = []

            create_kafka_consumer.return_value = FakeKafkaConsumer()
            self.event_engine.start()

            self.assertEqual(len(self.event_engine.threads), 1)

            # Since event_engine.start() launches threads, give them a hundred milliseconds to do something...
            time.sleep(0.1)

            # We should have subscribed to the fake consumer
            fake_subscribe.assert_called_with(pattern="somepattern")

            # The fake consumer will have returned one event, and that event will have been passed to our step
            process_event.assert_called_with("sampleevent")

    def _test_start_no_bus(self):
        self.event_engine.load_event_step_modules(self.event_steps_dir)
        with patch.object(XOSKafkaThread, "create_kafka_consumer") as create_kafka_consumer, \
                patch.object(event_engine_log, "warning") as log_warning:

                create_kafka_consumer.side_effect = NoBrokersAvailable()
                self.event_engine.start()

        log_warning.assert_called()

    def test_start_bad_tech(self):
        """ Set an unknown Technology in the event_step. XOSEventEngine.start() should print an error message and
            not create any threads.
        """

        self.event_engine.load_event_step_modules(self.event_steps_dir)

        with patch.object(XOSKafkaThread, "create_kafka_consumer") as create_kafka_consumer, \
                patch.object(event_engine_log, "error") as log_error, \
                patch.object(self.event_engine.event_steps[0], "technology") as technology:
            technology.return_value = "not_kafka"
            create_kafka_consumer.return_value = FakeKafkaConsumer()
            self.event_engine.start()

            self.assertEqual(len(self.event_engine.threads), 0)

            log_error.assert_called_with('Unknown technology. Skipping step', step="TestEventStep",
                                         technology=ANY)

    def test_start_bad_no_topics(self):
        """ Set no topics in the event_step. XOSEventEngine.start() will launch a thread, but the thread will fail
            with an exception before calling subscribe.
        """

        self.event_engine.load_event_step_modules(self.event_steps_dir)

        with patch.object(XOSKafkaThread, "create_kafka_consumer") as create_kafka_consumer, \
             patch.object(FakeKafkaConsumer, "subscribe") as fake_subscribe, \
             patch.object(self.event_engine.event_steps[0], "topics", new_callable=PropertyMock) as topics:
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

        with patch.object(XOSKafkaThread, "create_kafka_consumer") as create_kafka_consumer, \
             patch.object(FakeKafkaConsumer, "subscribe") as fake_subscribe, \
             patch.object(self.event_engine.event_steps[0], "pattern", new_callable=PropertyMock) as pattern:
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
        with patch.object(XOSKafkaThread, "create_kafka_consumer") as create_kafka_consumer, \
                patch.object(event_engine_log, "error") as log_error, \
                patch.object(Config, "get", new=functools.partial(config_get_mock, config_get_orig, {"event_bus.kind": None})):

            create_kafka_consumer.return_value = FakeKafkaConsumer()
            self.event_engine.start()

            self.assertEqual(len(self.event_engine.threads), 0)

            log_error.assert_called_with('Eventbus kind is not configured in synchronizer config file.')

    def test_start_config_bad_eventbus_kind(self):
        """ Set an unknown event_bus.kind in Config. XOSEventEngine.start() should print an error message and
            not create any threads.
        """

        self.event_engine.load_event_step_modules(self.event_steps_dir)

        config_get_orig = Config.get
        with patch.object(XOSKafkaThread, "create_kafka_consumer") as create_kafka_consumer, \
                patch.object(event_engine_log, "error") as log_error, \
                patch.object(Config, "get",
                             new=functools.partial(config_get_mock, config_get_orig, {"event_bus.kind": "not_kafka"})):
            create_kafka_consumer.return_value = FakeKafkaConsumer()
            self.event_engine.start()

            self.assertEqual(len(self.event_engine.threads), 0)

            log_error.assert_called_with('Eventbus kind is set to a technology we do not implement.',
                                         eventbus_kind='not_kafka')

if __name__ == '__main__':
    unittest.main()
