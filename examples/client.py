from nameko_pyrq.client import PyRqClient


class ExampleService(object):
    name = "example_service"

    client = PyRqClient()

    def hello(self):
        self.client.dispatch('queue_name', 'method_name', arg1='value', arg2='value')
