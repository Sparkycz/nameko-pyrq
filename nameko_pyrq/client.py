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
    def __init__(self, queue_name):
        self._queue = None
        self._queue_name = queue_name

    def _setup(self):
        configuration = self.container.config[CONFIG_KEY]
        _redis_client = Redis(host=configuration['host'], port=configuration['port'], db=configuration['db'],
                              password=configuration['password'], decode_responses=True)
        self._queue = Queue(self._queue_name, _redis_client)

    def get_dependency(self, worker_ctx):
        self._setup()
        return self

    def dispatch(self, method: str, **params):
        request = {"method": method, "params": params}
        self._queue.add_item(json.dumps(request))

    def is_empty(self):
        if not self._queue.get_count():
            return True
        else:
            return False
