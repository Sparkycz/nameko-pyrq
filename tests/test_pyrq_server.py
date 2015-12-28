import unittest
import json

from redis import Redis
from pyrq.queues import Queue
from nameko_pyrq.server import pyrq_command, CONFIG_KEY
from nameko.containers import ServiceContainer

from tests import ConfigContainer


QUEUE_NAME = 'test_queue'


class Service(object):
    name = 'service'

    arg_missing = False

    @pyrq_command('hello')
    def hello(self, arg1):
        if not arg1:
            Service.arg_missing = True


class TestPyrqServer(unittest.TestCase):
    def setUp(self):
        configuration = ConfigContainer(CONFIG_KEY)
        self.service_container = ServiceContainer(Service, configuration.config)

        configuration = configuration.config[CONFIG_KEY]
        self._redis_client = Redis(host=configuration['host'], port=configuration['port'], db=configuration['db'],
                                   password=configuration['password'], decode_responses=True)
        self._queue = Queue(QUEUE_NAME, self._redis_client)

    def tearDown(self):
        self._redis_client.delete(QUEUE_NAME)

    def testService(self):
        self._queue.add_item(json.dumps({
            'method': 'hello', 'params': {
                'arg1': True
            }
        }))
        self.service_container.start()
        self.assertFalse(Service.arg_missing)

if __name__ == '__main__':
    unittest.main()
