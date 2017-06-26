import unittest
import json

from redis import Redis
from pyrq.queues import Queue
from nameko_pyrq import client
from tests import ConfigContainer


QUEUE_NAME = 'test-queue'


class TestPyrqClient(unittest.TestCase):
    def setUp(self):
        self._pyrq_client = client.PyRqClient()
        self._pyrq_client.container = ConfigContainer(client.CONFIG_KEY)

        configuration = self._pyrq_client.container.config[client.CONFIG_KEY]
        self._pyrq_client._redis_client = Redis(host=configuration['host'], port=configuration['port'],
                                                db=configuration['db'], password=configuration['password'],
                                                decode_responses=True)

        self._queue = Queue(QUEUE_NAME, self._pyrq_client._redis_client)

    def tearDown(self):
        self._pyrq_client._redis_client.delete(QUEUE_NAME)

    def test_dispatch(self):
        self._pyrq_client.dispatch(QUEUE_NAME, 'test_method', arg1='aaa', arg2=11)
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
        self.assertTrue(self._pyrq_client.is_empty(QUEUE_NAME))
        self._pyrq_client.dispatch(QUEUE_NAME, 'whatever')
        self.assertFalse(self._pyrq_client.is_empty(QUEUE_NAME))


if __name__ == '__main__':
    unittest.main()
