import json
import logging

from functools import partial
from time import sleep

from nameko.extensions import Entrypoint, ProviderCollector, SharedExtension
from nameko.exceptions import MalformedRequest, MethodNotFound
from pyrq.queues import Queue
from redis import Redis

logging.basicConfig(format='%(asctime) %(message)s')
_log = logging.getLogger(__name__)

CONFIG_KEY = 'PY-RQ'


class RedisRpc(ProviderCollector, SharedExtension):
    def __init__(self):
        super().__init__()
        self._redis_client = None
        self._queue = None
        self._provider_map = {}
        self._gt = None
        self._waiting_sleep = None
        self._batch_size = None
        self._infinite = None

    def setup(self):
        if self._queue is None:
            configuration = self.container.config[CONFIG_KEY]
            self._redis_client = Redis(host=configuration['host'], port=configuration['port'], db=configuration['db'],
                                       password=configuration['password'], decode_responses=True)
            self._queue = Queue(configuration['queue_name'], self._redis_client)
            self._waiting_sleep = configuration.get('waiting_sleep', 0)
            self._batch_size = configuration.get('batch_size', 10)
            self._infinite = configuration.get('infinite', True)

    def start(self):
        for provider in self._providers:
            self._provider_map[provider.command] = provider

        if not self._gt:
            self._gt = self.container.spawn_managed_thread(self.run, protected=True)

    def stop(self):
        self._gt.kill()
        super().stop()

    def run(self):
        while True:
            items = self._queue.get_items(self._batch_size)
            while items:
                self.container.spawn_managed_thread(
                    partial(self._handle_request, items.pop()),
                    protected=True
                )
            else:
                sleep(self._waiting_sleep)

            if not self._infinite:
                break

    def _handle_request(self, item_from_redis):
        data = json.loads(item_from_redis)
        try:
            method = data['method']
        except KeyError:
            MalformedRequest("Definition of method is missing. Got {}".format(data))

        try:
            _log.info("working on command: `{}`".format(method))
            provider = self._provider_map[method]
        except KeyError:
            raise MethodNotFound(("unknown command `{}`".format(method)))

        self.container.spawn_worker(
            provider, (), data.get('params'), handle_result=partial(
                self._handle_result, item_from_redis, id)
        )

    def _handle_result(self, item_from_redis, id, worker_ctx, result, exc_info):
        if not exc_info:
            self._queue.ack_item(item_from_redis)
        return result, exc_info


class RedisRpcCommandHandler(Entrypoint):
    server = RedisRpc()

    def __init__(self, command):
        self.command = command

    def setup(self):
        self.server.register_provider(self)

    def stop(self):
        self.server.unregister_provider(self)
        super().stop()

pyrq_command = RedisRpcCommandHandler.decorator
