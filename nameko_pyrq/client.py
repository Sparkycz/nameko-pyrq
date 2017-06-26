import json
import logging

from nameko.extensions import DependencyProvider
from pyrq.queues import Queue
from redis import Redis

FORMAT = '%(asctime) %(message)s'
logging.basicConfig(format=FORMAT)
_log = logging.getLogger(__name__)

CONFIG_KEY = 'PY-RQ'


class PyRqClient(DependencyProvider):
    def __init__(self):
        self._redis_client = None

    def get_dependency(self, worker_ctx):
        configuration = self.container.config[CONFIG_KEY]
        self._redis_client = Redis(host=configuration['host'], port=configuration['port'], db=configuration['db'],
                                   password=configuration['password'], decode_responses=True)

        return self

    def dispatch(self, queue_name: str, method: str, **params):
        """Dispatches request query to the queue

        Args:
            queue_name (str): Name of Redis queue
            method (str): nameko_pyrq method (action name)
            **params: Parameters for destination server
        """
        queue = Queue(queue_name, self._redis_client)

        queue.add_item(json.dumps({"method": method, "params": params}))

    def is_empty(self, queue_name: str):
        """Gets True if the queue is empty

        Args:
            queue_name (str): Name of Redis queue

        Returns:
            bool
        """
        queue = Queue(queue_name, self._redis_client)

        if not queue.get_count():
            return True
        else:
            return False
