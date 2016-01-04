import unittest
import json

from redis import Redis
from pyrq.queues import Queue
from nameko_pyrq import client
from tests import ConfigContainer


QUEUE_NAME = 'test-queue'


class TestPyrqClient(unittest.TestCase):
    def setUp(self):
        self._pyrq_client = client.PyRqClient(QUEUE_NAME)
        self._pyrq_client.container = container = ConfigContainer(client.CONFIG_KEY)
        self._pyrq_client._setup()

        configuration = container.config[client.CONFIG_KEY]
        self._redis_client = Redis(host=configuration['host'], port=configuration['port'], db=configuration['db'],
                                   password=configuration['password'], decode_responses=True)
        self._queue = Queue(QUEUE_NAME, self._redis_client)

    def tearDown(self):
        self._redis_client.delete(QUEUE_NAME)

    def test_dispatch(self):
        self._pyrq_client.dispatch('test_method', arg1='aaa', arg2=11)
        expected = {
            'method': 'test_method',
            'params': {
                'arg1': 'aaa',
                'arg2': 11
            }
        }
        actual = self._queue.get_items(1)[0]
        self.assertEquals(expected, json.loads(actual))
        self._queue.ack_item(actual)

    def test_is_empty(self):
        self.assertTrue(self._pyrq_client.is_empty())
        self._pyrq_client.dispatch('whatever')
        self.assertFalse(self._pyrq_client.is_empty())


if __name__ == '__main__':
    unittest.main()
