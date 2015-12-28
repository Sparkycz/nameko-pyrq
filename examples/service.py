from nameko_pyrq.server import pyrq_command


class Service(object):
    name = 'service'

    @pyrq_command('hello')
    def hello(self, arg1):
        print(arg1)
