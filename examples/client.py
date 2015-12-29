from nameko_pyrq.client import PyRqClient


class ExampleService(object):
    name = "example_service"

    client = PyRqClient('queue_name')

    def hello(self):
        self.client.dispatch('method_name', arg1='value', arg2='value')
