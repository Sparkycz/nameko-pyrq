import os


class ConfigContainer(object):
    def __init__(self, main_key):
        self.config = {
            main_key: {
                'host': os.getenv('REDIS_HOST', 'localhost'),
                'port': int(os.getenv('REDIS_PORT', 6379)),
                'db': int(os.getenv('REDIS_DB', 0)),
                'password': os.getenv('REDIS_PASS', None),
                'queue_name': 'test_queue',
                'infinite': False
            }
        }
